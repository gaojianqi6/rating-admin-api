# app/models/user.py
from sqlmodel import Field, Relationship
from typing import Optional, List
from datetime import datetime
from app.lib.model_base import CamelModel


class User(CamelModel, table=True):
    __tablename__ = "user"

    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(max_length=50, unique=True)
    nickname: Optional[str] = Field(max_length=50, default=None)
    email: str = Field(max_length=100, unique=True)
    password: str = Field(max_length=255)
    avatar: Optional[str] = Field(max_length=255, default=None)
    description: Optional[str] = Field(max_length=500, default=None)
    country: Optional[str] = Field(max_length=50, default=None)
    created_time: datetime = Field(default_factory=datetime.utcnow)
    updated_time: datetime = Field(default_factory=datetime.utcnow)
    google_id: Optional[str] = Field(default=None, unique=True)
    logged_in_at: Optional[datetime] = Field(default=None)

    # Relationships
    ratings: List["UserRating"] = Relationship(back_populates="user")