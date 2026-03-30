from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_KEY: str
    JWT_SECRET: str
    ADMIN_PASSWORD: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440
    
    class Config:
        env_file = ".env"

settings = Settings()
