import stripe

from app.core.config import settings


stripe.api_key = settings.STRIPE_SECRET_KEY


class StripeClient:
    async def create_customer(self, *, email: str, user_id: int) -> stripe.Customer:
        customer = stripe.Customer.create(
            email=email,
            metadata={"user_id": str(user_id)},
        )
        return customer

    async def create_membership_checkout(
        self, *, customer_id: str
    ) -> stripe.checkout.Session:
        if settings.STRIPE_MEMBERSHIP_PRICE_ID is None:
            raise ValueError("Stripe membership price ID is not set in settings.")

        session = stripe.checkout.Session.create(
            customer=customer_id,
            mode="subscription",
            line_items=[
                {
                    "price": settings.STRIPE_MEMBERSHIP_PRICE_ID,
                    "quantity": 1,
                }
            ],
            success_url="http://localhost/success",
            cancel_url="http://localhost/cancel",
        )
        return session
