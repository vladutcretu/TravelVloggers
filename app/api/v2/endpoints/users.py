from fastapi import APIRouter, status, HTTPException, Request, Header

from app.api.dependencies import CurrentUser, DatabaseSession
from app.repositories.users import UsersRepository
from app.services.users import UsersService, UserDoesntExistError


payments = APIRouter(prefix="/payments", tags=["User Payments"])


@payments.post("/membership-subscribe", status_code=status.HTTP_200_OK)
async def subscribe_membership(current_user: CurrentUser, db: DatabaseSession):
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated"
        )

    repository = UsersRepository(db)
    service = UsersService(repository)

    try:
        checkout_url = await service.subscribe_membership(current_user)
    except UserDoesntExistError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User does not exist"
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    return {"checkout_url": checkout_url}


@payments.post("/stripe/webhook", status_code=status.HTTP_200_OK)
async def stripe_webhook(
    request: Request,
    db: DatabaseSession,
    stripe_signature: str = Header(alias="Stripe-Signature"),
):
    repository = UsersRepository(db)
    service = UsersService(repository)

    payload = await request.body()

    try:
        await service.process_stripe_webhook(
            payload=payload, sig_header=stripe_signature
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    return {"message": "Webhook processed successfully"}
