import jwt

from fastapi import status

from app.core.config import settings
from app.models.user import User
from app.core.security import hash_password


# Endpoint /api/v1/auth/register
async def test_register_endpoint_success(client):
    response = await client.post(
        "/api/v1/auth/register", json={"email": "test@mail.com", "password": "123456"}
    )

    assert response.status_code == status.HTTP_201_CREATED

    data = response.json()
    assert data["email"] == "test@mail.com"
    assert "id" in data
    assert "password_hash" not in data
    assert "is_superuser" not in data


async def test_register_endpoint_superuser_success(client):
    response = await client.post(
        "/api/v1/auth/register",
        json={"email": settings.SUPERUSER_EMAIL, "password": "123456"},
    )

    assert response.status_code == status.HTTP_201_CREATED

    data = response.json()
    assert data["email"] == settings.SUPERUSER_EMAIL
    assert "id" in data
    assert "password_hash" not in data
    assert "is_superuser" in data


async def test_register_endpoint_duplicate_email(client):
    payload = {"email": "test@mail.com", "password": "123456"}
    first_response = await client.post("/api/v1/auth/register", json=payload)
    second_response = await client.post("/api/v1/auth/register", json=payload)

    assert first_response.status_code == status.HTTP_201_CREATED
    assert second_response.status_code == status.HTTP_409_CONFLICT
    assert second_response.json()["detail"] == "Email already registered"


async def test_register_endpoint_short_password(client):
    response = await client.post(
        "/api/v1/auth/register", json={"email": "test@mail.com", "password": "123"}
    )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


async def test_register_endpoint_missing_fields(client):
    response = await client.post(
        "/api/v1/auth/register", json={"email": "test@mail.com"}
    )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


async def test_register_endpoint_email_format(client):
    response = await client.post(
        "/api/v1/auth/register", json={"email": "invalid-email", "password": "123456"}
    )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


# Endpoint /api/v1/auth/login
async def test_login_endpoint_success(client, db_session):
    user = User(email="test@mail.com", password_hash=hash_password("123456"))
    db_session.add(user)
    await db_session.commit()

    response = await client.post(
        "/api/v1/auth/login", json={"email": "test@mail.com", "password": "123456"}
    )

    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert "access_token" in data
    assert data["access_token"].startswith("ey")
    assert data["token_type"] == "bearer"


async def test_login_endpoint_email_incorrect(client, db_session):
    user = User(email="test@mail.com", password_hash=hash_password("123456"))
    db_session.add(user)
    await db_session.commit()

    response = await client.post(
        "/api/v1/auth/login", json={"email": "not_found@mail.com", "password": "123456"}
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json()["detail"] == "Email or password are incorrect"


async def test_login_endpoint_password_incorrect(client, db_session):
    user = User(email="test@mail.com", password_hash=hash_password("123456"))
    db_session.add(user)
    await db_session.commit()

    response = await client.post(
        "/api/v1/auth/login", json={"email": "test@mail.com", "password": "wrong_pass"}
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json()["detail"] == "Email or password are incorrect"


async def test_login_endpoint_missing_fields(client):
    response = await client.post("/api/v1/auth/login", json={"email": "test@mail.com"})

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


async def test_login_endpoint_email_format(client):
    response = await client.post(
        "/api/v1/auth/login", json={"email": "invalid-email", "password": "123456"}
    )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


async def test_login_token_payload(client, db_session):
    user = User(email="test@mail.com", password_hash=hash_password("123456"))
    db_session.add(user)
    await db_session.commit()

    response = await client.post(
        "/api/v1/auth/login", json={"email": "test@mail.com", "password": "123456"}
    )

    token = response.json()["access_token"]

    payload = jwt.decode(
        jwt=token,
        key=settings.access_token_secret_key.get_secret_value(),
        algorithms=[settings.access_token_algorithm],
    )

    assert "exp" in payload
    assert payload["sub"] == str(user.id)
    assert payload["type"] == "access"


# Endpoint /api/v1/auth/me
async def test_me_endpoint_success(client, db_session):
    user = User(email="test@mail.com", password_hash=hash_password("123456"))
    db_session.add(user)
    await db_session.commit()

    response = await client.post(
        "/api/v1/auth/login", json={"email": "test@mail.com", "password": "123456"}
    )

    token = response.json()["access_token"]

    response = await client.get(
        "/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert "id" in data
    assert data["email"] == "test@mail.com"
    assert type(data["is_admin"]) is bool
    assert type(data["is_superuser"]) is bool


async def test_me_endpoint_without_token(client):
    response = await client.get("/api/v1/auth/me")

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json()["detail"] == "Not authenticated"


async def test_me_endpoint_with_invalid_token(client, db_session):
    response = await client.get(
        "/api/v1/auth/me", headers={"Authorization": "Bearer invalid_token"}
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json()["detail"] == "Invalid or expired token"


async def test_me_endpoint_deleted_user(client, db_session):
    user = User(email="test@mail.com", password_hash=hash_password("123456"))
    db_session.add(user)
    await db_session.commit()

    response = await client.post(
        "/api/v1/auth/login", json={"email": "test@mail.com", "password": "123456"}
    )

    token = response.json()["access_token"]

    await db_session.delete(user)
    await db_session.commit()
    db_session.expunge_all()  # clear session cache

    response = await client.get(
        "/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "User does not exist"
