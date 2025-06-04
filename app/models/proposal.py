from sqlalchemy import Column, String, Text, Boolean, Date, ForeignKey, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID, TIMESTAMPTZ
from sqlalchemy.sql import text
from sqlalchemy.orm import relationship
from app.database import Base


class Proposal(Base):
    __tablename__ = "proposals"

    id = Column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    article_id = Column(String(50), ForeignKey("articles.article_id"), nullable=False)
    article = Column(String(255), nullable=False)
    type = Column(String(10), nullable=False)
    status = Column(String(10), nullable=False, default="申請中")
    title = Column(String(500), nullable=False)
    info_category_id = Column(UUID(as_uuid=True), ForeignKey("info_categories.id"), nullable=True)
    keywords = Column(Text, nullable=True)
    importance = Column(Boolean, nullable=True)
    published_start = Column(Date, nullable=True)
    published_end = Column(Date, nullable=True)
    target = Column(String(10), nullable=True)
    question = Column(Text, nullable=True)
    answer = Column(Text, nullable=True)
    add_comments = Column(Text, nullable=True)
    reason = Column(Text, nullable=False)
    approval_group_id = Column(UUID(as_uuid=True), ForeignKey("groups.id"), nullable=False)
    approved_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    approved_at = Column(TIMESTAMPTZ, nullable=True)
    rejection_reason = Column(Text, nullable=True)
    created_at = Column(TIMESTAMPTZ, server_default=text("CURRENT_TIMESTAMP"))
    updated_at = Column(TIMESTAMPTZ, server_default=text("CURRENT_TIMESTAMP"))
    
    # Check constraints
    __table_args__ = (
        CheckConstraint("type IN ('修正', '削除')", name="chk_proposal_type"),
        CheckConstraint("status IN ('申請中', '承認済み', '却下')", name="chk_proposal_status"),
        CheckConstraint("target IN ('社内向け', '社外向け', '該当なし') OR target IS NULL", name="chk_proposal_target"),
        CheckConstraint(
            "(status != '却下') OR (status = '却下' AND rejection_reason IS NOT NULL AND rejection_reason != '')",
            name="chk_rejection_reason"
        ),
    )
    
    # Relationships
    user = relationship("User", back_populates="proposals", foreign_keys=[user_id])
    article_ref = relationship("Article", back_populates="proposals")
    info_category = relationship("InfoCategory", back_populates="proposals")
    approval_group = relationship("Group", back_populates="proposals")
    approver = relationship("User", back_populates="approved_proposals", foreign_keys=[approved_by])
    proposal_before = relationship("ProposalBefore", back_populates="proposal", uselist=False)