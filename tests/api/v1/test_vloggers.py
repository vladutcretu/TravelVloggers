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

    assert response.status_code == status.HTTP_409_CONFLICT
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

    assert response.status_code == status.HTTP_409_CONFLICT
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

    assert response.status_code == status.HTTP_409_CONFLICT
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


# Endpoint DELETE /api/v1/vloggers/{vlogger_id}
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


# Endpoint GET /api/v1/vloggers/
async def test_get_vloggers_endpoint_without_more(vloggers_factory, client, pagination):
    vloggers = await vloggers_factory(instances=pagination.limit)

    response = await client.get(
        f"/api/v1/vloggers?skip={pagination.skip}&limit={pagination.limit}&order={pagination.order}"
    )

    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert len(data) == 4  # Vlogger items + 3 params
    assert len(data["vloggers"]) == min(len(vloggers), pagination.limit)

    item = data["vloggers"][0]
    assert item["youtube_channel_id"] == "id_0"
    assert item["youtube_channel_name"] == "name_0"
    assert item["youtube_channel_url"] == "url_0"
    assert item["youtube_avatar_url"] == "avatar_0"
    assert "id" in item
    assert "created_at" in item

    assert data["skip"] == pagination.skip
    assert data["limit"] == pagination.limit
    assert data["has_more"] is False


async def test_get_vloggers_endpoint_with_more(vloggers_factory, client, pagination):
    vloggers = await vloggers_factory(instances=pagination.limit + 1)

    response = await client.get(
        f"/api/v1/vloggers?skip={pagination.skip}&limit={pagination.limit}&order={pagination.order}"
    )

    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert len(data) == 4
    assert len(data["vloggers"]) == min(len(vloggers), pagination.limit)

    item = data["vloggers"][8]
    assert item["youtube_channel_id"] == "id_8"
    assert item["youtube_channel_name"] == "name_8"
    assert item["youtube_channel_url"] == "url_8"
    assert item["youtube_avatar_url"] == "avatar_8"
    assert "id" in item
    assert "created_at" in item

    assert data["skip"] == pagination.skip
    assert data["limit"] == pagination.limit
    assert data["has_more"] is True


async def test_get_vloggers_endpoint_with_skip(vloggers_factory, client, pagination):
    vloggers = await vloggers_factory(instances=pagination.limit)

    pagination.skip = 1

    response = await client.get(
        f"/api/v1/vloggers?skip={pagination.skip}&limit={pagination.limit}&order={pagination.order}"
    )

    assert response.status_code == status.HTTP_200_OK

    data = response.json()

    total_vloggers = len(vloggers)
    expected_count = max(0, total_vloggers - 1)  # skip = 1
    returned_count = len(data["vloggers"])

    assert returned_count == expected_count

    first_returned_vlogger = data["vloggers"][0]
    second_vlogger = vloggers[1]

    assert first_returned_vlogger["id"] == second_vlogger.id
    assert (
        first_returned_vlogger["youtube_channel_name"]
        == second_vlogger.youtube_channel_name
    )

    assert data["skip"] == 1
    assert data["limit"] == pagination.limit
    assert data["has_more"] is False


async def test_get_vloggers_endpoint_with_limit(vloggers_factory, client, pagination):
    vloggers = await vloggers_factory(instances=pagination.limit)

    pagination.limit = 2

    response = await client.get(
        f"/api/v1/vloggers?skip={pagination.skip}&limit={pagination.limit}&order={pagination.order}"
    )

    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert len(data["vloggers"]) == min(len(vloggers), pagination.limit)


async def test_get_vloggers_endpoint_with_order_asc(
    vloggers_factory, client, pagination
):
    vloggers = await vloggers_factory(instances=pagination.limit)

    pagination.order = "asc"

    response = await client.get(
        f"/api/v1/vloggers?skip={pagination.skip}&limit={pagination.limit}&order={pagination.order}"
    )

    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert len(data["vloggers"]) == min(len(vloggers), pagination.limit)

    vloggers_sorted_desc = sorted(
        vloggers, key=lambda vlogger: vlogger.created_at, reverse=False
    )
    first_returned_vlogger = data["vloggers"][0]
    first_created_vlogger = vloggers_sorted_desc[0]

    assert first_returned_vlogger["id"] == first_created_vlogger.id
    assert (
        first_returned_vlogger["youtube_channel_name"]
        == first_created_vlogger.youtube_channel_name
    )


