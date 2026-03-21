from fastapi import status

from app.core.config import settings


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
    assert second_response.status_code == status.HTTP_400_BAD_REQUEST
    assert second_response.json()["detail"] == "Email already registered"


async def test_register_endpoint_short_password(client):
    response = await client.post(
        "/api/v1/auth/register", json={"email": "test@mail.com", "password": "123"}
    )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
