from pydantic import BaseModel
from typing import Optional
from datetime import datetime, date
from uuid import UUID
from .proposal import ProposalTarget


class ProposalBeforeResponse(BaseModel):
    id: UUID
    proposal_id: UUID
    title_before: Optional[str]
    info_category_id_before: Optional[UUID]
    keywords_before: Optional[str]
    importance_before: Optional[bool]
    published_start_before: Optional[date]
    published_end_before: Optional[date]
    target_before: Optional[ProposalTarget]
    question_before: Optional[str]
    answer_before: Optional[str]
    add_comments_before: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True