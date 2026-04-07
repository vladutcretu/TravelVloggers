from datetime import datetime

from pydantic import BaseModel, EmailStr, Field, ConfigDict


class UserBase(BaseModel):
    email: EmailStr = Field(max_length=255)


class UserCreate(UserBase):
    password: str = Field(min_length=6)


class UserCreateResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: EmailStr
    is_superuser: bool = Field(default=False)


class UserLogin(UserCreate):
    pass


class UserLoginResponse(BaseModel):
    access_token: str
    token_type: str


class UserPrivateResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: EmailStr
    is_admin: bool
    is_superuser: bool


class UserPublicResponse(UserPrivateResponse):
    created_at: datetime


class UserUpdate(BaseModel):
    is_admin: bool = Field(default=False)
