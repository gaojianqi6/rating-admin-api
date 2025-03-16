from sqlmodel import Field, Relationship
from typing import Optional, TYPE_CHECKING
from datetime import datetime
from app.lib.model_base import CamelModel

if TYPE_CHECKING:
    from app.models.admin_role import AdminRole

class AdminUser(CamelModel, table=True):
    __tablename__ = "admin_user"
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(max_length=50, unique=True)
    email: str = Field(max_length=100, unique=True)
    password: str = Field(max_length=255)
    role_id: int = Field(foreign_key="admin_role.id")
    created_time: datetime = Field(default_factory=datetime.utcnow)
    updated_time: datetime = Field(default_factory=datetime.utcnow)
    updated_by: Optional[int] = Field(default=None, foreign_key="admin_user.id")

    # Use the simple class name in the string for the relationship
    role: Optional["AdminRole"] = Relationship(back_populates="users")


# Import AdminRole at runtime to ensure it is registered before mapping completes

from app.models.admin_role import AdminRole  # noqa: E402
AdminUser.update_forward_refs()