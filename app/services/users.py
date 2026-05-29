from datetime import datetime, timezone

from app.repositories.users import UsersRepository
from app.models.user import User
from app.schemas.v1.user import UserUpdate
from app.core.exceptions import UserDoesntExistError
from app.clients.stripe import StripeClient


class UsersService:
    def __init__(self, repository: UsersRepository):
        self.repository = repository

    async def get_users(self) -> list[User]:
        return await self.repository.get_users()

    async def get_user_by_id(self, user_id: int) -> User:
        user = await self.repository.get_user_by_id(user_id)
        if user is None:
            raise UserDoesntExistError()
        return user

    async def update_user(self, user: User, user_data: UserUpdate) -> User:
        updated_data = user_data.model_dump(exclude_unset=True)
        for field, value in updated_data.items():
            setattr(user, field, value)
        return await self.repository.update_user(user)

    async def delete_user(self, user: User) -> None:
        return await self.repository.delete_user(user)

    async def subscribe_membership(self, user: User):
        stripe_client = StripeClient()

        # check if user has already active membership
        if user.membership_expires_at and user.membership_expires_at > datetime.now(
            timezone.utc
        ):
            raise ValueError("User already has an active membership.")

        # check if user has a stripe customer id
        customer_id = user.stripe_customer_id
        if customer_id is None:
            # create customer in stripe and save customer id in db
            customer = await stripe_client.create_customer(
                email=user.email, user_id=user.id
            )
            updated_user = await self.repository.update_stripe_customer_id(
                user, customer.id
            )
            customer_id = updated_user.stripe_customer_id

        if customer_id is None:
            raise ValueError("Failed to create Stripe customer for the user.")

        # create checkout session
        session = await stripe_client.create_membership_checkout(
            customer_id=customer_id
        )
        # return checkout url
        return session.url
