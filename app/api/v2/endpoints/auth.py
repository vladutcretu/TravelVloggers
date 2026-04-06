from fastapi import APIRouter

from app.schemas.v2.user import UserAuthResponse, UserAuthRequest
from app.api.dependencies import DatabaseSession
from app.repositories.v2.auth import AuthRepository
from app.services.v2.auth import AuthService
from app.core.exceptions import UserDoesntExistError


router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/with-google", response_model=UserAuthResponse)
async def register_or_login_with_google(payload: UserAuthRequest, db: DatabaseSession):
    service = AuthService(AuthRepository(db))

    try:
        user, vlogger = await service.login_with_google(payload.google_id_token)
    except UserDoesntExistError:
        user, vlogger = await service.register_with_google(
            payload.google_id_token, payload.access_token
        )

    access_token = await service.create_access_token(user.id)

    return UserAuthResponse(
        access_token=access_token, token_type="bearer", user=user, vlogger=vlogger
    )
