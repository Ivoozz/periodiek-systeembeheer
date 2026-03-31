from sqlalchemy.orm import Session
from app.db.database import SessionLocal, engine, Base
from app.db.models import User
from app.core.auth import get_password_hash

def seed_db():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    
    # Check if admin already exists
    admin = db.query(User).filter(User.username == "beheerder").first()
    if not admin:
        print(">>> Creating default admin: beheerder / Welkom01!")
        admin = User(
            username="beheerder",
            password_hash=get_password_hash("Welkom01!"),
            role="Admin",
            is_active=True
        )
        db.add(admin)
        db.commit()
    else:
        print(">>> Admin user already exists.")
    
    db.close()

if __name__ == "__main__":
    seed_db()
