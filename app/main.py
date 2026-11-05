from fastapi import FastAPI
from app.core.config import settings
from app.api.v1.router import api_router

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Backend API for Inihome 3D House Design Platform"
)

@app.get("/")
async def root():
    return {
        "message": "Welcome to Inihome API",
        "status": "running"
    }

app.include_router(
    api_router,
    prefix=settings.API_V1_PREFIX
)