from app.providers.vector_store import LocalVectorStore
from app.services.ingestion import chunk_text
def test_chunking_preserves_text():
 chunks=chunk_text("alpha "*500,size=100,overlap=20)
 assert len(chunks)>1 and chunks[0].startswith("alpha")
def test_local_vector_metadata_filter():
 store=LocalVectorStore();store.upsert([("a",[1,0],{"workspace_id":"one"}),("b",[0,1],{"workspace_id":"two"})],"one")
 assert [m.id for m in store.query([1,0],5,{"workspace_id":"one"},"one")]==["a"]
