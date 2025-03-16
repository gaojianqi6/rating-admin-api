from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import select
from app.db.session import get_session
from app.models.admin_user import AdminUser
from app.core.security import verify_password, create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES
from datetime import timedelta

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends(), session=Depends(get_session)):
    query = select(AdminUser).where(AdminUser.username == form_data.username)
    result = session.execute(query)
    user = result.scalar_one_or_none()

    if user is None or not verify_password(form_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": user.username}, expires_delta=access_token_expires)

    return {"accessToken": access_token, "tokenType": "bearer"}
