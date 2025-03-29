from sqlmodel import Field, Relationship, SQLModel
from typing import Optional, List, Dict, Any
from datetime import datetime
from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import JSONB
from app.lib.model_base import CamelModel


class FieldDataSource(CamelModel, table=True):
    __tablename__ = "field_data_sources"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(max_length=100, unique=True)
    source_type: str = Field(max_length=30)  # static_list, range, api, dynamic

    # Use SQLAlchemy's Column directly for the JSONB field
    configuration: Optional[Dict[str, Any]] = Field(
        default=None,
        sa_column=Column(JSONB, nullable=True)
    )

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: Optional[int] = Field(default=None, foreign_key="admin_user.id")

    # Relationships
    options: List["FieldDataSourceOption"] = Relationship(back_populates="data_source")
    fields: List["TemplateField"] = Relationship(back_populates="data_source")