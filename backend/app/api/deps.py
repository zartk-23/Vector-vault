from fastapi import Depends, HTTPException, Header
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.models import User, WorkspaceMember, Role
from app.services.security import decode_token
def current_user(authorization:str|None=Header(default=None),db:Session=Depends(get_db))->User:
 if not authorization or not authorization.startswith("Bearer "): raise HTTPException(401,"Missing bearer token")
 try: uid=decode_token(authorization[7:],"access")
 except Exception: raise HTTPException(401,"Invalid or expired access token")
 user=db.get(User,uid)
 if not user: raise HTTPException(401,"Unknown user")
 return user
def require_member(workspace_id:str,user:User,db:Session,owner:bool=False)->WorkspaceMember:
 m=db.query(WorkspaceMember).filter_by(workspace_id=workspace_id,user_id=user.id).first()
 if not m or (owner and m.role != Role.OWNER): raise HTTPException(403,"Workspace access denied")
 return m