async def test_get_vloggers_endpoint_with_order_desc(
    vloggers_factory, client, pagination
):
    vloggers = await vloggers_factory(instances=pagination.limit)

    pagination.order = "desc"

    response = await client.get(
        f"/api/v1/vloggers?skip={pagination.skip}&limit={pagination.limit}&order={pagination.order}"
    )

    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert len(data["vloggers"]) == min(len(vloggers), pagination.limit)

    vloggers_sorted_desc = sorted(
        vloggers, key=lambda vlogger: vlogger.created_at, reverse=True
    )
    first_returned_vlogger = data["vloggers"][0]
    last_created_vlogger = vloggers_sorted_desc[0]

    assert first_returned_vlogger["id"] == last_created_vlogger.id
    assert (
        first_returned_vlogger["youtube_channel_name"]
        == last_created_vlogger.youtube_channel_name
    )


async def test_get_vloggers_endpoint_with_skip_invalid(
    vloggers_factory, client, pagination
):
    await vloggers_factory(instances=pagination.limit)

    pagination.skip = -1

    response = await client.get(
        f"/api/v1/vloggers?skip={pagination.skip}&limit={pagination.limit}&order={pagination.order}"
    )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


async def test_get_vloggers_endpoint_with_limit_invalid(
    vloggers_factory, client, pagination
):
    await vloggers_factory(instances=pagination.limit)

    pagination.limit = -10

    response = await client.get(
        f"/api/v1/vloggers?skip={pagination.skip}&limit={pagination.limit}&order={pagination.order}"
    )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


async def test_get_vloggers_endpoint_with_order_invalid(
    vloggers_factory, client, pagination
):
    await vloggers_factory(instances=pagination.limit)

    pagination.order = "alpha"

    response = await client.get(
        f"/api/v1/vloggers?skip={pagination.skip}&limit={pagination.limit}&order={pagination.order}"
    )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


async def test_get_vloggers_endpoint_with_no_vloggers(client, pagination):
    response = await client.get(
        f"/api/v1/vloggers?skip={pagination.skip}&limit={pagination.limit}&order={pagination.order}"
    )

    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert len(data) == 4
    assert len(data["vloggers"]) == 0

    assert data["skip"] == pagination.skip
    assert data["limit"] == pagination.limit
    assert data["has_more"] is False


# Endpoint GET /api/v1/vloggers/{vlogger_id}
async def test_get_vlogger_endpoint_success(vlogger, client):
    assert vlogger.id

    response = await client.get(f"/api/v1/vloggers/{vlogger.id}")

    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert data["youtube_channel_id"] == "test_channel_id"
    assert data["youtube_channel_name"] == "test_channel_name"
    assert data["youtube_channel_url"] == "test_channel_url"
    assert data["youtube_avatar_url"] == "test_avatar_url"
    assert data["id"] == vlogger.id
    assert "created_at" in data


async def test_get_vlogger_endpoint_invalid_vlogger(client):
    response = await client.get("/api/v1/vloggers/53252")

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "Vlogger does not exist"


async def test_get_vlogger_endpoint_invalid_type(client):
    response = await client.get("/api/v1/vloggers/vlogger4")

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


# Endpoint GET /api/v1/vloggers/{vlogger_id}/vlogs
async def test_get_vlogs_by_vlogger_endpoint_without_more(
    vlogs_factory, pagination, vlogger, client
):
    vlogs = await vlogs_factory(instances=pagination.limit)
    for vlog in vlogs:
        vlog.vlogger_id = vlogger.id

    assert vlogs[0].vlogger_id == vlogger.id
    assert vlogs[pagination.limit - 1].vlogger_id == vlogger.id

    response = await client.get(
        f"/api/v1/vloggers/{vlogger.id}/vlogs?skip={pagination.skip}&limit={pagination.limit}&order={pagination.order}"
    )

    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert len(data) == 10  # 6 Vlogger data + Vlog items + 3 params
    assert len(data["vlogs"]) == min(len(vlogs), pagination.limit)

    assert data["youtube_channel_id"] == vlogger.youtube_channel_id
    assert data["youtube_channel_name"] == vlogger.youtube_channel_name
    assert data["youtube_channel_url"] == vlogger.youtube_channel_url
    assert data["youtube_avatar_url"] == vlogger.youtube_avatar_url
    assert "id" in data
    assert "created_at" in data

    item = data["vlogs"][0]
    assert item["vlogger_id"] == vlogger.id
    assert item["country_id"] == vlogs[0].country_id
    assert item["youtube_video_id"] == vlogs[0].youtube_video_id
    assert item["youtube_video_url"] == vlogs[0].youtube_video_url
    assert "published_at" in item
    assert item["title"] == "title_0"
    assert item["thumbnail_url"] == "thumbnail_0"
    assert item["language"] is None
    assert "id" in item
    assert "created_at" in item

    assert data["skip"] == pagination.skip
    assert data["limit"] == pagination.limit
    assert data["has_more"] is False


