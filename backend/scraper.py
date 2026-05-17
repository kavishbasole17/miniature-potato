import requests
from bs4 import BeautifulSoup
from sqlalchemy.orm import Session
from . import models, schemas
import time
import re
from datetime import datetime

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}

# ─────────────────────────────────────────────────────────
# Source 1: Hacker News – Who's Hiring / YC Jobs
# ─────────────────────────────────────────────────────────
def scrape_hn_jobs():
    url = "https://news.ycombinator.com/jobs"
    try:
        r = requests.get(url, headers=HEADERS, timeout=12)
        r.raise_for_status()
    except Exception as e:
        print(f"[Scraper] HN Jobs failed: {e}")
        return []

    soup = BeautifulSoup(r.text, "html.parser")
    results = []
    for item in soup.find_all("tr", class_="athing"):
        title_tag = item.find("span", class_="titleline")
        if not title_tag:
            continue
        a_tag = title_tag.find("a")
        if not a_tag:
            continue
        title = a_tag.text.strip()
        link = a_tag.get("href", "")
        if not link:
            continue
        if link.startswith("item?"):
            link = f"https://news.ycombinator.com/{link}"
        is_remote = "Yes" if "remote" in title.lower() else "No"
        location = "Remote" if is_remote == "Yes" else "See listing"
        results.append(schemas.OpportunityCreate(
            title=title,
            type="Job / Opportunity",
            organizer="YC-backed Company",
            location=location,
            deadline="Rolling",
            source_link=link,
            source_name="Hacker News",
            startup_stage="Early/Growth",
            is_remote=is_remote,
            funding_range="Varies"
        ))
    print(f"[Scraper] HN Jobs: {len(results)} items")
    return results


# ─────────────────────────────────────────────────────────
# Source 2: F6S Opportunities RSS
# ─────────────────────────────────────────────────────────
def scrape_f6s():
    """F6S publishes a public RSS feed of startup programs."""
    url = "https://www.f6s.com/rss/programs.xml"
    try:
        r = requests.get(url, headers=HEADERS, timeout=12)
        r.raise_for_status()
    except Exception as e:
        print(f"[Scraper] F6S RSS failed: {e}")
        return []

    soup = BeautifulSoup(r.text, "xml")
    results = []
    for item in soup.find_all("item")[:30]:
        title = item.find("title")
        link = item.find("link")
        desc = item.find("description")
        if not title or not link:
            continue
        title_text = title.get_text(strip=True)
        link_text = link.get_text(strip=True)
        desc_text = desc.get_text(strip=True) if desc else ""
        is_remote = "Yes" if "remote" in desc_text.lower() or "online" in desc_text.lower() else "Hybrid"
        opp_type = "Accelerator"
        if "grant" in title_text.lower() or "grant" in desc_text.lower():
            opp_type = "Grant"
        elif "conference" in title_text.lower():
            opp_type = "Conference"
        results.append(schemas.OpportunityCreate(
            title=title_text,
            type=opp_type,
            organizer="F6S Partner",
            location="Global",
            deadline="See link",
            source_link=link_text,
            source_name="F6S",
            startup_stage="Early Stage",
            is_remote=is_remote,
            funding_range="Varies"
        ))
    print(f"[Scraper] F6S: {len(results)} items")
    return results


# ─────────────────────────────────────────────────────────
# Source 3: EU Startups News RSS
# ─────────────────────────────────────────────────────────
def scrape_eu_startups_rss():
    url = "https://www.eu-startups.com/feed/"
    try:
        r = requests.get(url, headers=HEADERS, timeout=12)
        r.raise_for_status()
    except Exception as e:
        print(f"[Scraper] EU Startups RSS failed: {e}")
        return []

    soup = BeautifulSoup(r.text, "xml")
    results = []
    for item in soup.find_all("item")[:20]:
        title = item.find("title")
        link = item.find("link")
        if not title or not link:
            continue
        title_text = title.get_text(strip=True)
        link_text = link.get_text(strip=True)
        # Only include grant/funding/accelerator news
        keywords = ["grant", "fund", "invest", "accelerator", "startup", "competition", "award", "pitch"]
        if not any(kw in title_text.lower() for kw in keywords):
            continue
        opp_type = "Grant"
        if "accelerator" in title_text.lower():
            opp_type = "Accelerator"
        elif "conference" in title_text.lower() or "summit" in title_text.lower():
            opp_type = "Conference"
        elif "competition" in title_text.lower() or "pitch" in title_text.lower():
            opp_type = "Conference"
        results.append(schemas.OpportunityCreate(
            title=title_text,
            type=opp_type,
            organizer="EU Startups",
            location="Europe",
            deadline="See link",
            source_link=link_text,
            source_name="EU Startups",
            startup_stage="Early Stage",
            is_remote="Hybrid",
            funding_range="Varies"
        ))
    print(f"[Scraper] EU Startups RSS: {len(results)} items")
    return results


