from pydantic import BaseModel
from typing import Optional
from datetime import datetime, date
from uuid import UUID
from enum import Enum


class ProposalType(str, Enum):
    MODIFY = "修正"
    DELETE = "削除"


class ProposalStatus(str, Enum):
    PENDING = "申請中"
    APPROVED = "承認済み"
    REJECTED = "却下"


class ProposalTarget(str, Enum):
    INTERNAL = "社内向け"
    EXTERNAL = "社外向け"
    NOT_APPLICABLE = "該当なし"


class ProposalCreate(BaseModel):
    article_id: str
    article: str
    type: ProposalType
    title: str
    info_category_id: Optional[UUID] = None
    keywords: Optional[str] = None
    importance: Optional[bool] = None
    published_start: Optional[date] = None
    published_end: Optional[date] = None
    target: Optional[ProposalTarget] = None
    question: Optional[str] = None
    answer: Optional[str] = None
    add_comments: Optional[str] = None
    reason: str


class ProposalUpdate(BaseModel):
    title: Optional[str] = None
    info_category_id: Optional[UUID] = None
    keywords: Optional[str] = None
    importance: Optional[bool] = None
    published_start: Optional[date] = None
    published_end: Optional[date] = None
    target: Optional[ProposalTarget] = None
    question: Optional[str] = None
    answer: Optional[str] = None
    add_comments: Optional[str] = None
    reason: Optional[str] = None


class ProposalApprovalRequest(BaseModel):
    status: ProposalStatus
    rejection_reason: Optional[str] = None


class ProposalResponse(BaseModel):
    id: UUID
    user_id: UUID
    article_id: str
    article: str
    type: ProposalType
    status: ProposalStatus
    title: str
    info_category_id: Optional[UUID]
    keywords: Optional[str]
    importance: Optional[bool]
    published_start: Optional[date]
    published_end: Optional[date]
    target: Optional[ProposalTarget]
    question: Optional[str]
    answer: Optional[str]
    add_comments: Optional[str]
    reason: str
    approval_group_id: UUID
    approved_by: Optional[UUID]
    approved_at: Optional[datetime]
    rejection_reason: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True