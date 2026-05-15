from datetime import datetime, timezone

from fastapi import status

from app.models.vlog import Vlog


# Endpoint POST /api/v2/vlogs/
async def test_post_vlogs_endpoint_without_token(
    vloggers_factory,
    countries_factory,
    client,
):
    vloggers = await vloggers_factory(instances=1)
    countries = await countries_factory(instances=1)

    response = await client.post(
        "/api/v2/vlogs",
        headers={"Authoriztion": "Bearer "},
        json={
            "vlogger_id": vloggers[0].id,
            "country_id": countries[0].id,
            "youtube_video_id:": "stringstrin",
        },
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json()["detail"] == "Not authenticated"


async def test_post_vlogs_endpoint_with_user_without_vlogger(
    vloggers_factory,
    countries_factory,
    client,
    user_token,
):
    vloggers = await vloggers_factory(instances=1)
    countries = await countries_factory(instances=1)

    response = await client.post(
        "/api/v2/vlogs",
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
    countries_factory,
    client,
    user_with_vlogger,
    vlogger_token,
):
    user, vlogger = user_with_vlogger
    countries = await countries_factory(instances=1)

    response = await client.post(
        "/api/v2/vlogs",
        headers={"Authorization": f"Bearer {vlogger_token}"},
        json={
            "vlogger_id": vlogger.id,
            "country_id": countries[0].id,
        },
    )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


async def test_post_vlogs_endpoint_with_invalid_vlogger(
    vloggers_factory,
    countries_factory,
    client,
    vlogger_token,
):
    other_vlogger = (await vloggers_factory(instances=1))[0]
    countries = await countries_factory(instances=1)

    response = await client.post(
        "/api/v2/vlogs",
        headers={"Authorization": f"Bearer {vlogger_token}"},
        json={
            "vlogger_id": other_vlogger.id,
            "country_id": countries[0].id,
            "youtube_video_id": "stringstrin",
        },
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json()["detail"] == "Not authorized"


async def test_post_vlogs_endpoint_with_invalid_country(
    client,
    user_with_vlogger,
    vlogger_token,
):
    user, vlogger = user_with_vlogger

    response = await client.post(
        "/api/v2/vlogs",
        headers={"Authorization": f"Bearer {vlogger_token}"},
        json={
            "vlogger_id": vlogger.id,
            "country_id": 3235253,
            "youtube_video_id": "stringstrin",
        },
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "Country does not exist"


async def test_post_vlogs_endpoint_with_invalid_video_id(
    countries_factory,
    client,
    user_with_vlogger,
    vlogger_token,
):
    user, vlogger = user_with_vlogger
    countries = await countries_factory(instances=1)

    response = await client.post(
        "/api/v2/vlogs",
        headers={"Authorization": f"Bearer {vlogger_token}"},
        json={
            "vlogger_id": vlogger.id,
            "country_id": countries[0].id,
            "youtube_video_id": "12345",
        },
    )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


async def test_post_vlogs_endpoint_with_duplicate_video_id(
    countries_factory,
    vlog,
    client,
    user_with_vlogger,
    vlogger_token,
):
    user, vlogger = user_with_vlogger
    countries = await countries_factory(instances=1)

    response = await client.post(
        "/api/v2/vlogs",
        headers={"Authorization": f"Bearer {vlogger_token}"},
        json={
            "vlogger_id": vlogger.id,
            "country_id": countries[0].id,
            "youtube_video_id": vlog.youtube_video_id,
        },
    )

    assert response.status_code == status.HTTP_409_CONFLICT
    assert response.json()["detail"] == "Youtube Video ID already exists"


async def test_post_vlogs_endpoint_with_no_return_data(
    countries_factory,
    client,
    mock_youtube_client,
    user_with_vlogger,
    vlogger_token,
):
    user, vlogger = user_with_vlogger
    countries = await countries_factory(instances=1)

    response = await client.post(
        "/api/v2/vlogs",
        headers={"Authorization": f"Bearer {vlogger_token}"},
        json={
            "vlogger_id": vlogger.id,
            "country_id": countries[0].id,
            "youtube_video_id": "stringstrin",
        },
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "Youtube Data not found"


async def test_post_vlogs_endpoint_success(
    countries_factory,
    client,
    mock_youtube_client,
    user_with_vlogger,
    vlogger_token,
):
    user, vlogger = user_with_vlogger
    countries = await countries_factory(instances=1)

    response = await client.post(
        "/api/v2/vlogs",
        headers={"Authorization": f"Bearer {vlogger_token}"},
        json={
            "vlogger_id": vlogger.id,
            "country_id": countries[0].id,
            "youtube_video_id": "dQw4w9WgXcQ",
        },
    )

    assert response.status_code == status.HTTP_201_CREATED

    data = response.json()
    assert len(data) == 10

    assert data["vlogger_id"] == vlogger.id
    assert data["country_id"] == countries[0].id
    assert data["youtube_video_id"] == "dQw4w9WgXcQ"
    assert "published_at" in data
    assert data["title"] == "Test Video"
    assert data["thumbnail_url"] == "https://test.com/thumbnail.jpg"
    assert data["language"] == "en"
    assert data["youtube_video_url"] == "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    assert "id" in data
    assert "created_at" in data


# Endpoint POST /api/v2/vlogs/countries
async def test_get_countries_endpoint_all_false(
    countries_factory,
    client,
):
    countries = await countries_factory(instances=3)

    response = await client.get("/api/v2/vlogs/countries")

    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 3

    for country_data, country in zip(data, countries):
        assert country_data["id"] == country.id
        assert country_data["name"] == country.name
        assert country_data["iso_code"] == country.iso_code
        assert country_data["has_vlog"] is False


async def test_get_countries_endpoint_one_true(
    vloggers_factory,
    countries_factory,
    db_session,
    client,
):
    vloggers = await vloggers_factory(instances=1)
    countries = await countries_factory(instances=3)

    vlog = Vlog(
        vlogger_id=vloggers[0].id,
        country_id=countries[1].id,
        youtube_video_id="dQw4w9WgXcQ",
        published_at=datetime.now(),
        title="Test Video",
        thumbnail_url="https://test.com/thumbnail.jpg",
    )
    db_session.add(vlog)
    await db_session.commit()

    response = await client.get("/api/v2/vlogs/countries")

    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 3

    for country_data, country in zip(data, countries):
        assert country_data["id"] == country.id
        assert country_data["name"] == country.name
        assert country_data["iso_code"] == country.iso_code
        if country.id == countries[1].id:
            assert country_data["has_vlog"] is True
        else:
            assert country_data["has_vlog"] is False


# Endpoint GET /api/v2/vlogs/country/{country_id}
async def test_get_vlogs_by_country_endpoint_without_more(
    vlogs_factory, pagination, country, client
):
    vlogs = await vlogs_factory(instances=pagination.limit)
    for vlog in vlogs:
        vlog.country_id = country.id

    assert vlogs[0].country_id == country.id
    assert vlogs[pagination.limit - 1].country_id == country.id

    response = await client.get(
        f"/api/v2/vlogs/country/{country.id}?skip={pagination.skip}&limit={pagination.limit}&order={pagination.order}"
    )

    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert len(data) == 4  # Vlog items + 3 params
    assert len(data["vlogs"]) == min(len(vlogs), pagination.limit)

    item = data["vlogs"][0]
    assert item["vlogger_id"] == vlogs[0].vlogger_id
    assert item["country_id"] == country.id
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


async def test_get_vlogs_by_country_endpoint_with_more(
    vlogs_factory, pagination, country, client
):
    vlogs = await vlogs_factory(instances=pagination.limit + 1)
    for vlog in vlogs:
        vlog.country_id = country.id

    assert vlogs[0].country_id == country.id
    assert vlogs[pagination.limit - 1].country_id == country.id

    response = await client.get(
        f"/api/v2/vlogs/country/{country.id}?skip={pagination.skip}&limit={pagination.limit}&order={pagination.order}"
    )

    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert len(data) == 4  # Vlog items + 3 params
    assert len(data["vlogs"]) == min(len(vlogs), pagination.limit)

    item = data["vlogs"][0]
    assert item["vlogger_id"] == vlogs[0].vlogger_id
    assert item["country_id"] == country.id
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


async def test_get_vlogs_by_country_endpoint_with_skip(
    vlogs_factory, pagination, country, client
):
    vlogs = await vlogs_factory(instances=pagination.limit)
    for vlog in vlogs:
        vlog.country_id = country.id

    assert vlogs[0].country_id == country.id
    assert vlogs[pagination.limit - 1].country_id == country.id

    pagination.skip = 1

    response = await client.get(
        f"/api/v2/vlogs/country/{country.id}?skip={pagination.skip}&limit={pagination.limit}&order={pagination.order}"
    )

    assert response.status_code == status.HTTP_200_OK

    data = response.json()

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


async def test_get_vlogs_by_country_endpoint_with_limit(
    vlogs_factory, pagination, country, client
):
    vlogs = await vlogs_factory(instances=pagination.limit)
    for vlog in vlogs:
        vlog.country_id = country.id

    assert vlogs[0].country_id == country.id
    assert vlogs[pagination.limit - 1].country_id == country.id

    pagination.limit = 2

    response = await client.get(
        f"/api/v2/vlogs/country/{country.id}?skip={pagination.skip}&limit={pagination.limit}&order={pagination.order}"
    )

    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert len(data["vlogs"]) == min(len(vlogs), pagination.limit)


async def test_get_vlogs_by_country_endpoint_with_order_asc(
    vlogs_factory, pagination, country, client
):
    vlogs = await vlogs_factory(instances=pagination.limit)
    for vlog in vlogs:
        vlog.country_id = country.id

    assert vlogs[0].country_id == country.id
    assert vlogs[pagination.limit - 1].country_id == country.id

    pagination.order = "asc"

    response = await client.get(
        f"/api/v2/vlogs/country/{country.id}?skip={pagination.skip}&limit={pagination.limit}&order={pagination.order}"
    )

    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert len(data["vlogs"]) == min(len(vlogs), pagination.limit)

    vlogs_sorted_desc = sorted(vlogs, key=lambda vlog: vlog.published_at, reverse=False)
    first_returned_vlog = data["vlogs"][0]
    first_published_vlog = vlogs_sorted_desc[0]

    assert first_returned_vlog["id"] == first_published_vlog.id
    assert (
        first_returned_vlog["youtube_video_id"] == first_published_vlog.youtube_video_id
    )


async def test_get_vlogs_by_country_endpoint_with_order_desc(
    vlogs_factory, pagination, country, client
):
    vlogs = await vlogs_factory(instances=pagination.limit)
    for vlog in vlogs:
        vlog.country_id = country.id

    assert vlogs[0].country_id == country.id
    assert vlogs[pagination.limit - 1].country_id == country.id

    pagination.order = "desc"

    response = await client.get(
        f"/api/v2/vlogs/country/{country.id}?skip={pagination.skip}&limit={pagination.limit}&order={pagination.order}"
    )

    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert len(data["vlogs"]) == min(len(vlogs), pagination.limit)

    vlogs_sorted_desc = sorted(vlogs, key=lambda vlog: vlog.published_at, reverse=True)
    first_returned_vlog = data["vlogs"][0]
    last_published_vlog = vlogs_sorted_desc[0]

    assert first_returned_vlog["id"] == last_published_vlog.id
    assert (
        first_returned_vlog["youtube_video_id"] == last_published_vlog.youtube_video_id
    )


async def test_get_vlogs_by_country_endpoint_with_invalid_country(
    vlogs_factory, client
):
    await vlogs_factory(instances=10)

    response = await client.get("/api/v1/vlogs/country/15")

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "Country does not exist"


async def test_get_vlogs_by_country_endpoint_with_invalid_country_type(
    vlogs_factory, pagination, client
):
    await vlogs_factory(instances=pagination.limit)

    response = await client.get("/api/v1/vlogs/country/USA")

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


async def test_get_vlogs_by_country_endpoint_with_skip_invalid(
    vlogs_factory, pagination, country, client
):
    await vlogs_factory(instances=pagination.limit)

    pagination.skip = -1

    response = await client.get(
        f"/api/v2/vlogs/country/{country.id}?skip={pagination.skip}&limit={pagination.limit}&order={pagination.order}"
    )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


async def test_get_vlogs_by_country_endpoint_with_limit_invalid(
    vlogs_factory, pagination, country, client
):
    await vlogs_factory(instances=pagination.limit)

    pagination.limit = -10

    response = await client.get(
        f"/api/v2/vlogs/country/{country.id}?skip={pagination.skip}&limit={pagination.limit}&order={pagination.order}"
    )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


async def test_get_vlogs_by_country_endpoint_with_order_invalid(
    vlogs_factory, pagination, country, client
):
    await vlogs_factory(instances=pagination.limit)

    pagination.order = "alpha"

    response = await client.get(
        f"/api/v2/vlogs/country/{country.id}?skip={pagination.skip}&limit={pagination.limit}&order={pagination.order}"
    )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


async def test_get_vlogs_by_country_endpoint_with_no_vlogs(pagination, country, client):
    response = await client.get(
        f"/api/v2/vlogs/country/{country.id}?skip={pagination.skip}&limit={pagination.limit}&order={pagination.order}"
    )

    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert len(data) == 4  # Vlog items + 3 params
    assert len(data["vlogs"]) == 0

    assert data["skip"] == pagination.skip
    assert data["limit"] == pagination.limit
    assert data["has_more"] is False


async def test_get_vlogs_by_country_endpoint_with_language_filter_no_results(
    db_session, vlogger, country, pagination, client
):
    language = "en"

    vlog = Vlog(
        vlogger_id=vlogger.id,
        country_id=country.id,
        youtube_video_id="dQw4w9WgXcQ",
        published_at=datetime.now(timezone.utc),
        title="title_test_with_language",
        thumbnail_url="thumbnail_test_with_language",
        language=f"{language}",
    )
    db_session.add(vlog)
    await db_session.commit()

    response = await client.get(
        f"/api/v2/vlogs/country/{country.id}?skip={pagination.skip}&limit={pagination.limit}&order={pagination.order}&language={language + language}"
    )

    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert len(data) == 4  # Vlog items + 3 params

    assert len(data["vlogs"]) == 0
    assert data["vlogs"] == []
    assert data["skip"] == pagination.skip
    assert data["limit"] == pagination.limit
    assert data["has_more"] is False


async def test_get_vlogs_by_country_endpoint_with_language_filter_with_results(
    db_session, vlogger, country, pagination, client
):
    language = "en"

    vlog = Vlog(
        vlogger_id=vlogger.id,
        country_id=country.id,
        youtube_video_id="dQw4w9WgXcQ",
        published_at=datetime.now(timezone.utc),
        title="title_test_with_language",
        thumbnail_url="thumbnail_test_with_language",
        language=f"{language}",
    )
    db_session.add(vlog)
    await db_session.commit()

    response = await client.get(
        f"/api/v2/vlogs/country/{country.id}?skip={pagination.skip}&limit={pagination.limit}&order={pagination.order}&language={language}"
    )

    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert len(data) == 4  # Vlog items + 3 params

    item = data["vlogs"][0]
    assert item["vlogger_id"] == vlogger.id
    assert item["country_id"] == country.id
    assert item["youtube_video_id"] == vlog.youtube_video_id
    assert item["youtube_video_url"] == vlog.youtube_video_url
    assert "published_at" in item
    assert item["title"] == "title_test_with_language"
    assert item["thumbnail_url"] == "thumbnail_test_with_language"
    assert item["language"] == language
    assert "id" in item
    assert "created_at" in item

    assert data["skip"] == pagination.skip
    assert data["limit"] == pagination.limit
    assert data["has_more"] is False


async def test_get_vlogs_by_country_endpoint_with_year_filter_no_results(
    db_session, vlogger, country, pagination, client
):
    publish_year = 2023

    vlog = Vlog(
        vlogger_id=vlogger.id,
        country_id=country.id,
        youtube_video_id="dQw4w9WgXcQ",
        published_at=datetime.now(timezone.utc),
        title="title_test_with_publish_year",
        thumbnail_url="thumbnail_test_with_publish_year",
    )
    db_session.add(vlog)
    await db_session.commit()

    response = await client.get(
        f"/api/v2/vlogs/country/{country.id}?skip={pagination.skip}&limit={pagination.limit}&order={pagination.order}&publish_year={publish_year}"
    )

    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert len(data) == 4  # Vlog items + 3 params

    assert len(data["vlogs"]) == 0
    assert data["vlogs"] == []
    assert data["skip"] == pagination.skip
    assert data["limit"] == pagination.limit
    assert data["has_more"] is False


async def test_get_vlogs_by_country_endpoint_with_year_filter_with_results(
    db_session, vlogger, country, pagination, client
):
    publish_year = 2026

    vlog = Vlog(
        vlogger_id=vlogger.id,
        country_id=country.id,
        youtube_video_id="dQw4w9WgXcQ",
        published_at=datetime.now(timezone.utc),
        title="title_test_with_publish_year",
        thumbnail_url="thumbnail_test_with_publish_year",
    )
    db_session.add(vlog)
    await db_session.commit()

    response = await client.get(
        f"/api/v2/vlogs/country/{country.id}?skip={pagination.skip}&limit={pagination.limit}&order={pagination.order}&publish_year={publish_year}"
    )

    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert len(data) == 4  # Vlog items + 3 params

    item = data["vlogs"][0]
    assert item["vlogger_id"] == vlogger.id
    assert item["country_id"] == country.id
    assert item["youtube_video_id"] == vlog.youtube_video_id
    assert item["youtube_video_url"] == vlog.youtube_video_url
    assert "published_at" in item
    assert item["title"] == "title_test_with_publish_year"
    assert item["thumbnail_url"] == "thumbnail_test_with_publish_year"
    assert item["language"] is None
    assert "id" in item
    assert "created_at" in item

    assert data["skip"] == pagination.skip
    assert data["limit"] == pagination.limit
    assert data["has_more"] is False
