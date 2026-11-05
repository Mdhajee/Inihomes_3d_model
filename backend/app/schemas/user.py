from pydantic import BaseModel, EmailStr


class UserResponse(BaseModel):
    id: str
    full_name: str
    email: EmailStr