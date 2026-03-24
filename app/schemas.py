# app/schemas.py
from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import Optional

class IdResponse(BaseModel):
    id: int

class StatusResponse(BaseModel):
    status: str

class CreateUserRequest(BaseModel):
    username: str
    password: str
    role: str = "user"

class LoginRequest(BaseModel):
    username: str
    password: str

class LoginResponse(BaseModel):
    id: int
    token: UUID

class AdCreate(BaseModel):
    title: str
    description: str
    price: float

class AdUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None

class AdResponse(BaseModel):
    id: int
    title: str
    description: str
    price: float
    user_id: int
    created_at: datetime

    class Config:
        from_attributes = True