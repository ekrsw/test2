from pydantic import BaseModel
from typing import Optional
from uuid import UUID


class GroupCreate(BaseModel):
    name: str
    description: Optional[str] = None


class GroupUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None


class GroupResponse(BaseModel):
    id: UUID
    name: str
    description: Optional[str]

    class Config:
        from_attributes = True