async def test_get_vlogs_by_vlogger_endpoint_with_more(
    vlogs_factory, pagination, vlogger, client
):
    vlogs = await vlogs_factory(instances=pagination.limit + 1)
    for vlog in vlogs:
        vlog.vlogger_id = vlogger.id

    assert vlogs[0].vlogger_id == vlogger.id
    assert vlogs[pagination.limit - 1].vlogger_id == vlogger.id

    response = await client.get(f"/api/v1/vloggers/{vlogger.id}/vlogs")

    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert len(data) == 10  # 6 Vlogger data + Vlog items + 3 params
    assert len(data["vlogs"]) == min(len(vlogs), pagination.limit)

    assert data["youtube_channel_id"] == vlogger.youtube_channel_id
    assert data["youtube_channel_name"] == vlogger.youtube_channel_name
    assert data["youtube_channel_url"] == vlogger.youtube_channel_url
    assert data["youtube_avatar_url"] == vlogger.youtube_avatar_url
    assert "id" in data
    assert "created_at" in data

    item = data["vlogs"][0]
    assert item["vlogger_id"] == vlogger.id
    assert item["country_id"] == vlogs[0].country_id
    assert item["youtube_video_id"] == vlogs[0].youtube_video_id
    assert item["youtube_video_url"] == vlogs[0].youtube_video_url
    assert "published_at" in item
    assert item["title"] == "title_0"
    assert item["thumbnail_url"] == "thumbnail_0"
    assert item["language"] is None
    assert "id" in item
    assert "created_at" in item

    assert data["skip"] == pagination.skip
    assert data["limit"] == pagination.limit
    assert data["has_more"] is True


async def test_get_vlogs_by_vlogger_endpoint_with_skip(
    vlogs_factory, pagination, vlogger, client
):
    vlogs = await vlogs_factory(instances=pagination.limit)
    for vlog in vlogs:
        vlog.vlogger_id = vlogger.id

    assert vlogs[0].vlogger_id == vlogger.id
    assert vlogs[pagination.limit - 1].vlogger_id == vlogger.id

    pagination.skip = 1

    response = await client.get(
        f"/api/v1/vloggers/{vlogger.id}/vlogs?skip={pagination.skip}&limit={pagination.limit}&order={pagination.order}"
    )

    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert data["youtube_channel_id"] == vlogger.youtube_channel_id
    assert data["youtube_channel_name"] == vlogger.youtube_channel_name
    assert data["youtube_channel_url"] == vlogger.youtube_channel_url
    assert data["youtube_avatar_url"] == vlogger.youtube_avatar_url
    assert "id" in data
    assert "created_at" in data

    total_vlogs = len(vlogs)
    expected_count = max(0, total_vlogs - 1)  # skip = 1
    returned_count = len(data["vlogs"])

    assert returned_count == expected_count

    first_returned_vlog = data["vlogs"][0]
    second_vlog = vlogs[1]

    assert first_returned_vlog["id"] == second_vlog.id
    assert first_returned_vlog["youtube_video_id"] == second_vlog.youtube_video_id

    assert data["skip"] == 1
    assert data["limit"] == pagination.limit
    assert data["has_more"] is False


async def test_get_vlogs_by_vlogger_endpoint_with_limit(
    vlogs_factory, pagination, vlogger, client
):
    vlogs = await vlogs_factory(instances=pagination.limit)
    for vlog in vlogs:
        vlog.vlogger_id = vlogger.id

    assert vlogs[0].vlogger_id == vlogger.id
    assert vlogs[pagination.limit - 1].vlogger_id == vlogger.id

    pagination.limit = 2

    response = await client.get(
        f"/api/v1/vloggers/{vlogger.id}/vlogs?skip={pagination.skip}&limit={pagination.limit}&order={pagination.order}"
    )

    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert len(data["vlogs"]) == min(len(vlogs), pagination.limit)


