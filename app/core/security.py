from datetime import timedelta, datetime, UTC

from pwdlib import PasswordHash
import jwt
from google.oauth2 import id_token
from google.auth.transport import requests

from app.core.config import settings
from app.schemas.v2.user import UserBase
from app.core.exceptions import GoogleInvalidTokenError, GoogleIncompleteTokenError


password_hasher = PasswordHash.recommended()


def hash_password(password: str) -> str:
    return password_hasher.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return password_hasher.verify(plain_password, hashed_password)


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    """
    Create a JWT access token.
    """
    payload = data.copy()

    if expires_delta:
        expire = datetime.now(UTC) + expires_delta
    else:
        expire = datetime.now(UTC) + timedelta(
            minutes=settings.access_token_expire_minutes
        )

    payload.update({"exp": expire, "type": "access"})

    if "sub" not in payload:
        raise ValueError("Token must include 'sub'")

    encoded_jwt = jwt.encode(
        payload=payload,
        key=settings.access_token_secret_key.get_secret_value(),
        algorithm=settings.access_token_algorithm,
    )
    return encoded_jwt


def verify_access_token(token: str) -> int | None:
    """
    Verify a JWT access token (exp) and return the sub (user id) if it's valid.
    """
    try:
        payload = jwt.decode(
            jwt=token,
            key=settings.access_token_secret_key.get_secret_value(),
            algorithms=[settings.access_token_algorithm],
            options={"require": ["exp", "sub"]},
        )
    except jwt.InvalidTokenError:
        return None
    else:
        sub = payload.get("sub")
        token_type = payload.get("type")

        if sub is None or token_type != "access":
            return None

        return int(sub)


def decode_google_token(google_id_token: str) -> UserBase:
    """
    Decodes Google ID Token (JWT) and validates it using Google's public keys if needed.
    Returns email, google_id, full_name.
    """
    try:
        id_info = id_token.verify_oauth2_token(
            google_id_token,
            requests.Request(),
            audience=settings.GOOGLE_APP_CLIENT_ID,
        )
    except ValueError:
        raise GoogleInvalidTokenError("Google ID token is invalid or expired.")

    email = id_info.get("email")
    google_id = id_info.get("sub")
    full_name = id_info.get("name")

    if not all([email, google_id, full_name]):
        raise GoogleIncompleteTokenError(
            "Google token payload is missing required fields."
        )

    return UserBase(
        email=str(email),
        google_id=str(google_id),
        full_name=str(full_name),
    )
