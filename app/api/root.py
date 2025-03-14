from fastapi import APIRouter

router = APIRouter()

@router.get("/", tags=["Root"])
async def read_root():
    return {"ratingAdminAPIVersion": "0.0.1"}