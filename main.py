from contextlib import asynccontextmanager

from fastapi import FastAPI, Request

from app.db.connection import Base, engine
from app.db.redis import get_redis_client
from app.api.v1 import router as v1_router
from app.api.v2 import router as v2_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # On startup
    app.state.redis = get_redis_client()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    # On shutdown
    await app.state.redis.close()
    await engine.dispose()


app = FastAPI(lifespan=lifespan)
app.include_router(v1_router.router)  # /api/v1/ routes
app.include_router(v2_router.router)  # /api/v2/ routes


@app.get("/redis")
async def test_redis(request: Request):
    redis = request.app.state.redis

    await redis.set("test", "ok")
    value = await redis.get("test")
    return value
