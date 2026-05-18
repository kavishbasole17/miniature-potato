from fastapi import Request, Depends, HTTPException, status
from fastapi.security import APIKeyHeader
import config, crud
from database import get_db
from sqlalchemy.orm import Session
import hashlib

def verify_password(plain_password, hashed_password):
    # simplistic approach for demo, PBKDF2 would be better
    return hashlib.sha256(plain_password.encode()).hexdigest() == hashed_password

def get_password_hash(password):
    return hashlib.sha256(password.encode()).hexdigest()

def check_admin_auth(request: Request, db: Session = Depends(get_db)):
    if not config.ADMIN_PASSWORD:
        return True # Auth disabled
    
    # Check session cookie
    session_user = request.cookies.get("session_user")
    if session_user:
        return True
    
    # Check headers
    x_admin_username = request.headers.get("X-Admin-Username")
    x_admin_password = request.headers.get("X-Admin-Password")
    
    if x_admin_username and x_admin_password:
        # Check team user first
        user = crud.get_user_by_username(db, x_admin_username)
        if user and user.is_active and verify_password(x_admin_password, user.password_hash):
            return True
        
        # Check master
        if x_admin_username.lower() == config.ADMIN_USERNAME.lower() and x_admin_password == config.ADMIN_PASSWORD:
            return True

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Unauthorized",
    )
