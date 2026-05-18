from sqlalchemy.orm import Session
from sqlalchemy import or_
import models, schemas
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

def get_user_by_username(db: Session, username: str):
    from sqlalchemy import func
    return db.query(models.AppUser).filter(func.lower(models.AppUser.username) == func.lower(username)).first()

def get_region_hints(db: Session):
    return [r.name for r in db.query(models.RegionHint).all()]

def get_scrape_sources(db: Session):
    return db.query(models.ScrapeSource).all()

def get_opportunity(db: Session, id: int):
    return db.query(models.Opportunity).filter(models.Opportunity.id == id).first()

def create_opportunity(db: Session, opp: schemas.OpportunityCreate):
    db_opp = models.Opportunity(**opp.dict())
    db.add(db_opp)
    db.commit()
    db.refresh(db_opp)
    return db_opp

def update_opportunity(db: Session, id: int, opp: schemas.OpportunityUpdate):
    db_opp = get_opportunity(db, id)
    if db_opp:
        for key, value in opp.dict(exclude_unset=True).items():
            setattr(db_opp, key, value)
        db.commit()
        db.refresh(db_opp)
    return db_opp

def delete_opportunity(db: Session, id: int):
    db_opp = get_opportunity(db, id)
    if db_opp:
        db.delete(db_opp)
        db.commit()
    return db_opp
