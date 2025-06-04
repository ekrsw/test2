from sqlalchemy import Column, String, Text
from sqlalchemy.dialects.postgresql import UUID, TIMESTAMPTZ
from sqlalchemy.sql import text
from sqlalchemy.orm import relationship
from app.database import Base


class InfoCategory(Base):
    __tablename__ = "info_categories"

    id = Column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(TIMESTAMPTZ, server_default=text("CURRENT_TIMESTAMP"))
    updated_at = Column(TIMESTAMPTZ, server_default=text("CURRENT_TIMESTAMP"))
    
    # Relationships
    proposals = relationship("Proposal", back_populates="info_category")
    proposals_before = relationship("ProposalBefore", back_populates="info_category_before")