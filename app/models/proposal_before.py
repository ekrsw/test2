from sqlalchemy import Column, String, Text, Boolean, Date, ForeignKey, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID, TIMESTAMPTZ
from sqlalchemy.sql import text
from sqlalchemy.orm import relationship
from app.database import Base


class ProposalBefore(Base):
    __tablename__ = "proposals_before"

    id = Column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    proposal_id = Column(UUID(as_uuid=True), ForeignKey("proposals.id"), nullable=False)
    title_before = Column(String(500), nullable=True)
    info_category_id_before = Column(UUID(as_uuid=True), ForeignKey("info_categories.id"), nullable=True)
    keywords_before = Column(Text, nullable=True)
    importance_before = Column(Boolean, nullable=True)
    published_start_before = Column(Date, nullable=True)
    published_end_before = Column(Date, nullable=True)
    target_before = Column(String(10), nullable=True)
    question_before = Column(Text, nullable=True)
    answer_before = Column(Text, nullable=True)
    add_comments_before = Column(Text, nullable=True)
    created_at = Column(TIMESTAMPTZ, server_default=text("CURRENT_TIMESTAMP"))
    
    # Check constraints
    __table_args__ = (
        CheckConstraint("target_before IN ('社内向け', '社外向け', '該当なし') OR target_before IS NULL", name="chk_target_before"),
    )
    
    # Relationships
    proposal = relationship("Proposal", back_populates="proposal_before")
    info_category_before = relationship("InfoCategory", back_populates="proposals_before")