# app/models/item_statistics.py
from sqlmodel import Field, Relationship
from typing import Optional
from datetime import datetime
from app.lib.model_base import CamelModel


class ItemStatistics(CamelModel, table=True):
    __tablename__ = "item_statistics"

    item_id: int = Field(foreign_key="items.id", primary_key=True)
    avg_rating: float = Field(default=0)
    ratings_count: int = Field(default=0)
    views_count: int = Field(default=0)
    last_calculated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    item: Optional["Item"] = Relationship(back_populates="statistics")