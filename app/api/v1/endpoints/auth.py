from fastapi import APIRouter, status, HTTPException

from app.schemas.user import (
    UserCreateResponse,
    UserCreate,
    UserLogin,
    UserLoginResponse,
    UserPrivateResponse,
)
from app.api.dependencies import DatabaseSession, CurrentUser
from app.repositories.auth import AuthRepository
from app.services.auth import (
    AuthService,
    EmailAlreadyExistsError,
    EmailOrPasswordIncorrectError,
)


router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post(
    "/register",
    response_model=UserCreateResponse,
    response_model_exclude_defaults=True,
    status_code=status.HTTP_201_CREATED,
)
async def register(user_data: UserCreate, db: DatabaseSession):
    repository = AuthRepository(db)
    service = AuthService(repository)

    try:
        user = await service.register_user(user_data.email, user_data.password)
    except EmailAlreadyExistsError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    return user


@router.post("/login", response_model=UserLoginResponse, status_code=status.HTTP_200_OK)
async def login(user_data: UserLogin, db: DatabaseSession):
    repository = AuthRepository(db)
    service = AuthService(repository)

    try:
        access_token = await service.login_user(user_data.email, user_data.password)
    except EmailOrPasswordIncorrectError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email or password are incorrect",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return UserLoginResponse(access_token=access_token, token_type="bearer")


@router.get("/me", response_model=UserPrivateResponse, status_code=status.HTTP_200_OK)
async def get_me(current_user: CurrentUser):
    return current_user
