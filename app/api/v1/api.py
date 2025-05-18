from fastapi import APIRouter
from app.api.v1.endpoints import auth, users, test, data_sources, templates, items, statistics

router = APIRouter()
router.include_router(auth.router)
router.include_router(users.router)
router.include_router(test.router)
router.include_router(data_sources.router)
router.include_router(templates.router)
router.include_router(items.router)
router.include_router(statistics.router)