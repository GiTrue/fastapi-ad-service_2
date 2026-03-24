# app/auth.py
import bcrypt
import uuid
import datetime
from fastapi import Header, HTTPException, Depends, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import func
from models import Token, User, Advertisement
from database import get_db_session
from config import settings

def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode(), salt).decode()

def check_password(password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(password.encode(), hashed_password.encode())

async def check_token(
    x_token: uuid.UUID = Header(..., alias="x-token"),
    db_session: AsyncSession = Depends(get_db_session)
) -> Token:
    # Используем TTL из настроек
    expire_threshold = func.now() - datetime.timedelta(seconds=settings.TOKEN_TTL)
    query = select(Token).where(Token.token == x_token, Token.creation_time >= expire_threshold)
    token_obj = await db_session.scalar(query)

    if token_obj is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Невалидный токен или сессия истекла"
        )
    return token_obj

def check_access(user: User, advertisement: Advertisement):
    """
    Логика RBAC: 
    Админ может всё. Пользователь — только свои записи.
    """
    if user.role == "admin":
        return True
    if advertisement.user_id == user.id:
        return True
    
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN, 
        detail="Недостаточно прав для выполнения операции"
    )