from fastapi import status


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
