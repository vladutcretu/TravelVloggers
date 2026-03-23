from fastapi import status

from app.models.vlogger import Vlogger


# Endpoint POST /api/v1/vloggers
async def test_post_vloggers_endpoint_success(client, admin_token):
    response = await client.post(
        "/api/v1/vloggers",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "youtube_channel_id": "test_id",
            "youtube_channel_name": "test_name",
            "youtube_channel_url": "test_url",
            "youtube_avatar_url": "test_avatar",
        },
    )

    assert response.status_code == status.HTTP_201_CREATED

    data = response.json()
    assert data["youtube_channel_id"] == "test_id"
    assert data["youtube_channel_name"] == "test_name"
    assert data["youtube_channel_url"] == "test_url"
    assert data["youtube_avatar_url"] == "test_avatar"
    assert "id" in data
    assert "created_at" in data


async def test_post_vloggers_endpoint_as_superuser(client, superuser_token):
    response = await client.post(
        "/api/v1/vloggers",
        headers={"Authorization": f"Bearer {superuser_token}"},
        json={
            "youtube_channel_id": "test_id",
            "youtube_channel_name": "test_name",
            "youtube_channel_url": "test_url",
            "youtube_avatar_url": "test_avatar",
        },
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json()["detail"] == "Not authorized"


async def test_post_vloggers_endpoint_as_user(client, user_token):
    response = await client.post(
        "/api/v1/vloggers",
        headers={"Authorization": f"Bearer {user_token}"},
        json={
            "youtube_channel_id": "test_id",
            "youtube_channel_name": "test_name",
            "youtube_channel_url": "test_url",
            "youtube_avatar_url": "test_avatar",
        },
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json()["detail"] == "Not authorized"


async def test_post_vloggers_endpoint_without_token(client):
    response = await client.post(
        "/api/v1/vloggers",
        headers={"Authorization": "Bearer "},
        json={
            "youtube_channel_id": "test_id",
            "youtube_channel_name": "test_name",
            "youtube_channel_url": "test_url",
            "youtube_avatar_url": "test_avatar",
        },
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json()["detail"] == "Not authenticated"


async def test_post_vloggers_endpoint_duplicate_channel_id(
    db_session, client, admin_token
):
    vlogger = Vlogger(
        youtube_channel_id="test_id",
        youtube_channel_name="test_name",
        youtube_channel_url="test_url",
        youtube_avatar_url="test_avatar",
    )
    db_session.add(vlogger)
    await db_session.commit()

    assert vlogger.id

    response = await client.post(
        "/api/v1/vloggers",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "youtube_channel_id": "test_id",
            "youtube_channel_name": "name_test",
            "youtube_channel_url": "url_test",
            "youtube_avatar_url": "test_avatar",
        },
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["detail"] == "Vlogger already exists"


async def test_post_vloggers_endpoint_duplicate_channel_name(
    db_session, client, admin_token
):
    vlogger = Vlogger(
        youtube_channel_id="test_id",
        youtube_channel_name="test_name",
        youtube_channel_url="test_url",
        youtube_avatar_url="test_avatar",
    )
    db_session.add(vlogger)
    await db_session.commit()

    assert vlogger.id

    response = await client.post(
        "/api/v1/vloggers",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "youtube_channel_id": "id_test",
            "youtube_channel_name": "test_name",
            "youtube_channel_url": "url_test",
            "youtube_avatar_url": "test_avatar",
        },
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["detail"] == "Vlogger already exists"


async def test_post_vloggers_endpoint_duplicate_channel_url(
    db_session, client, admin_token
):
    vlogger = Vlogger(
        youtube_channel_id="test_id",
        youtube_channel_name="test_name",
        youtube_channel_url="test_url",
        youtube_avatar_url="test_avatar",
    )
    db_session.add(vlogger)
    await db_session.commit()

    assert vlogger.id

    response = await client.post(
        "/api/v1/vloggers",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "youtube_channel_id": "id_test",
            "youtube_channel_name": "name_test",
            "youtube_channel_url": "test_url",
            "youtube_avatar_url": "test_avatar",
        },
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["detail"] == "Vlogger already exists"
