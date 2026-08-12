from abc import ABC, abstractmethod
import hashlib
class EmbeddingProvider(ABC):
 @abstractmethod
 def embed(self, texts:list[str])->list[list[float]]: ...
class LocalEmbeddingProvider(EmbeddingProvider):
 def embed(self,texts):
  out=[]
  for text in texts:
   vec=[0.0]*64
   for token in text.lower().split(): vec[int(hashlib.sha256(token.encode()).hexdigest()[:8],16)%64]+=1
   out.append(vec)
  return out
class OpenAIEmbeddingProvider(EmbeddingProvider):
 def __init__(self,api_key:str,model:str):
  from openai import OpenAI
  self.client=OpenAI(api_key=api_key);self.model=model
 def embed(self,texts):
  response=self.client.embeddings.create(model=self.model,input=texts)
  return [row.embedding for row in response.data]
