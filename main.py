from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import FastAPI, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.connection import Base, engine, get_db
from app.api.v1 import router as v1_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # On startup
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    # On shutdown
    await engine.dispose()


app = FastAPI(lifespan=lifespan)
app.include_router(v1_router.router) # /api/v1/ routes


@app.get("/")
async def main(db: Annotated[AsyncSession, Depends(get_db)]):
    result = await db.execute(select(1))
    value = result.scalar()
    return {"db_test": value}
