
from pydantic import BaseModel, EmailStr, Field


# Login request
class LoginSchema(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)


# Authentication response
class TokenSchema(BaseModel):
    access_token: str
    token_type: str = "bearer"
