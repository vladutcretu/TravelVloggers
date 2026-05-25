from fastapi import status


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
