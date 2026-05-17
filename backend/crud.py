from sqlalchemy.orm import Session
from sqlalchemy import or_
from . import models, schemas
import math

def get_opportunities(
    db: Session, 
    skip: int = 0, 
    limit: int = 20, 
    search: str = None,
    type: str = None,
    source: str = None,
    startup_stage: str = None
):
    query = db.query(models.Opportunity)
    
    if search:
        search_filter = f"%{search}%"
        query = query.filter(
            or_(
                models.Opportunity.title.ilike(search_filter),
                models.Opportunity.organizer.ilike(search_filter),
                models.Opportunity.location.ilike(search_filter)
            )
        )
    
    if type:
        query = query.filter(models.Opportunity.type == type)
    if source:
        query = query.filter(models.Opportunity.source_name == source)
    if startup_stage:
        query = query.filter(models.Opportunity.startup_stage == startup_stage)
        
    total = query.count()
    items = query.order_by(models.Opportunity.created_at.desc()).offset(skip).limit(limit).all()
    
    return {
        "total": total,
        "page": math.floor(skip / limit) + 1 if limit > 0 else 1,
        "size": limit,
        "items": items
    }

def get_filter_options(db: Session):
    types = [r[0] for r in db.query(models.Opportunity.type).distinct().all() if r[0]]
    sources = [r[0] for r in db.query(models.Opportunity.source_name).distinct().all() if r[0]]
    stages = [r[0] for r in db.query(models.Opportunity.startup_stage).distinct().all() if r[0]]
    
    return {
        "types": types,
        "sources": sources,
        "startup_stages": stages
    }
