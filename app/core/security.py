from datetime import timedelta, datetime, UTC

from pwdlib import PasswordHash
import jwt

from app.core.config import settings


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


def verify_access_token(token: str) -> str | None:
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

        return str(sub)
