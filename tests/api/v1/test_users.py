from fastapi import status


# Endpoint GET /api/v1/users
async def test_get_users_endpoint_success_single_user(client, superuser_token):
    response = await client.get(
        "/api/v1/users", headers={"Authorization": f"Bearer {superuser_token}"}
    )

    assert response.status_code == status.HTTP_200_OK

    data = response.json()

    assert len(data) == 1
    item = data[0]

    assert "id" in item
    assert "email" in item
    assert "password_hash" not in item
    assert "is_admin" in item
    assert "is_superuser" in item


async def test_get_users_endpoint_success_multiple_users(
    client, admin, user, superuser_token
):
    assert admin.id
    assert user.id

    response = await client.get(
        "/api/v1/users", headers={"Authorization": f"Bearer {superuser_token}"}
    )

    assert response.status_code == status.HTTP_200_OK

    data = response.json()

    assert len(data) > 1
    item = data[1]

    assert "id" in item
    assert "email" in item
    assert "password_hash" not in item
    assert "is_admin" in item
    assert "is_superuser" in item


async def test_get_users_endpoint_as_admin(client, admin_token):
    response = await client.get(
        "/api/v1/users", headers={"Authorization": f"Bearer {admin_token}"}
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json()["detail"] == "Not authorized"


async def test_get_users_endpoint_as_user(client, user_token):
    response = await client.get(
        "/api/v1/users", headers={"Authorization": f"Bearer {user_token}"}
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json()["detail"] == "Not authorized"


async def test_get_users_endpoint_without_token(client):
    response = await client.get("/api/v1/users", headers={"Authorization": "Bearer "})

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json()["detail"] == "Not authenticated"


# Endpoint PATCH /api/v1/users
async def test_patch_users_endpoint_success_user_to_admin(
    client, user, superuser_token
):
    assert not user.is_admin

    response = await client.patch(
        f"/api/v1/users/{user.id}",
        headers={"Authorization": f"Bearer {superuser_token}"},
        json={"is_admin": True},
    )

    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert "id" in data
    assert "email" in data
    assert data["is_admin"]
    assert "is_superuser" in data
    assert "created_at" in data


async def test_patch_users_endpoint_success_admin_to_user(
    client, admin, superuser_token
):
    assert admin.is_admin

    response = await client.patch(
        f"/api/v1/users/{admin.id}",
        headers={"Authorization": f"Bearer {superuser_token}"},
        json={"is_admin": False},
    )

    assert response.status_code == status.HTTP_200_OK
    assert not response.json()["is_admin"]


async def test_patch_users_endpoint_as_admin(client, user, admin_token):
    assert not user.is_admin

    response = await client.patch(
        f"/api/v1/users/{user.id}",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"is_admin": True},
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json()["detail"] == "Not authorized"


async def test_patch_users_endpoint_as_user(client, admin, user_token):
    assert admin.is_admin

    response = await client.patch(
        f"/api/v1/users/{admin.id}",
        headers={"Authorization": f"Bearer {user_token}"},
        json={"is_admin": False},
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json()["detail"] == "Not authorized"


async def test_patch_users_endpoint_with_invalid_user(client, superuser_token):
    response = await client.patch(
        "/api/v1/users/34682",
        headers={"Authorization": f"Bearer {superuser_token}"},
        json={"is_admin": True},
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "User does not exist"


async def test_patch_users_endpoint_with_multiple_fields(client, user, superuser_token):
    assert not user.is_admin

    response = await client.patch(
        f"/api/v1/users/{user.id}",
        headers={"Authorization": f"Bearer {superuser_token}"},
        json={"email": "test@mail.com", "is_admin": True, "is_superuser": True},
    )

    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert data["email"] == "user@mail.com"
    assert data["is_admin"]
    assert not data["is_superuser"]


async def test_patch_users_endpoint_with_int(client, user, superuser_token):
    assert not user.is_admin

    response = await client.patch(
        f"/api/v1/users/{user.id}",
        headers={"Authorization": f"Bearer {superuser_token}"},
        json={"is_admin": 1},
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["is_admin"]


async def test_patch_users_endpoint_with_str(client, user, superuser_token):
    assert not user.is_admin

    response = await client.patch(
        f"/api/v1/users/{user.id}",
        headers={"Authorization": f"Bearer {superuser_token}"},
        json={"is_admin": "true"},
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["is_admin"]
