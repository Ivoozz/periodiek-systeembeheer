from fastapi import Depends, Request, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from app.database import get_db
from app.models import User

SECRET_KEY = "GEHEIM_Sleutel_Voor_Systeembeheer_Verander_Dit_In_Productie!"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 1440

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def get_current_user(request: Request, db: Session = Depends(get_db)):
    token = request.cookies.get("access_token")
    if not token:
        return None
    
    try:
        # Support both "Bearer <token>" and just "<token>" in the cookie
        if token.startswith("Bearer "):
            token = token[7:]
            
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            return None
    except JWTError:
        return None
        
    user = db.query(User).filter(User.username == username).first()
    return user

def require_behandelaar(user: User = Depends(get_current_user)):
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Niet ingelogd",
        )
    if user.role != "Behandelaar":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Onvoldoende rechten (Behandelaar vereist)",
        )
    return user

def require_klant(user: User = Depends(get_current_user)):
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Niet ingelogd",
        )
    if user.role != "Klant":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Onvoldoende rechten (Klant vereist)",
        )
    return user
