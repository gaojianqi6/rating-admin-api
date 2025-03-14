from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List

class AdminRole(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(max_length=20, unique=True)

    users: List["AdminUser"] = Relationship(back_populates="role")
