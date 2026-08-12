import logging, time, uuid
from datetime import timedelta
from fastapi import Depends, FastAPI, File, Header, HTTPException, Request, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from app.core.config import settings
from app.db.session import Base, engine, get_db
from app.models.models import ApiKey, Collection, Document, DocumentChunk, DocumentStatus, Role, User, Workspace, WorkspaceMember
from app.providers.embeddings import LocalEmbeddingProvider, OpenAIEmbeddingProvider
from app.providers.vector_store import LocalVectorStore, PineconeVectorStore
from app.schemas.api import *
from app.api.deps import current_user, require_member
from app.services.ingestion import checksum, chunk_text, extract_text
from app.services.rag import grounded_answer
from app.services.security import decode_token, hash_password, new_api_key, token, verify_password

log=logging.getLogger("vectorvault"); app=FastAPI(title="VectorVault",version="0.1.0")
cfg=settings()
vectors = PineconeVectorStore(cfg.pinecone_api_key, cfg.pinecone_index) if cfg.vector_store == "pinecone" and cfg.pinecone_api_key and cfg.pinecone_index else LocalVectorStore()
embeddings = OpenAIEmbeddingProvider(cfg.openai_api_key, cfg.openai_embedding_model) if cfg.embedding_provider == "openai" and cfg.openai_api_key else LocalEmbeddingProvider()
app.add_middleware(CORSMiddleware,allow_origins=settings().cors_origins.split(","),allow_credentials=True,allow_methods=["*"],allow_headers=["*"])
@app.middleware("http")
async def request_context(request:Request,call_next):
 request.state.request_id=str(uuid.uuid4()); start=time.perf_counter()
 try: response=await call_next(request)
 except HTTPException as e: response=JSONResponse(status_code=e.status_code,content={"error":{"code":"REQUEST_FAILED","message":str(e.detail),"request_id":request.state.request_id}})
 except Exception:
  log.exception("request_failed",extra={"request_id":request.state.request_id}); response=JSONResponse(status_code=500,content={"error":{"code":"INTERNAL_ERROR","message":"An unexpected error occurred.","request_id":request.state.request_id}})
 response.headers["X-Request-ID"]=request.state.request_id; log.info("request",extra={"route":request.url.path,"status":response.status_code,"ms":round((time.perf_counter()-start)*1000)}); return response
@app.on_event("startup")
def setup(): Base.metadata.create_all(engine)
@app.get("/api/v1/health")
def health(): return {"status":"ok"}
@app.get("/api/v1/health/ready")
def ready(db:Session=Depends(get_db)): db.execute(__import__('sqlalchemy').text("SELECT 1")); return {"status":"ready","vector_store":settings().vector_store}
@app.post("/api/v1/auth/register",response_model=TokenOut,status_code=201)
def register(body:RegisterIn,db:Session=Depends(get_db)):
 if db.query(User).filter_by(email=body.email.lower()).first(): raise HTTPException(409,"Email already registered")
 u=User(email=body.email.lower(),password_hash=hash_password(body.password)); db.add(u);db.commit(); return TokenOut(access_token=token(u.id,"access",timedelta(minutes=settings().access_token_minutes)),refresh_token=token(u.id,"refresh",timedelta(days=settings().refresh_token_days)))
@app.post("/api/v1/auth/login",response_model=TokenOut)
def login(body:LoginIn,db:Session=Depends(get_db)):
 u=db.query(User).filter_by(email=body.email.lower()).first()
 if not u or not verify_password(body.password,u.password_hash): raise HTTPException(401,"Invalid credentials")
 return TokenOut(access_token=token(u.id,"access",timedelta(minutes=settings().access_token_minutes)),refresh_token=token(u.id,"refresh",timedelta(days=settings().refresh_token_days)))
@app.post("/api/v1/auth/refresh",response_model=TokenOut)
def refresh(refresh_token:str,db:Session=Depends(get_db)):
 try: uid=decode_token(refresh_token,"refresh")
 except Exception: raise HTTPException(401,"Invalid refresh token")
 if not db.get(User,uid):raise HTTPException(401,"Invalid refresh token")
 return TokenOut(access_token=token(uid,"access",timedelta(minutes=settings().access_token_minutes)),refresh_token=token(uid,"refresh",timedelta(days=settings().refresh_token_days)))
@app.get("/api/v1/users/me")
def me(u:User=Depends(current_user)):return {"id":u.id,"email":u.email}
@app.post("/api/v1/workspaces",status_code=201)
def create_workspace(body:WorkspaceIn,u:User=Depends(current_user),db:Session=Depends(get_db)):
 w=Workspace(name=body.name);db.add(w);db.flush();db.add(WorkspaceMember(workspace_id=w.id,user_id=u.id,role=Role.OWNER));db.commit();return {"id":w.id,"name":w.name,"role":"owner"}
@app.get("/api/v1/workspaces")
def workspaces(u:User=Depends(current_user),db:Session=Depends(get_db)): return [{"id":m.workspace_id,"name":db.get(Workspace,m.workspace_id).name,"role":m.role.value} for m in db.query(WorkspaceMember).filter_by(user_id=u.id)]
@app.post("/api/v1/collections",status_code=201)
def create_collection(body:CollectionIn,u:User=Depends(current_user),db:Session=Depends(get_db)):
 require_member(body.workspace_id,u,db); c=Collection(workspace_id=body.workspace_id,name=body.name);db.add(c);db.commit();return {"id":c.id,"name":c.name,"workspace_id":c.workspace_id}
