# app/main.py
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

import models, schemas
from database import engine, Base, get_db_session
from auth import hash_password, check_password, check_token, check_access

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()

app = FastAPI(title="Ad Service", lifespan=lifespan)

@app.post("/user", response_model=schemas.IdResponse)
async def create_user(user_data: schemas.CreateUserRequest, db: AsyncSession = Depends(get_db_session)):
    new_user = models.User(
        username=user_data.username,
        password=hash_password(user_data.password),
        role=user_data.role
    )
    db.add(new_user)
    try:
        await db.commit()
    except Exception:
        raise HTTPException(status_code=400, detail="User already exists")
    await db.refresh(new_user)
    return {"id": new_user.id}

@app.post("/login", response_model=schemas.LoginResponse)
async def login(login_data: schemas.LoginRequest, db: AsyncSession = Depends(get_db_session)):
    query = select(models.User).where(models.User.username == login_data.username)
    user = await db.scalar(query)
    
    if user is None or not check_password(login_data.password, user.password):
        raise HTTPException(status_code=401, detail="Wrong login/pass")
    
    new_token = models.Token(user_id=user.id)
    db.add(new_token)
    await db.commit()
    await db.refresh(new_token)
    return {"id": user.id, "token": new_token.token}

@app.post("/advertisement", response_model=schemas.IdResponse)
async def create_ad(
    data: schemas.AdCreate, 
    token: models.Token = Depends(check_token), 
    db: AsyncSession = Depends(get_db_session)
):
    new_ad = models.Advertisement(**data.model_dump(), user_id=token.user_id)
    db.add(new_ad)
    await db.commit()
    await db.refresh(new_ad)
    return {"id": new_ad.id}

@app.get("/advertisement/{ad_id}", response_model=schemas.AdResponse)
async def get_ad(ad_id: int, db: AsyncSession = Depends(get_db_session)):
    ad = await db.get(models.Advertisement, ad_id)
    if not ad:
        raise HTTPException(status_code=404, detail="Ad not found")
    return ad

@app.patch("/advertisement/{ad_id}", response_model=schemas.IdResponse)
async def update_ad(
    ad_id: int, 
    data: schemas.AdUpdate, 
    token: models.Token = Depends(check_token), 
    db: AsyncSession = Depends(get_db_session)
):
    ad = await db.get(models.Advertisement, ad_id)
    if not ad:
        raise HTTPException(status_code=404, detail="Ad not found")
    
    # ПРОВЕРКА ПРАВ
    check_access(token.user, ad)
    
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(ad, key, value)
    
    await db.commit()
    return {"id": ad.id}

@app.delete("/advertisement/{ad_id}", response_model=schemas.StatusResponse)
async def delete_ad(
    ad_id: int, 
    token: models.Token = Depends(check_token), 
    db: AsyncSession = Depends(get_db_session)
):
    ad = await db.get(models.Advertisement, ad_id)
    if not ad:
        raise HTTPException(status_code=404, detail="Ad not found")
    
    # ПРОВЕРКА ПРАВ
    check_access(token.user, ad)
    
    await db.delete(ad)
    await db.commit()
    return {"status": "deleted"}