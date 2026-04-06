from pydantic import BaseModel, EmailStr, ConfigDict

from app.schemas.v2.vlogger import VloggerResponse


class UserAuthRequest(BaseModel):
    google_id_token: str
    access_token: str


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: EmailStr
    google_id: str
    full_name: str


class UserAuthResponse(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse
    vlogger: VloggerResponse
