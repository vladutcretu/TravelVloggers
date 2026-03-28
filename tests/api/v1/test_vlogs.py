from fastapi import status
from sqlalchemy import select

from app.models.vlog import Vlog


# Endpoint GET /api/v1/vlogs/countries/
async def test_get_countries_endpoint_without_more(
    countries_factory, client, pagination
):
    countries = await countries_factory(instances=pagination.limit)
    assert len(countries) <= pagination.limit

    response = await client.get(
        f"/api/v1/vlogs/countries?skip={pagination.skip}&limit={pagination.limit}&order={pagination.order}"
    )

    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert len(data) == 4  # Country items + 3 params
    assert len(data["countries"]) == min(len(countries), pagination.limit)

    item = data["countries"][0]
    assert item["name"] == "Name #0"
    assert item["iso_code"] == "AA"
    assert "id" in item

    assert data["skip"] == pagination.skip
    assert data["limit"] == pagination.limit
    assert data["has_more"] is False


async def test_get_countries_endpoint_with_more(countries_factory, client, pagination):
    countries = await countries_factory(instances=14)
    assert len(countries) > pagination.limit

    response = await client.get(
        f"/api/v1/vlogs/countries?skip={pagination.skip}&limit={pagination.limit}&order={pagination.order}"
    )

    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert len(data) == 4
    assert len(data["countries"]) == min(len(countries), pagination.limit)

    item = data["countries"][0]
    assert item["name"] == "Name #0"
    assert item["iso_code"] == "AA"
    assert "id" in item

    assert data["skip"] == pagination.skip
    assert data["limit"] == pagination.limit
    assert data["has_more"] is True


async def test_get_countries_endpoint_with_skip(countries_factory, client, pagination):
    countries = await countries_factory(instances=pagination.limit)

    pagination.skip = 1

    response = await client.get(
        f"/api/v1/vlogs/countries?skip={pagination.skip}&limit={pagination.limit}&order={pagination.order}"
    )

    assert response.status_code == status.HTTP_200_OK

    data = response.json()

    total_countries = len(countries)
    expected_count = max(0, total_countries - 1)  # skip = 1
    returned_count = len(data["countries"])

    assert returned_count == expected_count

    first_returned_country = data["countries"][0]
    second_country = countries[1]

    assert first_returned_country["id"] == second_country.id
    assert first_returned_country["name"] == second_country.name

    assert data["skip"] == 1
    assert data["limit"] == pagination.limit
    assert data["has_more"] is False


async def test_get_countries_endpoint_with_limit(countries_factory, client, pagination):
    countries = await countries_factory(instances=pagination.limit)

    pagination.limit = 2

    response = await client.get(
        f"/api/v1/vlogs/countries?skip={pagination.skip}&limit={pagination.limit}&order={pagination.order}"
    )

    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert len(data["countries"]) == min(len(countries), pagination.limit)


async def test_get_countries_endpoint_with_order_asc(
    countries_factory, client, pagination
):
    countries = await countries_factory(instances=pagination.limit)

    pagination.order = "asc"

    response = await client.get(
        f"/api/v1/vlogs/countries?skip={pagination.skip}&limit={pagination.limit}&order={pagination.order}"
    )

    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert len(data["countries"]) == min(len(countries), pagination.limit)

    countries_sorted_desc = sorted(
        countries, key=lambda country: country.name, reverse=False
    )
    first_returned_country = data["countries"][0]
    first_created_country = countries_sorted_desc[0]

    assert first_returned_country["id"] == first_created_country.id
    assert first_returned_country["name"] == first_created_country.name


async def test_get_countries_endpoint_with_order_desc(
    countries_factory, client, pagination
):
    countries = await countries_factory(instances=pagination.limit)

    pagination.order = "desc"

    response = await client.get(
        f"/api/v1/vlogs/countries?skip={pagination.skip}&limit={pagination.limit}&order={pagination.order}"
    )

    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert len(data["countries"]) == min(len(countries), pagination.limit)

    countries_sorted_desc = sorted(
        countries, key=lambda country: country.name, reverse=True
    )
    first_returned_country = data["countries"][0]
    last_created_country = countries_sorted_desc[0]

    assert first_returned_country["id"] == last_created_country.id
    assert first_returned_country["name"] == last_created_country.name


