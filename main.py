from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import FastAPI, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.connection import Base, engine, get_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    # On startup
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    # On shutdown
    await engine.dispose()


app = FastAPI(lifespan=lifespan)


@app.get("/")
async def main(db: Annotated[AsyncSession, Depends(get_db)]):
    result = await db.execute(select(1))
    value = result.scalar()
    return {"db_test": value}
