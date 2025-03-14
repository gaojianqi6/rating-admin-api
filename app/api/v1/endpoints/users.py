import os
from fastapi import APIRouter, Depends
from app.core.security import oauth2_scheme
from jose import jwt, JWTError
from app.models.admin_user import AdminUser
from sqlmodel import select
from app.db.session import get_session
from fastapi import HTTPException, status

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
