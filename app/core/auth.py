import os
from datetime import datetime, timedelta
from typing import Optional, Annotated
from fastapi import Request, Depends, HTTPException, status
from fastapi.security import APIKeyCookie
from passlib.context import CryptContext
from itsdangerous import URLSafeSerializer, BadSignature
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.models import User

# Configuration
SECRET_KEY = os.getenv("SECRET_KEY", "super-secret-key-change-it-in-production")
SESSION_COOKIE_NAME = "session"
ALGORITHM = "HS256"

# Password Hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Session Serializer
serializer = URLSafeSerializer(SECRET_KEY)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_session_cookie(user_id: int) -> str:
    return serializer.dumps({"user_id": user_id})

def get_user_id_from_session(token: str) -> Optional[int]:
    try:
        data = serializer.loads(token)
        return data.get("user_id")
    except BadSignature:
        return None

# Dependency to get current user from cookie
async def get_current_user(request: Request, db: Session = Depends(get_db)) -> Optional[User]:
    session_token = request.cookies.get(SESSION_COOKIE_NAME)
    if not session_token:
        return None
    
    user_id = get_user_id_from_session(session_token)
    if user_id is None:
        return None
        
    user = db.query(User).filter(User.id == user_id).first()
    return user

async def get_current_user_required(user: Annotated[Optional[User], Depends(get_current_user)]) -> User:
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Cookie"},
        )
    return user
