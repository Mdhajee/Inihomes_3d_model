
from fastapi import APIRouter, HTTPException, status

from app.schemas.auth import (
    RegisterRequest,
    LoginRequest,
    TokenResponse
)
from app.schemas.user import UserResponse
from app.repositories.store import user_repository
from app.core.security import (
    hash_password,
    verify_password,
    create_access_token
)

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED
)
async def register_user(user_data: RegisterRequest):

    existing_user = user_repository.get_user_by_email(
        str(user_data.email)
    )

    if existing_user:
        raise HTTPException(
            status_code=409,
            detail="Email already registered"
        )

    user = {
        "full_name": user_data.full_name,
        "email": str(user_data.email).lower(),
        "password_hash": hash_password(user_data.password)
    }

    created_user = user_repository.create_user(user)

    return created_user


@router.post(
    "/login",
    response_model=TokenResponse
)
async def login_user(login_data: LoginRequest):

    user = user_repository.get_user_by_email(
        str(login_data.email)
    )

    if not user or not verify_password(
        login_data.password,
        user["password_hash"]
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    access_token = create_access_token(user["id"])

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }
