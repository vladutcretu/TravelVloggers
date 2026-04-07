from datetime import datetime

from pydantic import BaseModel, EmailStr, Field, ConfigDict

from app.schemas.v2.vlogger import VloggerResponse


class UserAuthRequest(BaseModel):
    google_id_token: str
    access_token: str


class UserBase(BaseModel):
    email: EmailStr
    google_id: str = Field(max_length=255)
    full_name: str = Field(max_length=255)


class UserResponse(UserBase):
    model_config = ConfigDict(from_attributes=True)

    id: int


class UserPrivateResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: EmailStr
    full_name: str | None = None
    is_admin: bool
    is_superuser: bool
    stripe_customer_id: str | None = None
    stripe_subscription_id: str | None = None
    membership_expires_at: datetime | None = None
    has_membership_active: bool


class UserAuthResponse(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse
    vlogger: VloggerResponse | None
