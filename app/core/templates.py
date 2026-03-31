from fastapi.templating import Jinja2Templates
from app.db.database import SessionLocal
from app.core.branding import get_branding_settings
import time

# Simple In-Memory Cache for Branding (SaaS Optimization)
BRANDING_CACHE = {
    "data": None,
    "last_update": 0
}
CACHE_TTL = 300  # 5 minutes

def get_cached_branding():
    now = time.time()
    if BRANDING_CACHE["data"] is None or (now - BRANDING_CACHE["last_update"]) > CACHE_TTL:
        db = SessionLocal()
        try:
            BRANDING_CACHE["data"] = get_branding_settings(db)
            BRANDING_CACHE["last_update"] = now
        finally:
            db.close()
    return BRANDING_CACHE["data"]

def branding_context_processor(request):
    # DONT open a DB session here every time! Use Cache.
    return {"branding": get_cached_branding()}

templates = Jinja2Templates(directory="app/templates", context_processors=[branding_context_processor])
