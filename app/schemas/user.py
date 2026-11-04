
from pydantic import BaseModel, Field, EmailStr


# User registration details
class UserCreateSchema(BaseModel):
    name: str = Field(min_length=2)
    email: EmailStr
    password: str = Field(min_length=8)


# User response details
class UserResponseSchema(BaseModel):
    user_id: str
    name: str
    email: EmailStr
