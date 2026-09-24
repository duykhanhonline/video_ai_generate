from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field

UserRole = Literal["reviewer", "contributor"]


class UserRegister(BaseModel):
    email: EmailStr
    name: str = Field(min_length=1, max_length=255)
    password: str = Field(min_length=8)
    role: UserRole = "contributor"


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: str
    name: str | None
    role: UserRole
    created_at: datetime


class LoginResponse(BaseModel):
    access_token: str
    user: UserRead
