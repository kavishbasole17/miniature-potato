import os
from dotenv import load_dotenv

env_path = os.path.join(os.path.dirname(__file__), ".env")
load_dotenv(env_path)

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./opportunities.db")
SCRAPER_USER_AGENT = os.getenv("SCRAPER_USER_AGENT", "Mozilla/5.0")
DEFAULT_KEYWORD = os.getenv("DEFAULT_KEYWORD", "")
DEFAULT_REGION = os.getenv("DEFAULT_REGION", "")
SCRAPE_INTERVAL_MINUTES = int(os.getenv("SCRAPE_INTERVAL_MINUTES", "360"))
if SCRAPE_INTERVAL_MINUTES < 10:
    SCRAPE_INTERVAL_MINUTES = 10

WEBHOOK_URL = os.getenv("WEBHOOK_URL", "")
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET", "")

FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin" if os.getenv("ADMIN_PASSWORD") else "")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "")
SESSION_SECRET = os.getenv("SESSION_SECRET", ADMIN_PASSWORD if ADMIN_PASSWORD else "default-secret")
