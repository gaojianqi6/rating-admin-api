from sqlmodel import Field, Relationship
from typing import Optional, Dict, Any
from datetime import datetime
from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import JSONB
from app.lib.model_base import CamelModel


class TemplateField(CamelModel, table=True):
    __tablename__ = "template_fields"

    id: Optional[int] = Field(default=None, primary_key=True)
    template_id: int = Field(foreign_key="templates.id")
    name: str = Field(max_length=50)
    display_name: str = Field(max_length=100)
    description: Optional[str] = None
    field_type: str = Field(max_length=30)
    is_required: bool = Field(default=False)
    is_searchable: bool = Field(default=False)
    is_filterable: bool = Field(default=False)
    display_order: int
    data_source_id: Optional[int] = Field(default=None, foreign_key="field_data_sources.id")

    # Use SQLAlchemy's Column directly for the JSONB field
    validation_rules: Optional[Dict[str, Any]] = Field(
        default=None,
        sa_column=Column(JSONB, nullable=True)
    )

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    template: Optional["Template"] = Relationship(back_populates="fields")
    data_source: Optional["FieldDataSource"] = Relationship(back_populates="fields")