from fastapi import status


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
