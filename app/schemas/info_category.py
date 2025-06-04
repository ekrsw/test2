from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from uuid import UUID


class InfoCategoryCreate(BaseModel):
    name: str
    description: Optional[str] = None


class InfoCategoryUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None


class InfoCategoryResponse(BaseModel):
    id: UUID
    name: str
    description: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True