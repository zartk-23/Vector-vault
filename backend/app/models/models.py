import enum, uuid
from datetime import datetime
from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, Integer, String, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column
from app.db.session import Base

def uid() -> str: return str(uuid.uuid4())
class Role(str, enum.Enum): OWNER="owner"; MEMBER="member"
class DocumentStatus(str, enum.Enum): PENDING="pending"; PROCESSING="processing"; COMPLETED="completed"; FAILED="failed"
class User(Base):
    __tablename__="users"; id: Mapped[str]=mapped_column(String(36),primary_key=True,default=uid); email: Mapped[str]=mapped_column(String(320),unique=True,index=True); password_hash: Mapped[str]=mapped_column(String(255)); created_at: Mapped[datetime]=mapped_column(DateTime,server_default=func.now())
class Workspace(Base):
    __tablename__="workspaces"; id: Mapped[str]=mapped_column(String(36),primary_key=True,default=uid); name: Mapped[str]=mapped_column(String(120)); created_at: Mapped[datetime]=mapped_column(DateTime,server_default=func.now())
class WorkspaceMember(Base):
    __tablename__="workspace_members"; __table_args__=(UniqueConstraint("workspace_id","user_id"),); id: Mapped[str]=mapped_column(String(36),primary_key=True,default=uid); workspace_id: Mapped[str]=mapped_column(ForeignKey("workspaces.id",ondelete="CASCADE"),index=True); user_id: Mapped[str]=mapped_column(ForeignKey("users.id",ondelete="CASCADE"),index=True); role: Mapped[Role]=mapped_column(Enum(Role))
class Collection(Base):
    __tablename__="collections"; id: Mapped[str]=mapped_column(String(36),primary_key=True,default=uid); workspace_id: Mapped[str]=mapped_column(ForeignKey("workspaces.id",ondelete="CASCADE"),index=True); name: Mapped[str]=mapped_column(String(120)); created_at: Mapped[datetime]=mapped_column(DateTime,server_default=func.now())
class Document(Base):
    __tablename__="documents"; id: Mapped[str]=mapped_column(String(36),primary_key=True,default=uid); workspace_id: Mapped[str]=mapped_column(ForeignKey("workspaces.id",ondelete="CASCADE"),index=True); collection_id: Mapped[str]=mapped_column(ForeignKey("collections.id",ondelete="CASCADE"),index=True); filename: Mapped[str]=mapped_column(String(255)); content_type: Mapped[str]=mapped_column(String(100)); size: Mapped[int]=mapped_column(Integer); checksum: Mapped[str]=mapped_column(String(64),index=True); status: Mapped[DocumentStatus]=mapped_column(Enum(DocumentStatus),default=DocumentStatus.PENDING,index=True); chunk_count: Mapped[int]=mapped_column(Integer,default=0); error: Mapped[str|None]=mapped_column(Text,nullable=True); created_at: Mapped[datetime]=mapped_column(DateTime,server_default=func.now())
class DocumentChunk(Base):
    __tablename__="document_chunks"; id: Mapped[str]=mapped_column(String(36),primary_key=True,default=uid); document_id: Mapped[str]=mapped_column(ForeignKey("documents.id",ondelete="CASCADE"),index=True); ordinal: Mapped[int]=mapped_column(Integer); text: Mapped[str]=mapped_column(Text); vector_id: Mapped[str]=mapped_column(String(160),unique=True); embedding_model: Mapped[str]=mapped_column(String(100));
class ApiKey(Base):
    __tablename__="api_keys"; id: Mapped[str]=mapped_column(String(36),primary_key=True,default=uid); workspace_id: Mapped[str]=mapped_column(ForeignKey("workspaces.id",ondelete="CASCADE"),index=True); name: Mapped[str]=mapped_column(String(120)); prefix: Mapped[str]=mapped_column(String(16)); key_hash: Mapped[str]=mapped_column(String(128),unique=True,index=True); revoked: Mapped[bool]=mapped_column(Boolean,default=False); last_used_at: Mapped[datetime|None]=mapped_column(DateTime,nullable=True); created_at: Mapped[datetime]=mapped_column(DateTime,server_default=func.now())
