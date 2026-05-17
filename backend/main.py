from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from sqlalchemy.orm import Session
from contextlib import asynccontextmanager
from apscheduler.schedulers.background import BackgroundScheduler
from typing import Optional
import pandas as pd
import io

from . import models, schemas, crud, scraper
from .database import engine, get_db, SessionLocal

models.Base.metadata.create_all(bind=engine)

scheduler = BackgroundScheduler()


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
    # Run scraper once on startup to populate the DB
    scheduled_scrape()
    # Schedule subsequent scrapes every 12 hours
    scheduler.add_job(scheduled_scrape, "interval", hours=12, id="scrape_job")
    scheduler.start()
    yield
    scheduler.shutdown(wait=False)


app = FastAPI(title="Startup Opportunities API", version="1.0.0", lifespan=lifespan)

# Allow React dev server and any deployment origin
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/opportunities", response_model=schemas.PaginatedOpportunities)
def read_opportunities(
    skip: int = 0,
    limit: int = 20,
    search: Optional[str] = None,
    type: Optional[str] = None,  # matches frontend query param name
    source: Optional[str] = None,
    startup_stage: Optional[str] = None,
    db: Session = Depends(get_db),
):
    return crud.get_opportunities(db, skip, limit, search, type, source, startup_stage)


@app.get("/api/options")
def read_options(db: Session = Depends(get_db)):
    return crud.get_filter_options(db)


@app.post("/api/scrape")
def trigger_scrape(db: Session = Depends(get_db)):
    added = scraper.run_scraper(db)
    return {"message": f"Scrape completed. Added {added} new opportunities."}


@app.get("/api/export/csv")
def export_csv(db: Session = Depends(get_db)):
    """Export all stored opportunities to a CSV file."""
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
