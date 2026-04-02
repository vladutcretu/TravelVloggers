# TravelVloggers
TravelVloggers is a backend API that aggregates travel-related video content posted on YouTube. It allows users to discover travel vloggers, explore videos recorded in specific countries, and see which countries a particular vlogger has visited.


## Table of Contents
1. [Technology Stack](#technology-stack)
2. [Features](#features)


## Technology Stack
- ⚙️ Backend: [FastAPI](https://fastapi.tiangolo.com) with
    - 🧰 [SQLAlchemy](https://www.sqlalchemy.org) for database interactions.
    - ✅ [Pydantic](https://docs.pydantic.dev/latest/) for data validation.
    - 🐛 [pytest](https://docs.pytest.org/en/stable/) for writing tests.
- 💾 Database: [PostgreSQL](https://www.postgresql.org/).
- 🧩Other tools and libraries:
    - 🗓️ [Trello](https://trello.com/b/GufG4LeA/travelvloggers) for planning work.
    - 🐋 [Docker](https://www.docker.com/) for containerization.
    - 💼 [uv](https://docs.astral.sh/uv/) as the Python package and project manager; see [pyproject.toml](pyproject.toml) for all dependencies.


## Features
The API is designed to evolve through versioned endpoints.
In version v1.0.0 the platform manually curates travel vloggers and their videos, while version v2.0.0 introduces a subscription-based upload system for vloggers who wish to manage their own content. 

For v1.0.0 (fully developed) the main technical objectives were:
- Administrators can manage vloggers profiles and link vlogs to their profiles.
- Integrate YouTube Data API v3 to fetch video metadata such as title, thumbnail, publish date, language.
- Import countries/cities from a reliable external dataset (e.g. GeoNames) to populate database.

For v2.0.0 (currently unplanned) the main technical objectives are:
- Integrate YouTube OAuth to let visitors make their own profiles on the platform.
- Integrate a payment system that allows users to upgrade their account to submit their own vlogs.

Read more about technical planning, design and objectives for each version on [NOTES.md](NOTES.md).