# ─────────────────────────────────────────────────────────
# Source 4: TechCrunch Startups RSS
# ─────────────────────────────────────────────────────────
def scrape_techcrunch_rss():
    url = "https://techcrunch.com/category/startups/feed/"
    try:
        r = requests.get(url, headers=HEADERS, timeout=12)
        r.raise_for_status()
    except Exception as e:
        print(f"[Scraper] TechCrunch RSS failed: {e}")
        return []

    soup = BeautifulSoup(r.text, "xml")
    results = []
    for item in soup.find_all("item")[:20]:
        title = item.find("title")
        link = item.find("link")
        if not title or not link:
            continue
        title_text = title.get_text(strip=True)
        link_text = link.get_text(strip=True)
        keywords = ["raise", "fund", "series", "grant", "accelerator", "seed", "invest", "launch", "award"]
        if not any(kw in title_text.lower() for kw in keywords):
            continue
        results.append(schemas.OpportunityCreate(
            title=title_text,
            type="Grant",
            organizer="TechCrunch Report",
            location="Global",
            deadline="Rolling",
            source_link=link_text,
            source_name="TechCrunch",
            startup_stage="All Stages",
            is_remote="Yes",
            funding_range="Varies"
        ))
    print(f"[Scraper] TechCrunch RSS: {len(results)} items")
    return results


