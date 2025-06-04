from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, TIMESTAMPTZ
from sqlalchemy.sql import text
from sqlalchemy.orm import relationship
from app.database import Base


class Article(Base):
    __tablename__ = "articles"

    id = Column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    article_id = Column(String(50), nullable=False, unique=True)
    article = Column(String(255), nullable=False, unique=True)
    approval_group_id = Column(UUID(as_uuid=True), ForeignKey("groups.id"), nullable=False)
    created_at = Column(TIMESTAMPTZ, server_default=text("CURRENT_TIMESTAMP"))
    updated_at = Column(TIMESTAMPTZ, server_default=text("CURRENT_TIMESTAMP"))
    
    # Relationships
    approval_group = relationship("Group", back_populates="articles")
    proposals = relationship("Proposal", back_populates="article")