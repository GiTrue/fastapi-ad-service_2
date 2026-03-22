# app/models.py
import uuid
import datetime
from sqlalchemy import String, ForeignKey, Uuid, DateTime, Float, Column
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from database import Base

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(100), nullable=False)
    role: Mapped[str] = mapped_column(String(20), default="user") # 'user' или 'admin'

    tokens: Mapped[list["Token"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    ads: Mapped[list["Advertisement"]] = relationship(back_populates="owner", cascade="all, delete-orphan")

class Token(Base):
    __tablename__ = "token"
    id: Mapped[int] = mapped_column(primary_key=True)
    token: Mapped[uuid.UUID] = mapped_column(Uuid, server_default=func.gen_random_uuid(), unique=True)
    creation_time: Mapped[datetime.datetime] = mapped_column(DateTime, server_default=func.now())
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))

    user: Mapped[User] = relationship(back_populates="tokens")

class Advertisement(Base):
    __tablename__ = "advertisement"
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(100))
    description: Mapped[str] = mapped_column(String(1000))
    price: Mapped[float] = mapped_column(Float)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, server_default=func.now())
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))

    owner: Mapped[User] = relationship(back_populates="ads")

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "price": self.price,
            "author": self.owner.username if self.owner else "Unknown",
            "created_at": self.created_at.isoformat()
        }