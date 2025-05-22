import os
from fastapi import APIRouter, Depends, HTTPException, status
from app.core.security import oauth2_scheme, hash_password
from jose import jwt, JWTError
from sqlmodel import select
from sqlalchemy import func
from sqlalchemy.orm import joinedload
from app.db.session import get_session
from app.models.admin_user import AdminUser
from app.models.admin_role import AdminRole
from app.schemas.user import UserCreate, UserUpdate, UserResponse
from datetime import datetime

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

async def check_is_administrator(current_user: AdminUser = Depends(get_current_user)):
    """Check if the current user has Administrator role"""
    if not current_user.role or current_user.role.name != "Administrator":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can perform this action"
        )
    return current_user

@router.get("/me", response_model=UserResponse)
async def read_users_me(current_user: AdminUser = Depends(get_current_user), session=Depends(get_session)):
    # Load updater if available (using updated_by field)
    updater = None
    if current_user.updated_by:
        updater = session.get(AdminUser, current_user.updated_by)

    return {
        "id": current_user.id,
        "username": current_user.username,
        "email": current_user.email,
        "roleId": current_user.role_id,
        "roleName": current_user.role.name if current_user.role else None,
        "createdTime": current_user.created_time,
        "updatedTime": current_user.updated_time,
        "updatedBy": current_user.updated_by,
        "updatedByName": updater.username if updater else None
    }

@router.get("/roles")
async def get_all_roles(session=Depends(get_session)):
    query = select(AdminRole)
    result = session.execute(query)
    roles = result.scalars().all()
    return roles

@router.get("", summary="Get users by pagination")
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
        enriched_users.append({
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "roleId": user.role_id,
            "roleName": user.role.name if user.role else None,
            "createdTime": user.created_time,
            "updatedTime": user.updated_time,
            "updatedBy": user.updated_by,
            "updatedByName": updater_mapping.get(user.updated_by, None)
        })

    return {
        "list": enriched_users,
        "pageNo": pageNo,
        "pageSize": pageSize,
        "total": total
    }

@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_data: UserCreate,
    session=Depends(get_session),
    current_user: AdminUser = Depends(check_is_administrator)
):
    """Create a new admin user"""
    # Check if username already exists
    existing_user = session.exec(
        select(AdminUser).where(AdminUser.username == user_data.username)
    ).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )

    # Check if email already exists
    existing_email = session.exec(
        select(AdminUser).where(AdminUser.email == user_data.email)
    ).first()
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Check if role exists
    role = session.get(AdminRole, user_data.roleId)
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role not found"
        )

    # Create new user
    db_user = AdminUser(
        username=user_data.username,
        email=user_data.email,
        password=hash_password(user_data.password),
        role_id=user_data.roleId,
        updated_by=current_user.id
    )
    
    session.add(db_user)
    session.commit()
    session.refresh(db_user)

    return {
        "id": db_user.id,
        "username": db_user.username,
        "email": db_user.email,
        "roleId": db_user.role_id,
        "roleName": role.name,
        "createdTime": db_user.created_time,
        "updatedTime": db_user.updated_time,
        "updatedBy": db_user.updated_by,
        "updatedByName": current_user.username
    }

@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_data: UserUpdate,
    session=Depends(get_session),
    current_user: AdminUser = Depends(check_is_administrator)
):
    """Update an existing admin user"""
    # Get the user to update
    db_user = session.get(AdminUser, user_id)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Check username uniqueness if being updated
    if user_data.username and user_data.username != db_user.username:
        existing_user = session.exec(
            select(AdminUser).where(AdminUser.username == user_data.username)
        ).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken"
            )
        db_user.username = user_data.username

    # Check email uniqueness if being updated
    if user_data.email and user_data.email != db_user.email:
        existing_email = session.exec(
            select(AdminUser).where(AdminUser.email == user_data.email)
        ).first()
        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        db_user.email = user_data.email

    # Update password if provided
    if user_data.password:
        db_user.password = hash_password(user_data.password)

    # Update role if provided
    role = None
    if user_data.roleId:
        role = session.get(AdminRole, user_data.roleId)
        if not role:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Role not found"
            )
        db_user.role_id = user_data.roleId

    # Update metadata
    db_user.updated_time = datetime.utcnow()
    db_user.updated_by = current_user.id

    session.add(db_user)
    session.commit()
    session.refresh(db_user)

    # Get role name if not loaded
    if not role and db_user.role_id:
        role = session.get(AdminRole, db_user.role_id)

    return {
        "id": db_user.id,
        "username": db_user.username,
        "email": db_user.email,
        "roleId": db_user.role_id,
        "roleName": role.name if role else None,
        "createdTime": db_user.created_time,
        "updatedTime": db_user.updated_time,
        "updatedBy": db_user.updated_by,
        "updatedByName": current_user.username
    }

@router.delete("/{user_id}")
async def delete_user(
    user_id: int,
    session=Depends(get_session),
    current_user: AdminUser = Depends(check_is_administrator)
):
    """Delete an admin user"""
    # Protect user ID 1 from deletion
    if user_id == 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete the primary administrator account"
        )

    # Get the user to delete
    db_user = session.get(AdminUser, user_id)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Delete the user
    session.delete(db_user)
    session.commit()

    return {"status": "success", "message": "User deleted successfully"}