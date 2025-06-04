from sqlalchemy import Column, String, ForeignKey, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID, TIMESTAMPTZ
from sqlalchemy.sql import text
from sqlalchemy.orm import relationship
from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    username = Column(String(50), nullable=False, unique=True)
    email = Column(String(255), nullable=False, unique=True)
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(20), nullable=False)
    group_id = Column(UUID(as_uuid=True), ForeignKey("groups.id"), nullable=True)
    created_at = Column(TIMESTAMPTZ, server_default=text("CURRENT_TIMESTAMP"))
    updated_at = Column(TIMESTAMPTZ, server_default=text("CURRENT_TIMESTAMP"))
    
    # Check constraints
    __table_args__ = (
        CheckConstraint("role IN ('一般ユーザー', 'SV', '管理者')", name="chk_user_role"),
    )
    
    # Relationships
    group = relationship("Group", back_populates="users")
    proposals = relationship("Proposal", back_populates="user", foreign_keys="[Proposal.user_id]")
    approved_proposals = relationship("Proposal", back_populates="approver", foreign_keys="[Proposal.approved_by]")