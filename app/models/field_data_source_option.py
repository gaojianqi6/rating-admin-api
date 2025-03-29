from sqlmodel import Field, Relationship
from typing import Optional
from datetime import datetime
from app.lib.model_base import CamelModel


class FieldDataSourceOption(CamelModel, table=True):
    __tablename__ = "field_data_source_options"

    id: Optional[int] = Field(default=None, primary_key=True)
    data_source_id: int = Field(foreign_key="field_data_sources.id")
    value: str = Field(max_length=200)
    display_text: str = Field(max_length=200)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    data_source: Optional["FieldDataSource"] = Relationship(back_populates="options")
