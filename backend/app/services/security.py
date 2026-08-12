import hashlib, secrets
from datetime import datetime, timedelta, timezone
import jwt
from pwdlib import PasswordHash
from app.core.config import settings
password_hash=PasswordHash.recommended()
def hash_password(p:str)->str: return password_hash.hash(p)
def verify_password(p:str,h:str)->bool: return password_hash.verify(p,h)
def token(subject:str,kind:str,expires:timedelta)->str: return jwt.encode({"sub":subject,"kind":kind,"exp":datetime.now(timezone.utc)+expires},settings().jwt_secret,algorithm="HS256")
def decode_token(raw:str,kind:str)->str:
 data=jwt.decode(raw,settings().jwt_secret,algorithms=["HS256"])
 if data.get("kind")!=kind: raise jwt.InvalidTokenError("wrong token type")
 return data["sub"]
def new_api_key()->tuple[str,str,str]:
 raw="vv_"+secrets.token_urlsafe(32); return raw,raw[:11],hashlib.sha256(raw.encode()).hexdigest()
