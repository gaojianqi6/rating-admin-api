import os
from fastapi import APIRouter, Depends, HTTPException
from app.core.security import oauth2_scheme
from jose import jwt, JWTError
from sqlmodel import select
from sqlalchemy import func
from sqlalchemy.orm import joinedload
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

    # Eagerly load the role relationship for the current user
    query = select(AdminUser).where(AdminUser.username == username).options(joinedload(AdminUser.role))
    result = session.execute(query)
    user = result.scalar_one_or_none()

    if user is None:
        raise HTTPException(status_code=401, detail="User not found")

    return user


@router.get("/me", summary="Get current user with roleName and updatedByName")
async def read_users_me(current_user: AdminUser = Depends(get_current_user), session=Depends(get_session)):
    # Load updater if available (using updated_by field)
    updater = None
    if current_user.updated_by:
        updater = session.get(AdminUser, current_user.updated_by)

    # Convert the user model to a dictionary with alias (camelCase) fields
    user_data = current_user.dict(by_alias=True)
    user_data["roleName"] = current_user.role.name if current_user.role else None
    user_data["updatedByName"] = updater.username if updater else None

    return user_data


@router.get("/roles", summary="Get all roles")
async def get_all_roles(session=Depends(get_session)):
    query = select(AdminRole)
    result = session.execute(query)
    roles = result.scalars().all()
    return roles


@router.get("/", summary="Get users by pagination")
async def get_users_paginated(pageNo: int = 1, pageSize: int = 10, session=Depends(get_session)):
    offset = (pageNo - 1) * pageSize

    # Query for paginated users and eagerly load the 'role' relationship
    statement = select(AdminUser).offset(offset).limit(pageSize).options(joinedload(AdminUser.role))
    result = session.execute(statement)
    users_list = result.scalars().all()

    # Calculate the total number of users
    count_statement = select(func.count(AdminUser.id))
    total = session.execute(count_statement).scalar_one()

    # Collect all unique updated_by IDs from the user list
    updated_by_ids = {user.updated_by for user in users_list if user.updated_by is not None}
    updater_mapping = {}
    if updated_by_ids:
        statement_updater = select(AdminUser).where(AdminUser.id.in_(updated_by_ids))
        result_updater = session.execute(statement_updater)
        updaters = result_updater.scalars().all()
        updater_mapping = {u.id: u.username for u in updaters}

    # Enrich each user with roleName and updatedByName
    enriched_users = []
    for user in users_list:
        user_data = user.dict(by_alias=True)
        user_data["roleName"] = user.role.name if user.role else None
        user_data["updatedByName"] = updater_mapping.get(user.updated_by, None)
        enriched_users.append(user_data)

    return {
        "list": enriched_users,
        "pageNo": pageNo,
        "pageSize": pageSize,
        "total": total
    }