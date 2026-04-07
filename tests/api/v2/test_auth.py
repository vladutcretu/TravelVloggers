from fastapi import status

from app.models.user import User
from app.models.vlogger import Vlogger


# Endpoint /api/v2/auth/with-google
async def test_login_with_google_without_vlogger(client, db_session, mock_google_token):
    user = User(email="test@gmail.com", google_id="1234567890", full_name="Tester")
    db_session.add(user)
    await db_session.commit()

    payload = {"google_id_token": "fake_token", "access_token": "fake_access"}

    response = await client.post("/api/v2/auth/with-google", json=payload)

    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert data["access_token"].startswith("ey")
    assert data["token_type"] == "bearer"

    assert data["user"]["email"] == "test@gmail.com"
    assert data["user"]["google_id"] == "1234567890"
    assert data["user"]["full_name"] == "Tester"
    assert data["user"]["id"]

    assert data["vlogger"] is None


async def test_login_with_google_with_vlogger(client, db_session, mock_google_token):
    user = User(email="test@gmail.com", google_id="1234567890", full_name="Tester")
    db_session.add(user)
    await db_session.commit()

    vlogger = Vlogger(
        youtube_channel_id="test_channel_id",
        youtube_channel_name="test_channel_name",
        youtube_channel_url="test_channel_url",
        youtube_avatar_url="test_avatar_url",
        user_id=user.id,
        youtube_subscribers_count=100,
        youtube_uploads_id="test_uploads_id",
    )
    db_session.add(vlogger)
    await db_session.commit()

    payload = {"google_id_token": "fake_token", "access_token": "fake_access"}

    response = await client.post("/api/v2/auth/with-google", json=payload)

    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert data["access_token"].startswith("ey")
    assert data["token_type"] == "bearer"

    assert data["user"]["email"] == "test@gmail.com"
    assert data["user"]["google_id"] == "1234567890"
    assert data["user"]["full_name"] == "Tester"
    assert data["user"]["id"]

    assert data["vlogger"]["youtube_channel_id"] == "test_channel_id"
    assert data["vlogger"]["youtube_channel_name"] == "test_channel_name"
    assert data["vlogger"]["youtube_channel_url"] == "test_channel_url"
    assert data["vlogger"]["youtube_avatar_url"] == "test_avatar_url"
    assert data["vlogger"]["youtube_subscribers_count"] == 100
    assert data["vlogger"]["youtube_uploads_id"] == "test_uploads_id"
    assert data["vlogger"]["id"]
    assert data["vlogger"]["user_id"] == user.id
    assert data["vlogger"]["created_at"]


async def test_register_with_google_success(
    client, mock_google_token, mock_youtube_client
):
    payload = {"google_id_token": "fake_token", "access_token": "fake_access"}

    response = await client.post("/api/v2/auth/with-google", json=payload)

    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert data["access_token"].startswith("ey")
    assert data["token_type"] == "bearer"

    assert data["user"]["email"] == "test@gmail.com"
    assert data["user"]["google_id"] == "1234567890"
    assert data["user"]["full_name"] == "Tester"
    assert data["user"]["id"]

    assert data["vlogger"]["youtube_channel_id"] == "test_channel_id"
    assert data["vlogger"]["youtube_channel_name"] == "test_channel_name"
    assert data["vlogger"]["youtube_channel_url"] == "test_channel_url"
    assert data["vlogger"]["youtube_avatar_url"] == "test_avatar_url"
    assert data["vlogger"]["youtube_subscribers_count"] == 100
    assert data["vlogger"]["youtube_uploads_id"] == "test_uploads_id"
    assert data["vlogger"]["id"]
    assert data["vlogger"]["user_id"] == data["user"]["id"]
    assert data["vlogger"]["created_at"]


async def test_register_with_google_email_exists(client, db_session, mock_google_token):
    user = User(
        email="test@gmail.com", google_id="0987654321", full_name="Other Tester"
    )
    db_session.add(user)
    await db_session.commit()

    payload = {"google_id_token": "fake_token", "access_token": "fake_access"}

    response = await client.post("/api/v2/auth/with-google", json=payload)

    assert response.status_code == status.HTTP_409_CONFLICT
    assert response.json()["detail"] == "Email or Google ID already exists."


async def test_with_google_with_invalid_google_id(
    client, db_session, mock_google_token
):
    user = User(email="test@gmail.com", google_id="1234567890", full_name="Tester")
    db_session.add(user)
    await db_session.commit()

    payload = {"google_id_token": "", "access_token": "fake_access"}

    response = await client.post("/api/v2/auth/with-google", json=payload)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json()["detail"] == "Google ID token is invalid or expired."


async def test_with_google_without_google_id(client, db_session, mock_google_token):
    user = User(email="test@gmail.com", google_id="1234567890", full_name="Tester")
    db_session.add(user)
    await db_session.commit()

    payload = {"access_token": "fake_access"}

    response = await client.post("/api/v2/auth/with-google", json=payload)

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


# Endpoint /api/v2/auth/me
async def test_me_endpoint_success(client, db_session, mock_google_token):
    user = User(email="test@gmail.com", google_id="1234567890", full_name="Tester")
    db_session.add(user)
    await db_session.commit()

    response = await client.post(
        "/api/v2/auth/with-google",
        json={"google_id_token": "fake_token", "access_token": "fake_access"},
    )

    token = response.json()["access_token"]

    response = await client.get(
        "/api/v2/auth/me", headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert "id" in data
    assert data["email"] == "test@gmail.com"
    assert type(data["is_admin"]) is bool
    assert type(data["is_superuser"]) is bool
    assert "stripe_customer_id" in data
    assert "stripe_subscription_id" in data
    assert "membership_expires_at" in data
    assert type(data["has_membership_active"]) is bool


async def test_me_endpoint_without_token(client):
    response = await client.get("/api/v2/auth/me")

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json()["detail"] == "Not authenticated"


async def test_me_endpoint_with_invalid_token(client):
    response = await client.get(
        "/api/v2/auth/me", headers={"Authorization": "Bearer invalid_token"}
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json()["detail"] == "Invalid or expired token"
