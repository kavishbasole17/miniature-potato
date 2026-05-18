from sqlalchemy import Column, Integer, String, DateTime, Text, UniqueConstraint
from sqlalchemy.sql import func
from database import Base
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

class RegionHint(Base):
    __tablename__ = "region_hints"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)

class ScrapeSource(Base):
    __tablename__ = "scrape_sources"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    kind = Column(String) # techstars, rss, json
    feed_url = Column(String, nullable=True)
    max_pages = Column(Integer, default=1)
    is_enabled = Column(Integer, default=1)

class ImportLog(Base):
    __tablename__ = "import_logs"
    id = Column(Integer, primary_key=True, index=True)
    trigger = Column(String) # scheduler, manual, cli
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    ended_at = Column(DateTime(timezone=True), nullable=True)
    keyword = Column(String, nullable=True)
    region = Column(String, nullable=True)
    fetch_count = Column(Integer, default=0)
    insert_count = Column(Integer, default=0)
    update_count = Column(Integer, default=0)
    skip_count = Column(Integer, default=0)
    errors_json = Column(Text, nullable=True)
    events_json = Column(Text, nullable=True)

class AppUser(Base):
    __tablename__ = "app_users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password_hash = Column(String)
    is_superuser = Column(Integer, default=0)
    is_active = Column(Integer, default=1)
