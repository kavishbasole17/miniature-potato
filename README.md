# Startup Orbit - Opportunities Scraper & Dashboard

A full-stack application built with React (Vite) and FastAPI to automatically collect, store, and display startup opportunities (grants, conferences, jobs, accelerators) from multiple sources. 

## Features
- **Automated Scraping**: Periodically scrapes sources for new opportunities (Hacker News Jobs, Techstars, and custom fallbacks).
- **Aesthetic Dashboard**: Premium, modern dark-themed UI built with React, TailwindCSS, and Framer Motion.
- **Search & Filter**: Keyword search, filter by opportunity type, source, and startup stage.
- **Data Export**: Export stored opportunities to CSV.
- **Anti-Duplication**: Uniquely tracks opportunities via source URLs to prevent duplicates.

## Note on Scraping Challenges and Handling
Scraping modern web platforms comes with significant challenges:
1. **Cloudflare & Bot Protection**: Many startup directories (like Betalist or well-known grants platforms) heavily utilize anti-bot protection that blocks standard `requests` via CAPTCHAs. 
2. **Dynamic Content rendering**: Sites often load opportunities dynamically via JavaScript (React/Vue) and not server-side HTML.
3. **Handling**:
   - Implemented standard browser headers (`User-Agent`, `Accept`) to bypass basic blocks.
   - For highly protected directories, fallback datasets have been securely coded to ensure the system is populated with at least 20+ verified, real-world startup opportunities (YC, Sequoia Arc, Google for Startups, etc.).
   - Used robust `try-except` error handling around network requests to ensure the background scheduler doesn't crash if a site changes its structure or temporarily blocks the IP.

## Setup Instructions

### Backend (FastAPI)
1. Navigate to the backend directory:
   ```bash
   cd backend
   ```
2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   # Windows:
   .\venv\Scripts\activate
   # Mac/Linux:
   source venv/bin/activate
   ```
3. Install dependencies:
   ```bash
   pip install fastapi uvicorn sqlalchemy requests beautifulsoup4 apscheduler pydantic pandas lxml
   ```
4. Run the server:
   ```bash
   python -m uvicorn main:app --reload --port 8000
   ```
   *(The server will automatically trigger the initial scrape upon startup)*

### Frontend (React + Vite)
1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```
2. Install dependencies:
   ```bash
   npm install
   ```
3. Run the development server:
   ```bash
   npm run dev
   ```

## Technologies Used
- **Frontend**: React, TypeScript, TailwindCSS, Framer Motion, Lucide React, Vite
- **Backend**: FastAPI, SQLAlchemy (SQLite), APScheduler, BeautifulSoup4, Pandas
