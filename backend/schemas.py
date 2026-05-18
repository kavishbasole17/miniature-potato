from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class OpportunityBase(BaseModel):
    title: str
    type: str
    organizer: str
    location: Optional[str] = None
    deadline: Optional[str] = None
    source_link: str
    source_name: str
    funding_range: Optional[str] = None
    startup_stage: Optional[str] = None
    is_remote: Optional[str] = None


class OpportunityCreate(OpportunityBase):
    pass

class OpportunityUpdate(BaseModel):
    title: Optional[str] = None
    type: Optional[str] = None
    organizer: Optional[str] = None
    location: Optional[str] = None
    deadline: Optional[str] = None
    source_link: Optional[str] = None
    source_name: Optional[str] = None
    funding_range: Optional[str] = None
    startup_stage: Optional[str] = None
    is_remote: Optional[str] = None


class Opportunity(OpportunityBase):
    id: int
    created_at: datetime

    model_config = {"from_attributes": True}  # Pydantic v2 (replaces deprecated orm_mode)


class PaginatedOpportunities(BaseModel):
    total: int
    page: int
    size: int
    items: List[Opportunity]
