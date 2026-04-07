from fastapi import APIRouter, HTTPException, status

from app.schemas.v2.user import UserAuthResponse, UserAuthRequest, UserResponse
from app.schemas.v2.vlogger import VloggerResponse
from app.api.dependencies import DatabaseSession
from app.repositories.v2.auth import AuthRepository
from app.services.v2.auth import AuthService
from app.core.exceptions import (
    UserDoesntExistError,
    EmailAlreadyExistsError,
    GoogleIdAlreadyExistsError,
)


router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/with-google", response_model=UserAuthResponse)
async def register_or_login_with_google(payload: UserAuthRequest, db: DatabaseSession):
    service = AuthService(AuthRepository(db))

    try:
        user, vlogger = await service.login_with_google(payload.google_id_token)
    except UserDoesntExistError:
        try:
            user, vlogger = await service.register_with_google(
                payload.google_id_token, payload.access_token
            )
        except (EmailAlreadyExistsError, GoogleIdAlreadyExistsError):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email or Google ID already exists.",
            )

    access_token = await service.create_access_token(user.id)

    return UserAuthResponse(
        access_token=access_token,
        token_type="bearer",
        user=UserResponse.model_validate(user),
        vlogger=VloggerResponse.model_validate(vlogger) if vlogger else None,
    )