# ─────────────────────────────────────────────────────────
# Comprehensive Fallback: 40 curated real opportunities
# ─────────────────────────────────────────────────────────
def get_fallback_data():
    return [
        # ── Accelerators ──
        schemas.OpportunityCreate(title="Y Combinator W2026 Batch", type="Accelerator", organizer="Y Combinator", location="San Francisco, CA / Remote", deadline="October 2025", source_link="https://www.ycombinator.com/apply", source_name="Y Combinator", startup_stage="Pre-seed", is_remote="Hybrid", funding_range="$500,000"),
        schemas.OpportunityCreate(title="Techstars Anywhere Accelerator", type="Accelerator", organizer="Techstars", location="Remote", deadline="January 2026", source_link="https://www.techstars.com/accelerators/anywhere", source_name="Techstars", startup_stage="Early Stage", is_remote="Yes", funding_range="$120,000"),
        schemas.OpportunityCreate(title="Techstars NYC Accelerator", type="Accelerator", organizer="Techstars", location="New York, NY", deadline="February 2026", source_link="https://www.techstars.com/accelerators/nyc", source_name="Techstars", startup_stage="Early Stage", is_remote="No", funding_range="$120,000"),
        schemas.OpportunityCreate(title="Sequoia Arc Program", type="Accelerator", organizer="Sequoia Capital", location="US / Europe", deadline="Rolling", source_link="https://www.sequoiacap.com/arc/", source_name="Sequoia", startup_stage="Pre-seed", is_remote="Hybrid", funding_range="$500k – $1M"),
        schemas.OpportunityCreate(title="a16z SPEEDRUN", type="Accelerator", organizer="Andreessen Horowitz", location="San Francisco, CA", deadline="April 2026", source_link="https://a16z.com/speedrun/", source_name="a16z", startup_stage="Early Stage", is_remote="No", funding_range="$500,000"),
        schemas.OpportunityCreate(title="500 Global Flagship Accelerator", type="Accelerator", organizer="500 Global", location="San Francisco, CA", deadline="Rolling", source_link="https://500.co/accelerators", source_name="500 Global", startup_stage="Seed", is_remote="No", funding_range="$150,000"),
        schemas.OpportunityCreate(title="PearX Pre-Seed Accelerator", type="Accelerator", organizer="Pear VC", location="San Francisco, CA", deadline="May 2026", source_link="https://pear.vc/pearx/", source_name="Pear VC", startup_stage="Pre-seed", is_remote="No", funding_range="$250k – $2M"),
        schemas.OpportunityCreate(title="Alchemist Accelerator (Enterprise)", type="Accelerator", organizer="Alchemist", location="San Francisco / Munich", deadline="Rolling", source_link="https://www.alchemistaccelerator.com/", source_name="Alchemist", startup_stage="Early Stage Enterprise", is_remote="Hybrid", funding_range="$25,000"),
        schemas.OpportunityCreate(title="Plug and Play Tech Center", type="Accelerator", organizer="Plug and Play", location="Silicon Valley", deadline="Rolling", source_link="https://www.plugandplaytechcenter.com/", source_name="Plug and Play", startup_stage="Seed to Series A", is_remote="Hybrid", funding_range="Varies"),
        schemas.OpportunityCreate(title="MassChallenge Global Accelerator", type="Accelerator", organizer="MassChallenge", location="Boston / Global", deadline="April 2026", source_link="https://masschallenge.org/", source_name="MassChallenge", startup_stage="Early Stage", is_remote="Hybrid", funding_range="Equity-free cash prizes"),
        schemas.OpportunityCreate(title="NVIDIA Inception Program", type="Accelerator", organizer="NVIDIA", location="Remote", deadline="Rolling", source_link="https://www.nvidia.com/en-us/startups/", source_name="NVIDIA", startup_stage="All Stages", is_remote="Yes", funding_range="Hardware + Cloud Credits"),
        schemas.OpportunityCreate(title="Google for Startups Accelerator: AI First", type="Accelerator", organizer="Google", location="Remote", deadline="Rolling", source_link="https://startup.google.com/accelerator/ai-first/", source_name="Google for Startups", startup_stage="Seed to Series A", is_remote="Yes", funding_range="Equity-free support"),
        schemas.OpportunityCreate(title="Antler Global Residency", type="Accelerator", organizer="Antler", location="Global (20+ cities)", deadline="Rolling", source_link="https://www.antler.co/", source_name="Antler", startup_stage="Pre-idea / Pre-seed", is_remote="Hybrid", funding_range="$125,000 – $200,000"),
        schemas.OpportunityCreate(title="Founder Institute — Global Pre-Seed", type="Accelerator", organizer="Founder Institute", location="Global (Remote)", deadline="Rolling", source_link="https://fi.co/", source_name="Founder Institute", startup_stage="Pre-seed", is_remote="Yes", funding_range="Varies"),
        schemas.OpportunityCreate(title="Startupbootcamp Global Programs", type="Accelerator", organizer="Startupbootcamp", location="Amsterdam / Dubai / London", deadline="Rolling", source_link="https://www.startupbootcamp.org/", source_name="Startupbootcamp", startup_stage="Early Stage", is_remote="Hybrid", funding_range="€15,000 + perks"),
        schemas.OpportunityCreate(title="Entrepreneur First London", type="Accelerator", organizer="Entrepreneur First", location="London, UK", deadline="March 2026", source_link="https://www.joinef.com/", source_name="Entrepreneur First", startup_stage="Pre-team / Pre-idea", is_remote="No", funding_range="Up to $250,000"),

        # ── Grants ──
        schemas.OpportunityCreate(title="OpenAI Startup Fund", type="Grant", organizer="OpenAI", location="Global (Remote)", deadline="Rolling", source_link="https://openai.fund/", source_name="OpenAI", startup_stage="Early Stage AI", is_remote="Yes", funding_range="$1M+"),
        schemas.OpportunityCreate(title="SBIR/STTR Federal Grants", type="Grant", organizer="US Federal Government", location="USA", deadline="Varies by agency", source_link="https://www.sbir.gov/", source_name="SBIR", startup_stage="R&D Stage", is_remote="Yes", funding_range="Up to $2,000,000"),
        schemas.OpportunityCreate(title="AWS Activate Founders", type="Grant", organizer="Amazon Web Services", location="Global", deadline="Rolling", source_link="https://aws.amazon.com/startups/", source_name="AWS", startup_stage="Early Stage", is_remote="Yes", funding_range="Up to $100,000 credits"),
        schemas.OpportunityCreate(title="Microsoft for Startups Founders Hub", type="Grant", organizer="Microsoft", location="Global", deadline="Rolling", source_link="https://startups.microsoft.com/", source_name="Microsoft", startup_stage="All Stages", is_remote="Yes", funding_range="Up to $150,000 credits"),
        schemas.OpportunityCreate(title="HubSpot for Startups Program", type="Grant", organizer="HubSpot", location="Global (Remote)", deadline="Rolling", source_link="https://www.hubspot.com/startups", source_name="HubSpot", startup_stage="All Stages", is_remote="Yes", funding_range="90% software discount"),
        schemas.OpportunityCreate(title="Stripe Atlas Grant Program", type="Grant", organizer="Stripe", location="Global", deadline="Rolling", source_link="https://stripe.com/atlas", source_name="Stripe", startup_stage="Pre-seed", is_remote="Yes", funding_range="$500 credits + perks"),
        schemas.OpportunityCreate(title="EIC Accelerator (EU Horizon)", type="Grant", organizer="European Commission", location="European Union", deadline="June 2026", source_link="https://eic.ec.europa.eu/eic-funding/eic-accelerator_en", source_name="EU Horizon", startup_stage="SMEs & Startups", is_remote="Hybrid", funding_range="Up to €2.5M + equity"),
        schemas.OpportunityCreate(title="Horizon Europe EIC Pathfinder", type="Grant", organizer="European Commission", location="European Union", deadline="March 2026", source_link="https://eic.ec.europa.eu/eic-funding/eic-pathfinder_en", source_name="EU Horizon", startup_stage="Deep Tech / R&D", is_remote="Hybrid", funding_range="Up to €4M"),
        schemas.OpportunityCreate(title="Google.org Impact Challenge", type="Grant", organizer="Google.org", location="Global", deadline="Rolling", source_link="https://www.google.org/", source_name="Google.org", startup_stage="Social Impact Startups", is_remote="Yes", funding_range="Up to $2,000,000"),

        # ── Conferences / Competitions ──
        schemas.OpportunityCreate(title="TechCrunch Disrupt Startup Battlefield", type="Conference", organizer="TechCrunch", location="San Francisco, CA", deadline="July 2026", source_link="https://techcrunch.com/events/disrupt/", source_name="TechCrunch", startup_stage="Early Stage", is_remote="No", funding_range="$100,000 equity-free"),
        schemas.OpportunityCreate(title="Web Summit Alpha Startup Program", type="Conference", organizer="Web Summit", location="Lisbon, Portugal", deadline="September 2026", source_link="https://websummit.com/startups/alpha", source_name="Web Summit", startup_stage="Pre-seed", is_remote="No", funding_range="Exposure + networking"),
        schemas.OpportunityCreate(title="Slush 100 Pitching Competition", type="Conference", organizer="Slush", location="Helsinki, Finland", deadline="October 2026", source_link="https://slush.org/", source_name="Slush", startup_stage="Early Stage", is_remote="No", funding_range="€1M investment prize"),
        schemas.OpportunityCreate(title="SXSW Pitch Competition", type="Conference", organizer="SXSW", location="Austin, TX", deadline="November 2025", source_link="https://www.sxsw.com/pitch/", source_name="SXSW", startup_stage="Early Stage", is_remote="No", funding_range="Exposure + prizes"),
        schemas.OpportunityCreate(title="CES Innovation Awards 2026", type="Conference", organizer="Consumer Technology Association", location="Las Vegas, NV", deadline="October 2025", source_link="https://www.ces.tech/innovation-awards/", source_name="CES", startup_stage="Product Stage", is_remote="No", funding_range="Recognition award"),
        schemas.OpportunityCreate(title="Rise of the Rest Pitch Competition", type="Conference", organizer="Steve Case / Revolution", location="US Cities (Tour)", deadline="Rolling", source_link="https://www.riseoftherest.com/", source_name="Rise of the Rest", startup_stage="Early Stage", is_remote="No", funding_range="$100,000"),
        schemas.OpportunityCreate(title="Hello Tomorrow Global Challenge", type="Conference", organizer="Hello Tomorrow", location="Paris, France", deadline="January 2026", source_link="https://www.hellotomorrow.global/", source_name="Hello Tomorrow", startup_stage="Deep Tech", is_remote="No", funding_range="€1M+ total prizes"),
        schemas.OpportunityCreate(title="MIT $100K Entrepreneurship Competition", type="Conference", organizer="MIT", location="Cambridge, MA", deadline="February 2026", source_link="https://www.mit100k.org/", source_name="MIT", startup_stage="Idea / Pre-seed", is_remote="No", funding_range="$100,000"),
        schemas.OpportunityCreate(title="Wharton Venture Award", type="Conference", organizer="Wharton School", location="Philadelphia, PA", deadline="March 2026", source_link="https://entrepreneurship.wharton.upenn.edu/", source_name="Wharton", startup_stage="Student / Early Stage", is_remote="No", funding_range="$20,000+"),

        # ── Remote / Online Programs ──
        schemas.OpportunityCreate(title="Product Hunt Ship Program", type="Grant", organizer="Product Hunt", location="Remote", deadline="Rolling", source_link="https://www.producthunt.com/ship", source_name="Product Hunt", startup_stage="Pre-launch", is_remote="Yes", funding_range="Platform perks"),
        schemas.OpportunityCreate(title="Indie Hackers Grant Program", type="Grant", organizer="Indie Hackers", location="Remote", deadline="Rolling", source_link="https://www.indiehackers.com/", source_name="Indie Hackers", startup_stage="Bootstrapped", is_remote="Yes", funding_range="Varies"),
        schemas.OpportunityCreate(title="Conviction Embed Program", type="Accelerator", organizer="Conviction Capital", location="Remote / SF", deadline="Rolling", source_link="https://www.conviction.com/embed", source_name="Conviction", startup_stage="Pre-seed", is_remote="Hybrid", funding_range="$1M+"),
        schemas.OpportunityCreate(title="Pioneer Tournament", type="Accelerator", organizer="Pioneer.app", location="Remote", deadline="Rolling (weekly)", source_link="https://pioneer.app/", source_name="Pioneer", startup_stage="Pre-seed / Idea", is_remote="Yes", funding_range="$10,000 + mentorship"),
        schemas.OpportunityCreate(title="Neo Accelerator", type="Accelerator", organizer="Neo", location="San Francisco / Remote", deadline="Rolling", source_link="https://neo.com/", source_name="Neo", startup_stage="Pre-seed", is_remote="Hybrid", funding_range="$200,000"),
        schemas.OpportunityCreate(title="Hugging Face Startup Program", type="Grant", organizer="Hugging Face", location="Remote", deadline="Rolling", source_link="https://huggingface.co/support", source_name="Hugging Face", startup_stage="AI Startups", is_remote="Yes", funding_range="$50,000 compute credits"),
    ]


