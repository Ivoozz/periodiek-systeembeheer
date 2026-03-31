from fastapi import APIRouter, Depends, Form, Request, Response, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.models import User, Role
from app.core.auth import verify_password, create_session_cookie, SESSION_COOKIE_NAME
from app.core.security import RateLimiter

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

login_rate_limiter = RateLimiter(limit=5, window=60)

@router.get("/login", response_class=HTMLResponse, dependencies=[Depends(login_rate_limiter)])
async def login_page(request: Request, error: str = None):
    return templates.TemplateResponse("login.html", {"request": request, "error": error})

@router.post("/login", dependencies=[Depends(login_rate_limiter)])
async def login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.username == username).first()
    if not user or not verify_password(password, user.password_hash):
        return RedirectResponse(url="/login?error=1", status_code=status.HTTP_303_SEE_OTHER)
    
    # Redirect op basis van rol
    target_url = "/dashboard"
    if user.role == Role.TECHNICUS:
        target_url = "/behandelaar/dashboard"
        
    response = RedirectResponse(url=target_url, status_code=status.HTTP_303_SEE_OTHER)
    session_token = create_session_cookie(user.id)
    response.set_cookie(
        key=SESSION_COOKIE_NAME,
        value=session_token,
        httponly=True,
        secure=False, # HTTP allowed
        samesite="lax"
    )
    return response

@router.post("/logout")
async def logout():
    response = RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)
    response.delete_cookie(SESSION_COOKIE_NAME)
    return response