async def test_get_countries_endpoint_with_skip_invalid(
    countries_factory, client, pagination
):
    await countries_factory(instances=pagination.limit)

    pagination.skip = -1

    response = await client.get(
        f"/api/v1/vlogs/countries?skip={pagination.skip}&limit={pagination.limit}&order={pagination.order}"
    )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


async def test_get_countries_endpoint_with_limit_invalid(
    countries_factory, client, pagination
):
    await countries_factory(instances=pagination.limit)

    pagination.limit = -10

    response = await client.get(
        f"/api/v1/vlogs/countries?skip={pagination.skip}&limit={pagination.limit}&order={pagination.order}"
    )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


async def test_get_countries_endpoint_with_order_invalid(
    countries_factory, client, pagination
):
    await countries_factory(instances=pagination.limit)

    pagination.order = "alpha"

    response = await client.get(
        f"/api/v1/vlogs/countries?skip={pagination.skip}&limit={pagination.limit}&order={pagination.order}"
    )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


async def test_get_countries_endpoint_with_no_countries(client, pagination):
    response = await client.get(
        f"/api/v1/vlogs/countries?skip={pagination.skip}&limit={pagination.limit}&order={pagination.order}"
    )

    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert len(data) == 4
    assert len(data["countries"]) == 0

    assert data["skip"] == pagination.skip
    assert data["limit"] == pagination.limit
    assert data["has_more"] is False


async def test_get_countries_endpoint_with_search_name(
    countries_factory, client, pagination
):
    await countries_factory(instances=47)

    response = await client.get(
        f"/api/v1/vlogs/countries?search=am&skip={pagination.skip}&limit={pagination.limit}&order={pagination.order}"
    )

    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    item = data["countries"][0]
    assert "am" in item["name"]


async def test_get_countries_endpoint_with_search_iso(
    countries_factory, client, pagination
):
    await countries_factory(instances=47)

    response = await client.get(
        f"/api/v1/vlogs/countries?search=S&skip={pagination.skip}&limit={pagination.limit}&order={pagination.order}"
    )

    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    item = data["countries"][0]
    assert "S" in item["iso_code"]


# Endpoint POST /api/v1/vlogs/
async def test_post_vlogs_endpoint_without_token(
    vloggers_factory, countries_factory, client
):
    vloggers = await vloggers_factory(instances=1)
    countries = await countries_factory(instances=1)

    response = await client.post(
        "/api/v1/vlogs",
        headers={"Authoriztion": "Bearer "},
        json={
            "vlogger_id": vloggers[0].id,
            "country_id": countries[0].id,
            "youtube_video_id:": "stringstrin",
        },
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json()["detail"] == "Not authenticated"


async def test_post_vlogs_endpoint_without_access(
    vloggers_factory,
    countries_factory,
    client,
    user_token,
):
    vloggers = await vloggers_factory(instances=1)
    countries = await countries_factory(instances=1)

    response = await client.post(
        "/api/v1/vlogs",
        headers={"Authorization": f"Bearer {user_token}"},
        json={
            "vlogger_id": vloggers[0].id,
            "country_id": countries[0].id,
            "youtube_video_id": "stringstrin",
        },
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json()["detail"] == "Not authorized"


async def test_post_vlogs_endpoint_without_fields(
    vloggers_factory,
    countries_factory,
    client,
    admin_token,
):
    vloggers = await vloggers_factory(instances=1)
    countries = await countries_factory(instances=1)

    response = await client.post(
        "/api/v1/vlogs",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "vlogger_id": vloggers[0].id,
            "country_id": countries[0].id,
        },
    )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


async def test_post_vlogs_endpoint_with_invalid_vlogger(
    countries_factory,
    client,
    admin_token,
):
    countries = await countries_factory(instances=1)

    response = await client.post(
        "/api/v1/vlogs",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "vlogger_id": 5,
            "country_id": countries[0].id,
            "youtube_video_id": "stringstrin",
        },
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "Vlogger does not exist"


async def test_post_vlogs_endpoint_with_invalid_country(
    vloggers_factory, client, admin_token
):
    vloggers = await vloggers_factory(instances=1)

    response = await client.post(
        "/api/v1/vlogs",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "vlogger_id": vloggers[0].id,
            "country_id": 5,
            "youtube_video_id": "stringstrin",
        },
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "Country does not exist"


async def test_post_vlogs_endpoint_with_invalid_video_id(
    vloggers_factory,
    countries_factory,
    client,
    admin_token,
):
    vloggers = await vloggers_factory(instances=1)
    countries = await countries_factory(instances=1)

    response = await client.post(
        "/api/v1/vlogs",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "vlogger_id": vloggers[0].id,
            "country_id": countries[0].id,
            "youtube_video_id": "12345",
        },
    )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


