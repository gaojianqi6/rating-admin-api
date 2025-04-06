# app/models/item_field_value.py
from sqlmodel import Field, Relationship
from typing import Optional, Any, Dict
from datetime import datetime, date
from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import JSONB
from app.lib.model_base import CamelModel


class ItemFieldValue(CamelModel, table=True):
    __tablename__ = "item_field_values"

    id: Optional[int] = Field(default=None, primary_key=True)
    item_id: int = Field(foreign_key="items.id")
    field_id: int = Field(foreign_key="template_fields.id")
    text_value: Optional[str] = None
    numeric_value: Optional[float] = None
    date_value: Optional[date] = None
    boolean_value: Optional[bool] = None
    json_value: Optional[Dict[str, Any]] = Field(
        default=None,
        sa_column=Column(JSONB, nullable=True)
    )
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    item: Optional["Item"] = Relationship(back_populates="field_values")
    field: Optional["TemplateField"] = Relationship()