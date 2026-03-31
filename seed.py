from sqlalchemy.orm import Session
from app.db.database import SessionLocal, engine, Base
from app.db.models import User
from app.db.models import User, ChecklistTemplate, Category, Checkpoint

def seed_db():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    # 1. Admin User
    admin = db.query(User).filter(User.username == "beheerder").first()
    if not admin:
        print(">>> Creating default admin: beheerder")
        admin = User(
            username="beheerder",
            password_hash=get_password_hash("Welkom01!"),
            role="Admin",
            is_active=True
        )
        db.add(admin)
        db.commit()

    # 2. Default Checklist Template
    template = db.query(ChecklistTemplate).first()
    if not template:
        print(">>> Creating default template: Standaard Systeembeheer")
        template = ChecklistTemplate(name="Standaard Systeembeheer", description="Maandelijkse controle")
        db.add(template)
        db.commit()
        db.refresh(template)

        # Categories
        cat1 = Category(template_id=template.id, name="Server Status", order=1)
        cat2 = Category(template_id=template.id, name="Backup & Security", order=2)
        db.add_all([cat1, cat2])
        db.commit()

        # Checkpoints
        cp1 = Checkpoint(category_id=cat1.id, name="Diskruimte", description="Controleer beschikbare ruimte")
        cp2 = Checkpoint(category_id=cat1.id, name="Systeem Updates", description="Check voor OS updates")
        cp3 = Checkpoint(category_id=cat2.id, name="Backups", description="Controleer laatste backup succes")
        cp4 = Checkpoint(category_id=cat2.id, name="Antivirus", description="Updates en scans controleren")
        db.add_all([cp1, cp2, cp3, cp4])
        db.commit()

    db.close()


if __name__ == "__main__":
    seed_db()
