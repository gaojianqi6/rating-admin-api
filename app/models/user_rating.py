# app/models/user_rating.py
from sqlmodel import Field, Relationship
from typing import Optional
from datetime import datetime
from app.lib.model_base import CamelModel


class UserRating(CamelModel, table=True):
    __tablename__ = "user_ratings"

    id: Optional[int] = Field(default=None, primary_key=True)
    item_id: int = Field(foreign_key="items.id")
    user_id: int = Field(foreign_key="user.id")
    rating: float
    review_text: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    item: Optional["Item"] = Relationship(back_populates="ratings")
    user: Optional["User"] = Relationship(back_populates="ratings")