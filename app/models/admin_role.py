from sqlmodel import Field, Relationship
from typing import Optional, List
from app.lib.model_base import CamelModel

class AdminRole(CamelModel, table=True):
    __tablename__ = "admin_role"
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(max_length=20, unique=True)

    users: List["AdminUser"] = Relationship(back_populates="role")
