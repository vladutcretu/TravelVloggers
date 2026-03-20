from fastapi import status

from app.models.user import User
from sqlalchemy import select


async def test_populate_db_using_endpoint(client):
    """
    Create an object in database using an endpoint.
    """
    response = await client.post(
        "/api/v1/auth/register", json={"email": "TEST@mail.com", "password": "123456"}
    )

    assert response.status_code == status.HTTP_201_CREATED
    assert response.json()["email"] == "test@mail.com"


async def test_unpopulate_db_between_tests(db_session):
    """
    Prove that the previously created object do not exist anymore, since every action is rolled back once the test is finished.
    """
    result = await db_session.execute(select(User))
    users = result.scalars().all()
    assert len(users) == 0


async def test_populate_db_using_operations(db_session):
    """
    Create an object in the database using db_session to test the endpoint's components.
    """
    user = User(email="test@mail.com", password_hash="123456")
    db_session.add(user)
    await db_session.commit()

    result = await db_session.execute(select(User).where(User.email == "test@mail.com"))
    assert result.scalar_one_or_none is not None
