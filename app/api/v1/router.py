
from fastapi import APIRouter

from app.api.v1.auth import router as auth_router
from app.api.v1.users import router as users_router

api_router = APIRouter()

api_router.include_router(auth_router)
api_router.include_router(users_router)


@api_router.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "application": "Inihome Backend",
        "version": "1.0.0"
    }