async def test_post_vlogs_endpoint_with_duplicate_video_id(
    vloggers_factory,
    countries_factory,
    vlog,
    client,
    admin_token,
):
    vloggers = await vloggers_factory(instances=1)
    countries = await countries_factory(instances=1)

    response = await client.post(
        "/api/v1/vlogs",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "vlogger_id": vloggers[0].id,
            "country_id": countries[0].id,
            "youtube_video_id": vlog.youtube_video_id,
        },
    )

    assert response.status_code == status.HTTP_409_CONFLICT
    assert response.json()["detail"] == "Youtube Video ID already exists"


async def test_post_vlogs_endpoint_with_no_return_data(
    vloggers_factory,
    countries_factory,
    client,
    admin_token,
):
    vloggers = await vloggers_factory(instances=1)
    countries = await countries_factory(instances=1)

    response = await client.post(
        "/api/v1/vlogs",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "vlogger_id": vloggers[0].id,
            "country_id": countries[0].id,
            "youtube_video_id": "stringstrin",
        },
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "Youtube Data not found"


async def test_post_vlogs_endpoint_success(
    vloggers_factory,
    countries_factory,
    client,
    admin_token,
):
    vloggers = await vloggers_factory(instances=1)
    countries = await countries_factory(instances=1)

    response = await client.post(
        "/api/v1/vlogs",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "vlogger_id": vloggers[0].id,
            "country_id": countries[0].id,
            "youtube_video_id": "dQw4w9WgXcQ",
        },
    )

    assert response.status_code == status.HTTP_201_CREATED

    data = response.json()
    assert len(data) == 10

    assert data["vlogger_id"] == vloggers[0].id
    assert data["country_id"] == countries[0].id
    assert data["youtube_video_id"] == "dQw4w9WgXcQ"
    assert "published_at" in data
    assert (
        data["title"]
        == "Rick Astley - Never Gonna Give You Up (Official Video) (4K Remaster)"
    )
    assert "thumbnail_url" in data
    assert data["language"] == "en"
    assert data["youtube_video_url"] == "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    assert "id" in data
    assert "created_at" in data


# Endpoint PATCH /api/v1/vlogs/{vlog_id}
async def test_patch_vlogs_endpoint_success(
    vloggers_factory, countries_factory, vlog, client, admin_token
):
    vloggers = await vloggers_factory(instances=1)
    countries = await countries_factory(instances=1)

    response = await client.patch(
        f"/api/v1/vlogs/{vlog.id}",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "vlogger_id": vloggers[0].id,
            "country_id": countries[0].id,
        },
    )

    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert len(data) == 10

    assert data["vlogger_id"] == vloggers[0].id
    assert data["country_id"] == countries[0].id
    assert data["youtube_video_id"] == "stringstrin"
    assert "published_at" in data
    assert data["title"] == "test_title"
    assert data["thumbnail_url"] == "test_thumbnail_url"
    assert data["language"] == "en"
    assert data["youtube_video_url"] == "https://www.youtube.com/watch?v=stringstrin"
    assert "id" in data
    assert "created_at" in data


async def test_patch_vlogs_endpoint_with_only_vlogger(
    vloggers_factory, vlog, country, client, admin_token
):
    vloggers = await vloggers_factory(instances=1)

    response = await client.patch(
        f"/api/v1/vlogs/{vlog.id}",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "vlogger_id": vloggers[0].id,
        },
    )

    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert len(data) == 10

    assert data["vlogger_id"] == vloggers[0].id
    assert data["country_id"] == country.id
    assert data["youtube_video_id"] == "stringstrin"
    assert "published_at" in data
    assert data["title"] == "test_title"
    assert data["thumbnail_url"] == "test_thumbnail_url"
    assert data["language"] == "en"
    assert data["youtube_video_url"] == "https://www.youtube.com/watch?v=stringstrin"
    assert "id" in data
    assert "created_at" in data


