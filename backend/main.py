import os
import io
import json
from contextlib import asynccontextmanager
from typing import Optional

import pandas as pd
from fastapi import FastAPI, Depends, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from apscheduler.schedulers.background import BackgroundScheduler

import models
import schemas
import crud
import scraper
import config
import admin_auth
import webhook
from database import engine, get_db, SessionLocal

# Create all tables
models.Base.metadata.create_all(bind=engine)

scheduler = BackgroundScheduler()

_STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")


def scheduled_scrape():
    """Provide a fresh DB session for the background scraper task."""
    db = SessionLocal()
    try:
        scraper.run_scraper(db)
    except Exception as e:
        print(f"[Scheduler] Scrape failed: {e}")
    finally:
        db.close()


@asynccontextmanager
async def lifespan(app: FastAPI):
    from seed import init_db
    db = SessionLocal()
    init_db(db)
    db.close()
    scheduled_scrape()
    interval = max(10, config.SCRAPE_INTERVAL_MINUTES)
    scheduler.add_job(scheduled_scrape, "interval", minutes=interval, id="scrape_job")
    scheduler.start()
    yield
    scheduler.shutdown(wait=False)


app = FastAPI(title="Startup Opportunities API", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173", config.FRONTEND_URL],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve static files (theme.js etc.) — path relative to this file
if os.path.isdir(_STATIC_DIR):
    app.mount("/static", StaticFiles(directory=_STATIC_DIR), name="static")


# ─── Public API ───────────────────────────────────────────

@app.get("/api/health")
def read_health():
    return {
        "app": "startup-opportunity-aggregator",
        "project_root": os.getcwd(),
        "admin_paths_registered": True,
    }


@app.get("/api/opportunities", response_model=schemas.PaginatedOpportunities)
def read_opportunities(
    skip: int = 0,
    limit: int = 20,
    search: Optional[str] = None,
    type: Optional[str] = None,
    source: Optional[str] = None,
    startup_stage: Optional[str] = None,
    db: Session = Depends(get_db),
):
    return crud.get_opportunities(db, skip, limit, search, type, source, startup_stage)


# NOTE: export routes MUST be registered before the /{id} catch-all
@app.get("/api/opportunities/export.json")
def export_json(db: Session = Depends(get_db)):
    res = crud.get_opportunities(db, skip=0, limit=100_000)
    return [schemas.Opportunity.model_validate(i).model_dump() for i in res["items"]]


@app.get("/api/opportunities/export.csv")
def export_csv(db: Session = Depends(get_db)):
    res = crud.get_opportunities(db, skip=0, limit=100_000)
    items = res["items"]
    data = [
        {
            "Title": item.title,
            "Type": item.type,
            "Organizer": item.organizer,
            "Location": item.location,
            "Deadline": item.deadline,
            "Source": item.source_name,
            "Link": item.source_link,
            "Funding Range": item.funding_range,
            "Startup Stage": item.startup_stage,
            "Remote": item.is_remote,
        }
        for item in items
    ]
    df = pd.DataFrame(data)
    stream = io.StringIO()
    df.to_csv(stream, index=False)
    return Response(
        content=stream.getvalue(),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=opportunities.csv"},
    )


@app.get("/api/opportunities/{id}", response_model=schemas.Opportunity)
def read_opportunity(id: int, db: Session = Depends(get_db)):
    opp = crud.get_opportunity(db, id)
    if not opp:
        raise HTTPException(status_code=404, detail="Not Found")
    return opp


@app.post("/api/opportunities", response_model=schemas.Opportunity)
def create_opportunity(opp: schemas.OpportunityCreate, db: Session = Depends(get_db), auth: bool = Depends(admin_auth.check_admin_auth)):
    return crud.create_opportunity(db, opp)


@app.patch("/api/opportunities/{id}", response_model=schemas.Opportunity)
def update_opportunity(id: int, opp: schemas.OpportunityUpdate, db: Session = Depends(get_db), auth: bool = Depends(admin_auth.check_admin_auth)):
    updated = crud.update_opportunity(db, id, opp)
    if not updated:
        raise HTTPException(status_code=404, detail="Not Found")
    return updated


@app.delete("/api/opportunities/{id}")
def delete_opportunity(id: int, db: Session = Depends(get_db), auth: bool = Depends(admin_auth.check_admin_auth)):
    deleted = crud.delete_opportunity(db, id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Not Found")
    return {"ok": True}


@app.get("/api/regions")
def read_regions(db: Session = Depends(get_db)):
    return crud.get_region_hints(db)

@app.get("/api/sources")
def read_sources(db: Session = Depends(get_db)):
    return crud.get_scrape_sources(db)

@app.get("/api/logs")
def read_logs(db: Session = Depends(get_db)):
    return db.query(models.ImportLog).order_by(models.ImportLog.id.desc()).limit(50).all()


from fastapi import Form
import hashlib

@app.post("/api/admin/auth/login")
def api_admin_login(
    response: Response, 
    username: str = Form(...), 
    password: str = Form(...), 
    db: Session = Depends(get_db)
):
    if not config.ADMIN_PASSWORD:
        # If no password is set, login is effectively disabled, 
        # but let's just let the frontend know.
        raise HTTPException(status_code=401, detail="Admin login disabled (no ADMIN_PASSWORD in env)")
        
    valid = False
    user = crud.get_user_by_username(db, username)
    
    def verify_password(plain_password, hashed_password):
        return hashlib.sha256(plain_password.encode()).hexdigest() == hashed_password
        
    if user and user.is_active and verify_password(password, user.password_hash):
        valid = True
    elif username.lower() == config.ADMIN_USERNAME.lower() and password == config.ADMIN_PASSWORD:
        valid = True
        
    if valid:
        response.set_cookie("session_user", username, httponly=True, samesite="none", secure=True)
        return {"ok": True, "message": "Logged in successfully"}
        
    raise HTTPException(status_code=401, detail="Invalid credentials")

@app.get("/api/admin/check")
def check_admin_login(auth: bool = Depends(admin_auth.check_admin_auth)):
    return {"ok": True, "message": "Logged in"}

@app.post("/api/admin/auth/logout")
def api_admin_logout(response: Response):
    response.delete_cookie("session_user", samesite="none", secure=True)
    return {"ok": True, "message": "Logged out"}


@app.get("/api/scrape")
@app.post("/api/scrape")
def trigger_public_scrape(db: Session = Depends(get_db)):
    added = scraper.run_scraper(db)
    return {"message": "Scrape completed.", "import_log_id": 1, "added": added}


@app.get("/api/options")
def read_options(db: Session = Depends(get_db)):
    return crud.get_filter_options(db)


# ─── Admin HTML routes (must come last) ───────────────────
from admin_routes import router as admin_router  # noqa: E402
app.include_router(admin_router)
