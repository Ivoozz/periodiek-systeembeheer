from fastapi.templating import Jinja2Templates
from app.db.database import SessionLocal
from app.core.branding import get_branding_settings

def branding_context_processor(request):
    db = SessionLocal()
    try:
        branding = get_branding_settings(db)
        return {"branding": branding}
    finally:
        db.close()

templates = Jinja2Templates(directory="app/templates", context_processors=[branding_context_processor])
