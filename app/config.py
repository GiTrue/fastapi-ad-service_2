# app/config.py
import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Настройки базы данных (берутся из .env или дефолты)
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    POSTGRES_HOST: str = "db"
    POSTGRES_PORT: int = 5432

    # Настройки безопасности
    SECRET_KEY: str = "76SrYPwqmnv39X_L" 
    ALGORITHM: str = "HS256"
    
    # Время жизни токена (48 часов в секундах для auth.py)
    TOKEN_TTL: int = 60 * 60 * 48 

    @property
    def DATABASE_URL(self) -> str:
        return (f"postgresql+asyncpg://"
                f"{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@"
                f"{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}")

    class Config:
        env_file = ".env"
        extra = "ignore" # Игнорировать лишние переменные в .env

settings = Settings()