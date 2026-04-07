from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.db.connection import Base, engine
from app.api.v1 import router as v1_router
from app.api.v2 import router as v2_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # On startup
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    # On shutdown
    await engine.dispose()


app = FastAPI(lifespan=lifespan)
app.include_router(v1_router.router)  # /api/v1/ routes
app.include_router(v2_router.router)  # /api/v2/ routes
