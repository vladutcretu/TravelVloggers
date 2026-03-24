from fastapi import status
from sqlalchemy import select

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


# Endpoint PATCH /api/v1/vloggers/{vlogger_id}
async def test_patch_vloggers_endpoint_success(vlogger, client, admin_token):
    assert vlogger.id
    assert vlogger.youtube_channel_id == "test_channel_id"
    assert vlogger.youtube_channel_name == "test_channel_name"
    assert vlogger.youtube_channel_url == "test_channel_url"
    assert vlogger.youtube_avatar_url == "test_avatar_url"

    response = await client.patch(
        f"/api/v1/vloggers/{vlogger.id}",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "youtube_channel_name": "test_name",
            "youtube_channel_url": "test_url",
            "youtube_avatar_url": "test_avatar",
        },
    )

    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert data["youtube_channel_id"] == "test_channel_id"
    assert data["youtube_channel_name"] == "test_name"
    assert data["youtube_channel_url"] == "test_url"
    assert data["youtube_avatar_url"] == "test_avatar"
    assert data["id"] == vlogger.id
    assert "created_at" in data


async def test_patch_vloggers_endpoint_as_superuser(vlogger, client, superuser_token):
    assert vlogger.id

    response = await client.patch(
        f"/api/v1/vloggers/{vlogger.id}",
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


async def test_patch_vloggers_endpoint_as_user(vlogger, client, user_token):
    assert vlogger.id

    response = await client.patch(
        f"/api/v1/vloggers/{vlogger.id}",
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


async def test_patch_vloggers_endpoint_without_token(vlogger, client):
    assert vlogger.id

    response = await client.patch(
        f"/api/v1/vloggers/{vlogger.id}",
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


async def test_patch_vloggers_endpoint_invalid_vlogger(client, admin_token):
    response = await client.patch(
        "/api/v1/vloggers/325654",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "youtube_channel_id": "test_id",
            "youtube_channel_name": "test_name",
            "youtube_channel_url": "test_url",
            "youtube_avatar_url": "test_avatar",
        },
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "Vlogger does not exist"


async def test_patch_vloggers_endpoint_single_field(vlogger, client, admin_token):
    assert vlogger.id
    assert vlogger.youtube_channel_name == "test_channel_name"
    assert vlogger.youtube_channel_url == "test_channel_url"
    assert vlogger.youtube_avatar_url == "test_avatar_url"

    response = await client.patch(
        f"/api/v1/vloggers/{vlogger.id}",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"youtube_channel_name": "test_name"},
    )

    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert data["youtube_channel_name"] == "test_name"
    assert data["youtube_channel_url"] == "test_channel_url"
    assert data["youtube_avatar_url"] == "test_avatar_url"
    assert data["id"] == vlogger.id


async def test_patch_vloggers_endpoint_invalid_field(vlogger, client, admin_token):
    assert vlogger.id
    assert vlogger.youtube_channel_id == "test_channel_id"

    response = await client.patch(
        f"/api/v1/vloggers/{vlogger.id}",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"youtube_channel_id": "test_id"},
    )

    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert data["youtube_channel_id"] == "test_channel_id"
    assert data["id"] == vlogger.id
    assert "created_at" in data


async def test_patch_vloggers_endpoint_invalid_type(vlogger, client, admin_token):
    assert vlogger.id
    assert vlogger.youtube_channel_id == "test_channel_id"

    response = await client.patch(
        f"/api/v1/vloggers/{vlogger.id}",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"youtube_channel_name": 24},
    )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


# Endpoint DELETE /api/v1/vloggers/{user_id}
async def test_delete_vloggers_endpoint_success(
    vlogger, client, admin_token, db_session
):
    assert vlogger.id

    response = await client.delete(
        f"/api/v1/vloggers/{vlogger.id}",
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    assert response.status_code == status.HTTP_204_NO_CONTENT

    result = await db_session.execute(select(Vlogger).where(Vlogger.id == vlogger.id))
    deleted_vlogger = result.scalar_one_or_none()
    assert deleted_vlogger is None


async def test_delete_vloggers_endpoint_as_superuser(vlogger, client, superuser_token):
    assert vlogger.id

    response = await client.delete(
        f"/api/v1/vloggers/{vlogger.id}",
        headers={"Authorization": f"Bearer {superuser_token}"},
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json()["detail"] == "Not authorized"
    assert vlogger.id


async def test_delete_vloggers_endpoint_as_user(vlogger, client, user_token):
    assert vlogger.id

    response = await client.delete(
        f"/api/v1/vloggers/{vlogger.id}",
        headers={"Authorization": f"Bearer {user_token}"},
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json()["detail"] == "Not authorized"
    assert vlogger.id


async def test_delete_vloggers_endpoint_without_token(vlogger, client):
    assert vlogger.id

    response = await client.delete(
        f"/api/v1/vloggers/{vlogger.id}", headers={"Authorization": "Bearer "}
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json()["detail"] == "Not authenticated"


async def test_delete_vloggers_endpoint_invalid_vlogger(client, admin_token):
    response = await client.delete(
        "/api/v1/vloggers/24342", headers={"Authorization": f"Bearer {admin_token}"}
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "Vlogger does not exist"
