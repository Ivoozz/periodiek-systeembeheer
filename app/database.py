from app.db.session import engine, SessionLocal, Base, get_db

# Voor backward compatibility
SQLALCHEMY_DATABASE_URL = "sqlite:///./systeembeheer.db"
