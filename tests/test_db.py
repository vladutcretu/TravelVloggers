async def test_main(client):
    response = await client.get("/")

    assert response.status_code == 200
    assert response.json()["db_test"] == 1
