# run with: docker-compose exec app uv run python -m scripts.seed_countries

from pathlib import Path
import json
import asyncio

from sqlalchemy import select

from app.db.connection import async_session, engine, Base
from app.models.vlog import Country


# countries.json should have same root as seed_countries.py
json_path = Path(__file__).parent / "countries.json"


async def seed_countries():
    """
    Populate database with data from countries.json.
    The file structure is: [{"name": "string", "iso_code": "2-UPPER chars"}, {}]
    """
    async with async_session() as session:
        with open(json_path, "r", encoding="utf-8") as f:
            countries = json.load(f)

        result = await session.execute(select(Country.iso_code))
        existing_iso_codes = set(result.scalars().all())

        countries_to_add = [
            Country(name=country["name"], iso_code=country["iso_code"].upper())
            for country in countries
            if country["iso_code"] not in existing_iso_codes
        ]

        if countries_to_add:
            session.add_all(countries_to_add)
            await session.commit()
            print(f"Inserted {len(countries_to_add)} countries into database")
        else:
            print("No new countries to insert into database")


async def main():
    """
    Create countries table and start populate it.
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    await seed_countries()


if __name__ == "__main__":
    asyncio.run(main())
