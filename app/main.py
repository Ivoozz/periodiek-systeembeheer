from fastapi import FastAPI, Depends, HTTPException, status, Response, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
from app.database import engine, Base, get_db
from app import models, auth, schemas
from app.routers import customers, reports
from app.web import dashboard
from app.api.v1 import external

# Ensure tables exist
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Systeembeheer API")
templates = Jinja2Templates(directory="app/templates")

app.include_router(customers.router)
app.include_router(reports.router)
app.include_router(dashboard.router)
app.include_router(external.router)

@app.get("/", response_class=HTMLResponse)
def index(request: Request, user: models.User = Depends(auth.get_current_user)):
    if not user:
        return RedirectResponse(url="/login", status_code=302)
    if user.role == "Behandelaar":
        return RedirectResponse(url="/admin", status_code=302)
    elif user.role == "Klant":
        return RedirectResponse(url="/klant", status_code=302)
    else:
        return RedirectResponse(url="/login", status_code=302)

@app.get("/klant", response_class=HTMLResponse)
def klant_dashboard(request: Request, user: models.User = Depends(auth.get_current_user)):
    if not user or user.role != "Klant":
        return RedirectResponse(url="/login", status_code=302)
    return templates.TemplateResponse("klant/dashboard.html", {"request": request, "user": user})

@app.get("/login", response_class=HTMLResponse)
def login_get(request: Request, user: models.User = Depends(auth.get_current_user)):
    if user:
        return RedirectResponse(url="/")
    return templates.TemplateResponse("login.html", {"request": request, "user": None})

@app.post("/login")
def login_post(response: Response, username: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.username == username).first()
    if not user or not auth.verify_password(password, user.password_hash):
        return RedirectResponse(url="/login?error=1", status_code=302)
    
    access_token = auth.create_access_token(data={"sub": user.username, "role": user.role})
    resp = RedirectResponse(url="/", status_code=302)
    resp.set_cookie(
        key="access_token", 
        value=f"Bearer {access_token}", 
        httponly=True, 
        samesite="lax",
        max_age=1440 * 60
    )
    return resp

@app.get("/logout")
def logout(response: Response):
    resp = RedirectResponse(url="/login", status_code=302)
    resp.delete_cookie("access_token")
    return resp

@app.get("/admin", response_class=HTMLResponse)
def admin_dashboard(request: Request, user: models.User = Depends(auth.require_behandelaar)):
    return templates.TemplateResponse("admin/dashboard.html", {"request": request, "user": user})

@app.get("/admin/checklist/{customer_id}", response_class=HTMLResponse)
def admin_checklist(request: Request, customer_id: int, user: models.User = Depends(auth.require_behandelaar)):
    return templates.TemplateResponse("admin/checklist.html", {"request": request, "user": user, "customer_id": customer_id})

@app.get("/api/health")
def health_check():
    return {"status": "ok", "message": "Systeembeheer Backend is operationeel"}

@app.post("/api/login")
def login(login_data: schemas.LoginRequest, response: Response, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.username == login_data.username).first()
    if not user or not auth.verify_password(login_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Ongeldige gebruikersnaam of wachtwoord",
        )
    
    access_token = auth.create_access_token(data={"sub": user.username, "role": user.role})
    response.set_cookie(
        key="access_token", 
        value=f"Bearer {access_token}", 
        httponly=True, 
        samesite="lax",
        max_age=1440 * 60 # 24 hours in seconds
    )
    return {"status": "success", "user": {"username": user.username, "role": user.role}}

@app.post("/api/logout")
def logout(response: Response):
    response.delete_cookie("access_token")
    return {"status": "success", "message": "Uitgelogd"}

@app.get("/api/me")
def get_me(user: models.User = Depends(auth.get_current_user)):
    if not user:
        raise HTTPException(status_code=401, detail="Niet ingelogd")
    return {"username": user.username, "role": user.role}
