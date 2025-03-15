from fastapi import APIRouter
from app.api.v1.endpoints import auth, users, test

router = APIRouter()
router.include_router(auth.router)
router.include_router(users.router)
router.include_router(test.router)