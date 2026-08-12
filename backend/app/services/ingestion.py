import hashlib, re
from pypdf import PdfReader
from io import BytesIO
def extract_text(raw:bytes, content_type:str)->str:
 if content_type=="application/pdf": return "\n".join(p.extract_text() or "" for p in PdfReader(BytesIO(raw)).pages)
 return raw.decode("utf-8",errors="replace")
def chunk_text(text:str,size:int=900,overlap:int=150)->list[str]:
 text=re.sub(r"\s+"," ",text).strip()
 if not text:return []
 chunks=[]; start=0
 while start<len(text):
  end=min(len(text),start+size); cut=text.rfind(" ",start,end)
  if cut<=start: cut=end
  chunks.append(text[start:cut].strip())
  if cut==len(text):break
  start=cut-overlap
 return chunks
def checksum(raw:bytes)->str:return hashlib.sha256(raw).hexdigest()
