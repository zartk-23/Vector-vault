from abc import ABC, abstractmethod
from dataclasses import dataclass
import math
@dataclass
class VectorMatch: id:str; score:float; metadata:dict
class VectorStore(ABC):
 @abstractmethod
 def upsert(self, vectors:list[tuple[str,list[float],dict]], namespace:str)->None: ...
 @abstractmethod
 def query(self, vector:list[float], top_k:int, metadata:dict, namespace:str)->list[VectorMatch]: ...
 @abstractmethod
 def delete(self, ids:list[str], namespace:str)->None: ...
class LocalVectorStore(VectorStore):
 def __init__(self): self.data:dict[str,dict[str,tuple[list[float],dict]]]={}
 def upsert(self,vectors,namespace): self.data.setdefault(namespace,{}).update({i:(v,m) for i,v,m in vectors})
 def query(self,vector,top_k,metadata,namespace):
  def score(x): return sum(a*b for a,b in zip(vector,x))/(math.sqrt(sum(a*a for a in vector))*math.sqrt(sum(b*b for b in x)) or 1)
  rows=[VectorMatch(i,score(v),m) for i,(v,m) in self.data.get(namespace,{}).items() if all(m.get(k)==val for k,val in metadata.items())]
  return sorted(rows,key=lambda x:x.score,reverse=True)[:top_k]
 def delete(self,ids,namespace):
  for i in ids: self.data.get(namespace,{}).pop(i,None)
class PineconeVectorStore(VectorStore):
 """Production adapter. Pinecone remains isolated behind VectorStore."""
 def __init__(self, api_key:str, index_name:str):
  from pinecone import Pinecone
  self.index=Pinecone(api_key=api_key).Index(index_name)
 def upsert(self,vectors,namespace): self.index.upsert(vectors=[{"id":i,"values":v,"metadata":m} for i,v,m in vectors],namespace=namespace)
 def query(self,vector,top_k,metadata,namespace):
  result=self.index.query(vector=vector,top_k=top_k,filter=metadata,namespace=namespace,include_metadata=True)
  return [VectorMatch(x.id,x.score,dict(x.metadata or {})) for x in result.matches]
 def delete(self,ids,namespace): self.index.delete(ids=ids,namespace=namespace)
