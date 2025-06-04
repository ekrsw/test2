from sqlalchemy import Column, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import text
from sqlalchemy.orm import relationship
from app.database import Base


class Group(Base):
    __tablename__ = "groups"

    id = Column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    
    # Relationships
    users = relationship("User", back_populates="group")
    articles = relationship("Article", back_populates="approval_group")
    proposals = relationship("Proposal", back_populates="approval_group")