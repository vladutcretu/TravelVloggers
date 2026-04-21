from fastapi import APIRouter

from app.api.v2.endpoints import auth, vloggers


router = APIRouter(prefix="/api/v2")
router.include_router(auth.router)
router.include_router(vloggers.router)
