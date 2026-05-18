from fastapi import APIRouter, Request, Depends, Form, Response
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
import crud, config, models
from database import get_db
import hashlib
import os

router = APIRouter()
_TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), "templates")
templates = Jinja2Templates(directory=_TEMPLATE_DIR)

def verify_password(plain_password, hashed_password):
    return hashlib.sha256(plain_password.encode()).hexdigest() == hashed_password

@router.get("/", response_class=HTMLResponse)
def index(request: Request, db: Session = Depends(get_db)):
    data = crud.get_opportunities(db, skip=0, limit=20)
    return templates.TemplateResponse("dashboard.html", {"request": request, "data": data})

@router.get("/admin/login", response_class=HTMLResponse)
@router.get("/login", response_class=HTMLResponse)
@router.get("/api/admin/login", response_class=HTMLResponse)
def admin_login_page(request: Request):
    if not config.ADMIN_PASSWORD:
        return templates.TemplateResponse("admin_disabled.html", {"request": request})
    return templates.TemplateResponse("admin_login.html", {"request": request})

@router.post("/admin/login")
def admin_login(request: Request, response: Response, username: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    if not config.ADMIN_PASSWORD:
        return RedirectResponse("/", status_code=303)
        
    valid = False
    user = crud.get_user_by_username(db, username)
    if user and user.is_active and verify_password(password, user.password_hash):
        valid = True
    elif username.lower() == config.ADMIN_USERNAME.lower() and password == config.ADMIN_PASSWORD:
        valid = True
        
    if valid:
        resp = RedirectResponse("/admin/opportunities", status_code=303)
        resp.set_cookie("session_user", username, httponly=True)
        return resp
        
    return templates.TemplateResponse("admin_login.html", {"request": request, "error": "Invalid credentials"})

@router.get("/admin/logout")
def admin_logout(response: Response):
    resp = RedirectResponse("/", status_code=303)
    resp.delete_cookie("session_user")
    return resp

def check_session(request: Request):
    if config.ADMIN_PASSWORD and not request.cookies.get("session_user"):
        return False
    return True

@router.get("/admin/{page}", response_class=HTMLResponse)
def admin_page(request: Request, page: str, db: Session = Depends(get_db)):
    if not check_session(request):
        return RedirectResponse("/admin/login", status_code=303)
        
    data = {}
    if page == "opportunities":
        data = crud.get_opportunities(db, skip=0, limit=50)
    elif page == "regions":
        data = crud.get_region_hints(db)
    elif page == "sources":
        data = crud.get_scrape_sources(db)
    elif page == "import-logs":
        data = db.query(models.ImportLog).order_by(models.ImportLog.id.desc()).limit(50).all()
        
    return templates.TemplateResponse(f"admin/{page}.html", {"request": request, "data": data, "page": page})
