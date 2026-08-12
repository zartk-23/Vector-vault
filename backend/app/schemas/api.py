from pydantic import BaseModel, Field
class RegisterIn(BaseModel): email: str = Field(max_length=320); password: str = Field(min_length=12,max_length=128)
class LoginIn(RegisterIn): pass
class TokenOut(BaseModel): access_token:str; refresh_token:str; token_type:str="bearer"
class WorkspaceIn(BaseModel): name:str=Field(min_length=1,max_length=120)
class CollectionIn(BaseModel): workspace_id:str; name:str=Field(min_length=1,max_length=120)
class SearchIn(BaseModel): workspace_id:str; query:str=Field(min_length=1,max_length=2000); collection_id:str|None=None; top_k:int=Field(default=5,ge=1,le=20); filters:dict[str,str]=Field(default_factory=dict)
class AskOut(BaseModel): answer:str; sources:list[dict]
class ApiKeyIn(BaseModel): workspace_id:str; name:str=Field(min_length=1,max_length=120)
