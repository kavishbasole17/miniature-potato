import argparse
from backend.database import SessionLocal
from backend.scraper import run_scraper

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--keyword", type=str, default="")
    parser.add_argument("--region", type=str, default="")
    args = parser.parse_args()

    db = SessionLocal()
    try:
        added = run_scraper(db, keyword=args.keyword, region=args.region)
        print(f"Scrape completed successfully. Added {added} new items.")
    finally:
        db.close()
