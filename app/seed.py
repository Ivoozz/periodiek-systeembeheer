from sqlalchemy.orm import Session
from app.db.session import SessionLocal, engine, Base
from app.models import User, Template, Category, Checkpoint, SystemSettings
from app.core.auth import get_password_hash
import os
from dotenv import load_dotenv

load_dotenv()

def seed_db():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    # Default Admin
    admin_user = db.query(User).filter(User.username == "beheerder").first()
    if not admin_user:
        admin_user = User(
            username="beheerder",
            password_hash=get_password_hash(os.getenv("ADMIN_PASSWORD", "Welkom01!")),
            role="Behandelaar"
        )
        db.add(admin_user)

    # Default Settings
    settings = db.query(SystemSettings).first()
    if not settings:
        settings = SystemSettings(
            header_text="Periodiek Systeembeheer",
            footer_text="© 2026 Systeembeheer"
        )
        db.add(settings)

    # Default Template
    template = db.query(Template).first()
    if not template:
        template = Template(name="Standaard Onderhoud")
        db.add(template)
        db.flush()

        # Categories
        categories = ["Backup", "Servermanagement", "Usermanagement", "Infrastructuur", "Monitoring", "Security"]
        for cat_name in categories:
            cat = Category(name=cat_name, template_id=template.id)
            db.add(cat)
            db.flush()
            
            # Add some dummy checkpoints
            cp = Checkpoint(name=f"Controle {cat_name}", category_id=cat.id)
            db.add(cp)

    db.commit()
    db.close()
    print("Database seeding voltooid.")

if __name__ == "__main__":
    seed_db()
