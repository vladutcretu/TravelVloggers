from datetime import datetime, timezone

from app.repositories.v1.users import UsersRepository
from app.models.user import User
from app.schemas.v1.user import UserUpdate
from app.core.exceptions import UserDoesntExistError
from app.clients.stripe import StripeClient
from app.core.config import settings


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

    async def subscribe_membership(self, user: User) -> str | None:
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
            customer = stripe_client.create_customer(email=user.email, user_id=user.id)
            updated_user = await self.repository.update_stripe_customer_id(
                user, customer.id
            )
            customer_id = updated_user.stripe_customer_id  # type: ignore

        if customer_id is None:
            raise ValueError("Failed to create Stripe customer for the user.")

        # create checkout session
        session = stripe_client.create_membership_checkout(customer_id=customer_id)
        # return checkout url
        return session.url

    async def process_stripe_webhook(self, payload: bytes, sig_header: str) -> None:
        stripe_client = StripeClient()

        if settings.STRIPE_WEBHOOK_SECRET is None:
            raise ValueError("Stripe webhook secret is not set in settings.")

        event = stripe_client.construct_webhook_event(
            payload=payload,
            sig_header=sig_header,
            secret=settings.STRIPE_WEBHOOK_SECRET,
        )

        # handle subscription created/updated events
        if event.type in (
            "customer.subscription.created",
            "customer.subscription.updated",
        ):
            subscription = event.data.object

            customer_id = str(subscription.customer)
            subscription_id = str(subscription.id)
            if not customer_id or not subscription_id:
                raise ValueError(
                    "Invalid Stripe webhook event data: missing subscription or customer ID."
                )

            # extract from Event data of customer.subscription.created/updated
            period_end = subscription.items.data[0].current_period_end
            if not period_end:
                raise ValueError("Missing current_period_end in subscription item")

            # find user by stripe customer id and update membership info
            user = await self.repository.get_user_by_stripe_customer_id(customer_id)
            if not user:
                raise UserDoesntExistError()

            await self.repository.update_membership(
                user=user,
                subscription_id=subscription_id,
                membership_expires_at=datetime.fromtimestamp(
                    period_end,
                    tz=timezone.utc,
                ),
            )

            return

        return