async def test_get_vlogs_by_vlogger_endpoint_with_order_asc(
    vlogs_factory, pagination, vlogger, client
):
    vlogs = await vlogs_factory(instances=pagination.limit)
    for vlog in vlogs:
        vlog.vlogger_id = vlogger.id

    assert vlogs[0].vlogger_id == vlogger.id
    assert vlogs[pagination.limit - 1].vlogger_id == vlogger.id

    pagination.order = "asc"

    response = await client.get(
        f"/api/v1/vloggers/{vlogger.id}/vlogs?skip={pagination.skip}&limit={pagination.limit}&order={pagination.order}"
    )

    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert len(data["vlogs"]) == min(len(vlogs), pagination.limit)

    vlogs_sorted_desc = sorted(vlogs, key=lambda vlog: vlog.created_at, reverse=False)
    first_returned_vlog = data["vlogs"][0]
    first_created_vlog = vlogs_sorted_desc[0]

    assert first_returned_vlog["id"] == first_created_vlog.id
    assert (
        first_returned_vlog["youtube_video_id"] == first_created_vlog.youtube_video_id
    )


async def test_get_vlogs_by_vlogger_endpoint_with_order_desc(
    vlogs_factory, pagination, vlogger, client
):
    vlogs = await vlogs_factory(instances=pagination.limit)
    for vlog in vlogs:
        vlog.vlogger_id = vlogger.id

    assert vlogs[0].vlogger_id == vlogger.id
    assert vlogs[pagination.limit - 1].vlogger_id == vlogger.id

    pagination.order = "desc"

    response = await client.get(
        f"/api/v1/vloggers/{vlogger.id}/vlogs?skip={pagination.skip}&limit={pagination.limit}&order={pagination.order}"
    )

    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert len(data["vlogs"]) == min(len(vlogs), pagination.limit)

    vlogs_sorted_desc = sorted(vlogs, key=lambda vlog: vlog.created_at, reverse=True)
    first_returned_vlog = data["vlogs"][0]
    last_created_vlog = vlogs_sorted_desc[0]

    assert first_returned_vlog["id"] == last_created_vlog.id
    assert first_returned_vlog["youtube_video_id"] == last_created_vlog.youtube_video_id


async def test_get_vlogs_by_vlogger_endpoint_with_invalid_vlogger(
    vlogs_factory, pagination, client
):
    await vlogs_factory(instances=pagination.limit)

    response = await client.get(
        f"/api/v1/vloggers/12414/vlogs?skip={pagination.skip}&limit={pagination.limit}&order={pagination.order}"
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "Vlogger does not exist"


async def test_get_vlogs_by_vlogger_endpoint_with_invalid_vlogger_type(
    vlogs_factory, pagination, client
):
    await vlogs_factory(instances=pagination.limit)

    response = await client.get(
        f"/api/v1/vloggers/Traveler/vlogs?skip={pagination.skip}&limit={pagination.limit}&order={pagination.order}"
    )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


async def test_get_vlogs_by_vlogger_endpoint_with_skip_invalid(
    vlogs_factory, pagination, vlogger, client
):
    await vlogs_factory(instances=pagination.limit)

    pagination.skip = -1

    response = await client.get(
        f"/api/v1/vloggers/{vlogger.id}/vlogs?skip={pagination.skip}&limit={pagination.limit}&order={pagination.order}"
    )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


async def test_get_vlogs_by_vlogger_endpoint_with_limit_invalid(
    vlogs_factory, pagination, vlogger, client
):
    await vlogs_factory(instances=pagination.limit)

    pagination.limit = -10

    response = await client.get(
        f"/api/v1/vloggers/{vlogger.id}/vlogs?skip={pagination.skip}&limit={pagination.limit}&order={pagination.order}"
    )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


async def test_get_vlogs_by_vlogger_endpoint_with_order_invalid(
    vlogs_factory, pagination, vlogger, client
):
    await vlogs_factory(instances=pagination.limit)

    pagination.order = "alpha"

    response = await client.get(
        f"/api/v1/vloggers/{vlogger.id}/vlogs?skip={pagination.skip}&limit={pagination.limit}&order={pagination.order}"
    )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


async def test_get_vlogs_by_vlogger_endpoint_with_no_vlogs(pagination, vlogger, client):
    response = await client.get(
        f"/api/v1/vloggers/{vlogger.id}/vlogs?skip={pagination.skip}&limit={pagination.limit}&order={pagination.order}"
    )

    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert len(data) == 10
    assert len(data["vlogs"]) == 0

    assert data["youtube_channel_id"] == vlogger.youtube_channel_id
    assert data["youtube_channel_name"] == vlogger.youtube_channel_name
    assert data["youtube_channel_url"] == vlogger.youtube_channel_url
    assert data["youtube_avatar_url"] == vlogger.youtube_avatar_url
    assert "id" in data
    assert "created_at" in data

    assert data["skip"] == pagination.skip
    assert data["limit"] == pagination.limit
    assert data["has_more"] is False