async def test_patch_vlogs_endpoint_with_only_country(
    countries_factory, vlog, vlogger, client, admin_token
):
    countries = await countries_factory(instances=1)

    response = await client.patch(
        f"/api/v1/vlogs/{vlog.id}",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "country_id": countries[0].id,
        },
    )

    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert len(data) == 10

    assert data["vlogger_id"] == vlogger.id
    assert data["country_id"] == countries[0].id
    assert data["youtube_video_id"] == "stringstrin"
    assert "published_at" in data
    assert data["title"] == "test_title"
    assert data["thumbnail_url"] == "test_thumbnail_url"
    assert data["language"] == "en"
    assert data["youtube_video_url"] == "https://www.youtube.com/watch?v=stringstrin"
    assert "id" in data
    assert "created_at" in data


async def test_patch_vlogs_endpoint_without_access(
    vloggers_factory, countries_factory, vlog, client, user_token
):
    vloggers = await vloggers_factory(instances=1)
    countries = await countries_factory(instances=1)

    response = await client.patch(
        f"/api/v1/vlogs/{vlog.id}",
        headers={"Authorization": f"Bearer {user_token}"},
        json={
            "vlogger_id": vloggers[0].id,
            "country_id": countries[0].id,
        },
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json()["detail"] == "Not authorized"


async def test_patch_vlogs_endpoint_without_token(
    vloggers_factory, countries_factory, vlog, client
):
    vloggers = await vloggers_factory(instances=1)
    countries = await countries_factory(instances=1)

    response = await client.patch(
        f"/api/v1/vlogs/{vlog.id}",
        headers={"Authorization": "Bearer "},
        json={
            "vlogger_id": vloggers[0].id,
            "country_id": countries[0].id,
        },
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json()["detail"] == "Not authenticated"


async def test_patch_vlogs_endpoint_invalid_vlog(
    vloggers_factory, countries_factory, client, admin_token
):
    vloggers = await vloggers_factory(instances=1)
    countries = await countries_factory(instances=1)

    response = await client.patch(
        "/api/v1/vlogs/43445",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "vlogger_id": vloggers[0].id,
            "country_id": countries[0].id,
        },
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "Vlog does not exist"


async def test_patch_vlogs_endpoint_invalid_vlogger(vlog, client, admin_token):
    response = await client.patch(
        f"/api/v1/vlogs/{vlog.id}",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "vlogger_id": 45453,
        },
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "Vlogger does not exist"


async def test_patch_vlogs_endpoint_invalid_country(vlog, client, admin_token):
    response = await client.patch(
        f"/api/v1/vlogs/{vlog.id}",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "country_id": 142,
        },
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "Country does not exist"


async def test_patch_vlogs_endpoint_invalid_type(vlog, client, admin_token):
    response = await client.patch(
        f"/api/v1/vlogs/{vlog.id}",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"vlogger_id": "vlogger", "country_id": "country"},
    )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


# Endpoint DELETE /api/v1/vlogs/{vlogs_id}
async def test_delete_vlogs_endpoint_success(vlog, client, admin_token, db_session):
    assert vlog.id

    response = await client.delete(
        f"/api/v1/vlogs/{vlog.id}",
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    assert response.status_code == status.HTTP_204_NO_CONTENT

    result = await db_session.execute(select(Vlog).where(Vlog.id == vlog.id))
    deleted_vlog = result.scalar_one_or_none()
    assert deleted_vlog is None


async def test_delete_vlogs_endpoint_without_access(vlog, client, user_token):
    assert vlog.id

    response = await client.delete(
        f"/api/v1/vlogs/{vlog.id}",
        headers={"Authorization": f"Bearer {user_token}"},
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json()["detail"] == "Not authorized"
    assert vlog.id


async def test_delete_vlogs_endpoint_without_token(vlog, client):
    assert vlog.id

    response = await client.delete(
        f"/api/v1/vlogs/{vlog.id}", headers={"Authorization": "Bearer "}
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json()["detail"] == "Not authenticated"


async def test_delete_vlogs_endpoint_invalid_vlog(client, admin_token):
    response = await client.delete(
        "/api/v1/vlogs/24342", headers={"Authorization": f"Bearer {admin_token}"}
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "Vlog does not exist"
