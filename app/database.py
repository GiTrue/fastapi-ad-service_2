# app/database.py
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase
from config import settings

# Создаем асинхронный движок, используя URL из конфига
engine = create_async_engine(settings.DATABASE_URL)

# Фабрика сессий
Session = async_sessionmaker(
    bind=engine, 
    class_=AsyncSession, 
    expire_on_commit=False
)

# Базовый класс для моделей
class Base(DeclarativeBase):
    pass

# Зависимость для FastAPI (Dependency Injection)
async def get_db_session():
    async with Session() as session:
        yield session