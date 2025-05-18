from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime
from app.lib.model_base import APIBaseModel

class UserBase(APIBaseModel):
    username: str
    email: EmailStr
    roleId: int  # This will be converted to role_id in the model
    password: str

class UserCreate(UserBase):
    pass

class UserUpdate(APIBaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    roleId: Optional[int] = None  # This will be converted to role_id in the model
    password: Optional[str] = None

class UserResponse(APIBaseModel):
    id: int
    username: str
    email: str
    roleId: int
    roleName: Optional[str] = None
    createdTime: datetime
    updatedTime: datetime
    updatedBy: Optional[int] = None
    updatedByName: Optional[str] = None 