from sqlalchemy import Column, Integer, String, DateTime, Text, UniqueConstraint
from sqlalchemy.sql import func
from .database import Base
import datetime

class Opportunity(Base):
    __tablename__ = "opportunities"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    type = Column(String, index=True) # Grant, Conference, Accelerator, etc.
    organizer = Column(String)
    location = Column(String, nullable=True) # Includes eligibility / location
    deadline = Column(String, nullable=True) # Could be text like "April 30, 2026"
    source_link = Column(String)
    source_name = Column(String, index=True) # e.g., "OpenGrants", "YC"
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Auto-tag fields
    funding_range = Column(String, nullable=True)
    startup_stage = Column(String, nullable=True)
    is_remote = Column(String, nullable=True) # "Yes", "No", "Hybrid", etc.

    __table_args__ = (UniqueConstraint('source_link', name='_source_link_uc'),)
