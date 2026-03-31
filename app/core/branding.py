from sqlalchemy.orm import Session
from app.db.models import WhitelabelSettings

class BrandingSettings:
    def __init__(self, brand_name="Periodiek Systeembeheer", logo_url="/static/img/logo.png", 
                 primary_color="#3498db", secondary_color="#2c3e50"):
        self.brand_name = brand_name
        self.logo_url = logo_url
        self.primary_color = primary_color
        self.secondary_color = secondary_color

def get_branding_settings(db: Session):
    branding = db.query(WhitelabelSettings).first()
    if not branding:
        return BrandingSettings()
    return branding
