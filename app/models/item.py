# app/models/item.py
from sqlmodel import Field, Relationship
from typing import Optional, List
from datetime import datetime
from app.lib.model_base import CamelModel


class Item(CamelModel, table=True):
    __tablename__ = "items"

    id: Optional[int] = Field(default=None, primary_key=True)
    template_id: int = Field(foreign_key="templates.id")
    title: str = Field(max_length=200)
    slug: str = Field(max_length=255, unique=True)
    created_by: int = Field(foreign_key="user.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    template: Optional["Template"] = Relationship()
    field_values: List["ItemFieldValue"] = Relationship(back_populates="item")
    statistics: Optional["ItemStatistics"] = Relationship(back_populates="item")
    ratings: List["UserRating"] = Relationship(back_populates="item")