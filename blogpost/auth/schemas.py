from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr


class UserBase(BaseModel):
    full_name: str
    email: EmailStr
    username: str
    password: str


class UserResponse(BaseModel):
    id: int
    full_name: str
    email: EmailStr
    username: str
    is_active: bool
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


class LoginResponse(BaseModel):
    token_type: str
    access_token: str
    refresh_token: str
    model_config = ConfigDict(from_attributes=True)