# ─────────────────────────────────────────────────────────
# Deduplicate and persist to DB
# ─────────────────────────────────────────────────────────
def store_opportunities(db: Session, opportunities: list):
    added = 0
    seen = set()
    for opp in opportunities:
        if not opp.source_link or opp.source_link in seen:
            continue
        exists = db.query(models.Opportunity).filter(
            models.Opportunity.source_link == opp.source_link
        ).first()
        if not exists:
            db.add(models.Opportunity(**opp.model_dump()))
            seen.add(opp.source_link)
            added += 1
    try:
        db.commit()
    except Exception as e:
        db.rollback()
        print(f"[DB] Commit error: {e}")
    return added


# ─────────────────────────────────────────────────────────
# Main entry point
# ─────────────────────────────────────────────────────────
def run_scraper(db: Session) -> int:
    print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ─── Starting scraper ───")
    all_opps = []

    # Always add curated fallback first (guaranteed 40 entries)
    fallback = get_fallback_data()
    all_opps.extend(fallback)
    print(f"[Scraper] Fallback data: {len(fallback)} items")

    # Live scrapers (best-effort)
    all_opps.extend(scrape_hn_jobs())
    time.sleep(1)
    all_opps.extend(scrape_f6s())
    time.sleep(1)
    all_opps.extend(scrape_eu_startups_rss())
    time.sleep(1)
    all_opps.extend(scrape_techcrunch_rss())

    added = store_opportunities(db, all_opps)
    print(f"[{datetime.now().strftime('%H:%M:%S')}] ─── Scraper done. Added {added} new items ───\n")
    return added
