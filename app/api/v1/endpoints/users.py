import os
from fastapi import APIRouter, Depends, HTTPException
from app.core.security import oauth2_scheme
from jose import jwt, JWTError
from sqlmodel import select
from sqlalchemy import func
from app.db.session import get_session
from app.models.admin_user import AdminUser
from app.models.admin_role import AdminRole

SECRET_KEY = os.getenv("ADMIN_JWT_SECRET", "admin_default_secret_key")
router = APIRouter(prefix="/users", tags=["users"])

async def get_current_user(token: str = Depends(oauth2_scheme), session=Depends(get_session)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid credentials")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    query = select(AdminUser).where(AdminUser.username == username)
    result = session.execute(query)
    user = result.scalar_one_or_none()

    if user is None:
        raise HTTPException(status_code=401, detail="User not found")

    return user

@router.get("/me")
async def read_users_me(current_user: AdminUser = Depends(get_current_user)):
    return current_user

@router.get("/roles", summary="Get all roles")
async def get_all_roles(session=Depends(get_session)):
    query = select(AdminRole)
    result = session.execute(query)
    roles = result.scalars().all()
    return roles


@router.get("/", summary="Get users by pagination")
async def get_users_paginated(pageNo: int = 1, pageSize: int = 10, session=Depends(get_session)):
    offset = (pageNo - 1) * pageSize
    statement = select(AdminUser).offset(offset).limit(pageSize)
    result = session.execute(statement)
    users_list = result.scalars().all()

    # Calculate total count
    count_statement = select(func.count(AdminUser.id))
    total = session.execute(count_statement).scalar_one()

    return {
        "list": users_list,
        "pageNo": pageNo,
        "pageSize": pageSize,
        "total": total
    }