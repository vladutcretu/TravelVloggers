from datetime import datetime, timezone

from fastapi import status

from app.models.vlog import Vlog


# Endpoint GET /api/v2/vloggers/{vlogger_id}
async def test_get_vlogger_endpoint_success(vlogger, client):
    assert vlogger.id

    response = await client.get(f"/api/v2/vloggers/{vlogger.id}")

    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert data["youtube_channel_id"] == "test_channel_id"
    assert data["youtube_channel_name"] == "test_channel_name"
    assert data["youtube_channel_url"] == "test_channel_url"
    assert data["youtube_avatar_url"] == "test_avatar_url"
    assert data["id"] == vlogger.id
    assert data["vlogs_count"] == 0
    assert data["countries_count"] == 0
    assert "created_at" in data


async def test_get_vlogger_endpoint_invalid_vlogger(client):
    response = await client.get("/api/v2/vloggers/53252")

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "Vlogger does not exist"


async def test_get_vlogger_endpoint_invalid_type(client):
    response = await client.get("/api/v2/vloggers/vlogger4")

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
    assert response.json()["detail"][0]["type"] == "int_parsing"


# Endpoint GET /api/v2/vloggers/{vlogger_id}/countries
async def test_get_vlogger_countries_endpoint_success(
    vlogger, client, db_session, countries_factory
):
    countries = await countries_factory(instances=2)

    vlog = Vlog(
        vlogger_id=vlogger.id,
        country_id=countries[0].id,
        youtube_video_id="videoid0001",
        published_at=datetime.now(timezone.utc),
        title="test_title",
        thumbnail_url="test_thumbnail_url",
        language="en",
    )
    db_session.add(vlog)
    await db_session.commit()

    response = await client.get(f"/api/v2/vloggers/{vlogger.id}/countries")

    assert response.status_code == status.HTTP_200_OK
    data = response.json()

    assert len(data["countries"]) == 2

    countries_by_id = {country["id"]: country for country in data["countries"]}

    assert countries_by_id[countries[0].id]["has_vlog"] is True
    assert countries_by_id[countries[1].id]["has_vlog"] is False

    assert data["countries"][0]["id"] == countries[0].id
    assert data["countries"][0]["name"] == countries[0].name
    assert data["countries"][0]["iso_code"] == countries[0].iso_code


async def test_get_vlogger_countries_endpoint_invalid_vlogger(client):
    response = await client.get("/api/v2/vloggers/99999/countries")

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "Vlogger does not exist"


async def test_get_vlogger_countries_endpoint_invalid_type(client):
    response = await client.get("/api/v2/vloggers/invalid/countries")

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
    assert response.json()["detail"][0]["type"] == "int_parsing"
