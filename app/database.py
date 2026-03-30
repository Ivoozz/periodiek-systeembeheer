from app.db.session import engine, SessionLocal, Base, get_db

# Voor backward compatibility
SQLALCHEMY_DATABASE_URL = "sqlite:////var/www/systeembeheer/systeembeheer.db"