@app.get("/api/v1/collections")
def collections(workspace_id:str,u:User=Depends(current_user),db:Session=Depends(get_db)):
 require_member(workspace_id,u,db);return [{"id":c.id,"name":c.name} for c in db.query(Collection).filter_by(workspace_id=workspace_id)]
@app.delete("/api/v1/collections/{collection_id}",status_code=204)
def delete_collection(collection_id:str,u:User=Depends(current_user),db:Session=Depends(get_db)):
 c=db.get(Collection,collection_id)
 if not c:raise HTTPException(404,"Collection not found")
 require_member(c.workspace_id,u,db,owner=True);db.delete(c);db.commit()
@app.post("/api/v1/documents/upload",status_code=201)
async def upload(workspace_id:str,collection_id:str,file:UploadFile=File(...),u:User=Depends(current_user),db:Session=Depends(get_db)):
 require_member(workspace_id,u,db);c=db.get(Collection,collection_id)
 if not c or c.workspace_id!=workspace_id: raise HTTPException(404,"Collection not found")
 allowed={"application/pdf","text/plain","text/markdown"}; raw=await file.read()
 if len(raw)>settings().max_upload_bytes:raise HTTPException(413,"File exceeds upload limit")
 if file.content_type not in allowed:raise HTTPException(415,"Only PDF, TXT, and Markdown are supported")
 digest=checksum(raw)
 if db.query(Document).filter_by(workspace_id=workspace_id,checksum=digest).first():raise HTTPException(409,"Duplicate document")
 d=Document(workspace_id=workspace_id,collection_id=collection_id,filename=(file.filename or "upload")[-255:],content_type=file.content_type,size=len(raw),checksum=digest,status=DocumentStatus.PROCESSING);db.add(d);db.flush()
 try:
  pieces=chunk_text(extract_text(raw,file.content_type)); vectors_list=embeddings.embed(pieces)
  rows=[]
  for n,(piece,vec) in enumerate(zip(pieces,vectors_list)):
   vid=f"{workspace_id}:{d.id}:{n}"; rows.append(DocumentChunk(document_id=d.id,ordinal=n,text=piece,vector_id=vid,embedding_model="local-hash"));vectors.upsert([(vid,vec,{"workspace_id":workspace_id,"collection_id":collection_id,"document_id":d.id,"chunk_id":str(n),"filename":d.filename})],workspace_id)
  db.add_all(rows);d.chunk_count=len(rows);d.status=DocumentStatus.COMPLETED
 except Exception:
  d.status=DocumentStatus.FAILED;d.error="Ingestion failed";db.commit();raise HTTPException(422,"Unable to ingest document")
 db.commit();return {"id":d.id,"status":d.status.value,"chunk_count":d.chunk_count}
@app.get("/api/v1/documents")
def documents(workspace_id:str,u:User=Depends(current_user),db:Session=Depends(get_db)):
 require_member(workspace_id,u,db);return [{"id":d.id,"filename":d.filename,"status":d.status.value,"chunk_count":d.chunk_count,"size":d.size} for d in db.query(Document).filter_by(workspace_id=workspace_id)]
@app.post("/api/v1/search")
def search(body:SearchIn,u:User=Depends(current_user),db:Session=Depends(get_db)):
 require_member(body.workspace_id,u,db); metadata={"workspace_id":body.workspace_id,**({"collection_id":body.collection_id} if body.collection_id else {})};metadata.update(body.filters);matches=vectors.query(embeddings.embed([body.query])[0],body.top_k,metadata,body.workspace_id); ids=[m.id for m in matches];chunks={c.vector_id:c for c in db.query(DocumentChunk).filter(DocumentChunk.vector_id.in_(ids))};return {"results":[{"chunk_id":m.metadata["chunk_id"],"document_id":m.metadata["document_id"],"score":m.score,"text":chunks[m.id].text,"metadata":m.metadata} for m in matches if m.id in chunks]}
@app.post("/api/v1/query",response_model=AskOut)
def query(body:SearchIn,u:User=Depends(current_user),db:Session=Depends(get_db)):
 r=search(body,u,db);return AskOut(answer=grounded_answer(body.query,r["results"]),sources=[{k:x[k] for k in ("chunk_id","document_id","score")} for x in r["results"]])
@app.post("/api/v1/api-keys",status_code=201)
def create_key(body:ApiKeyIn,u:User=Depends(current_user),db:Session=Depends(get_db)):
 require_member(body.workspace_id,u,db,owner=True);raw,prefix,digest=new_api_key();k=ApiKey(workspace_id=body.workspace_id,name=body.name,prefix=prefix,key_hash=digest);db.add(k);db.commit();return {"id":k.id,"key":raw,"warning":"Store this key now; it will not be shown again."}
@app.get("/api/v1/api-keys")
def list_keys(workspace_id:str,u:User=Depends(current_user),db:Session=Depends(get_db)):
 require_member(workspace_id,u,db,owner=True);return [{"id":k.id,"name":k.name,"prefix":k.prefix,"created_at":k.created_at,"last_used_at":k.last_used_at,"revoked":k.revoked} for k in db.query(ApiKey).filter_by(workspace_id=workspace_id)]
@app.delete("/api/v1/api-keys/{key_id}",status_code=204)
def revoke_key(key_id:str,u:User=Depends(current_user),db:Session=Depends(get_db)):
 k=db.get(ApiKey,key_id)
 if not k:raise HTTPException(404,"API key not found")
 require_member(k.workspace_id,u,db,owner=True);k.revoked=True;db.commit()
