from sqlmodel import Field, Relationship
from typing import Optional, List
from datetime import datetime
from app.lib.model_base import CamelModel


class Template(CamelModel, table=True):
    __tablename__ = "templates"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(max_length=50, unique=True)
    display_name: str = Field(max_length=100)
    description: str
    full_marks: int = Field(default=10)
    is_published: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: Optional[int] = Field(default=None, foreign_key="admin_user.id")
    updated_by: Optional[int] = Field(default=None, foreign_key="admin_user.id")

    # Relationships
    fields: List["TemplateField"] = Relationship(back_populates="template")
    creator: Optional["AdminUser"] = Relationship(
        sa_relationship_kwargs={"foreign_keys": "Template.created_by",
                                "primaryjoin": "Template.created_by == AdminUser.id"}
    )
    updater: Optional["AdminUser"] = Relationship(
        sa_relationship_kwargs={"foreign_keys": "Template.updated_by",
                                "primaryjoin": "Template.updated_by == AdminUser.id"}
    )