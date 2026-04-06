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


class UserAuthResponse(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse
    vlogger: VloggerResponse | None
