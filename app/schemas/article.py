from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from uuid import UUID


class ArticleCreate(BaseModel):
    article_id: str
    article: str
    approval_group_id: UUID


class ArticleUpdate(BaseModel):
    article_id: Optional[str] = None
    article: Optional[str] = None
    approval_group_id: Optional[UUID] = None


class ArticleResponse(BaseModel):
    id: UUID
    article_id: str
    article: str
    approval_group_id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True