from sqlalchemy.orm import Session
import models

def init_db(db: Session):
    if db.query(models.RegionHint).count() == 0:
        regions = ["Global", "North America", "Europe", "Asia", "Remote"]
        for r in regions:
            db.add(models.RegionHint(name=r))
        db.commit()

    if db.query(models.ScrapeSource).count() == 0:
        db.add(models.ScrapeSource(name="Techstars", kind="techstars", is_enabled=1))
        db.add(models.ScrapeSource(name="EU-Startups", kind="rss", feed_url="https://www.eu-startups.com/feed/", is_enabled=1))
        db.commit()
