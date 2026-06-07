from datetime import datetime
from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field

class CaseStatus(str, Enum):
    NEW = "new"
    CLASSIFIED = "classified"
    REVIEW_PENDING = "review_pending"
    APPROVED = "approved"
    ROUTED = "routed"
    CLOSED = "closed"
    REJECTED = "rejected"

class CasePriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"

class CaseNote(BaseModel):
    note_id: str = Field(...)
    author: str = Field(...)
    message: str = Field(...)
    created_at: datetime = Field(default_factory=datetime.utcnow)

class AuditEvent(BaseModel):
    event_id: str = Field(...)
    action: str = Field(...)
    actor: str = Field(...)
    details: Optional[dict] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)

class CaseDocument(BaseModel):
    document_id: str = Field(...)
    filename: str = Field(...)
    document_type: str = Field(default="general")
    summary: Optional[str] = None

class CaseRecord(BaseModel):
    case_id: str = Field(...)
    title: str = Field(...)
    description: Optional[str] = None
    document: CaseDocument
    status: CaseStatus = Field(default=CaseStatus.NEW)
    priority: CasePriority = Field(default=CasePriority.MEDIUM)
    owner: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    notes: List[CaseNote] = Field(default_factory=list)
    audit_trail: List[AuditEvent] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    due_at: Optional[datetime] = None
