from fastapi import status

from app.models.user import User


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
    client, db_session, superuser_token
):
    user = User(email="user@mail.com", password_hash="123456")
    db_session.add(user)
    await db_session.commit()

    admin = User(email="admin@mail.com", password_hash="123456", is_admin=True)
    db_session.add(admin)
    await db_session.commit()

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
