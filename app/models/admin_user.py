from sqlmodel import SQLModel, Field, Relationship
from typing import Optional
from datetime import datetime

class AdminUser(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(max_length=50, unique=True)
    password: str = Field(max_length=255)
    role_id: int = Field(foreign_key="adminrole.id")
    created_time: datetime = Field(default_factory=datetime.utcnow)
    updated_time: datetime = Field(default_factory=datetime.utcnow)
    updated_by: Optional[int] = Field(default=None, foreign_key="adminuser.id")

    role: Optional["AdminRole"] = Relationship(back_populates="users")
