import bcrypt
import uuid
import datetime
from fastapi import Header, HTTPException, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import func
from models import Token, User
from database import get_db_session

# Срок жизни токена из задания (48 часов)
TOKEN_TTL = 60 * 60 * 48 

def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode(), salt).decode()

def check_password(password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(password.encode(), hashed_password.encode())

async def check_token(
    x_token: uuid.UUID = Header(..., alias="x-token"),
    db_session: AsyncSession = Depends(get_db_session)
) -> Token:
    expire_threshold = func.now() - datetime.timedelta(seconds=TOKEN_TTL)
    query = select(Token).where(Token.token == x_token, Token.creation_time >= expire_threshold)
    token_obj = await db_session.scalar(query)

    if token_obj is None:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    return token_obj