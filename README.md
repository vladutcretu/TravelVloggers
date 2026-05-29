# TravelVloggers
TravelVloggers is a backend API that aggregates travel-related video content posted on YouTube. It allows users to discover travel vloggers, explore videos recorded in specific countries, and see which countries a particular vlogger has visited.


## Table of Contents
1. [Technology Stack](#technology-stack)
2. [Features](#features)
3. [Local installation](#local-installation)


## Technology Stack
- ⚙️ Backend: [FastAPI](https://fastapi.tiangolo.com) with
    - 🧰 [SQLAlchemy](https://www.sqlalchemy.org) for database interactions.
    - ✅ [Pydantic](https://docs.pydantic.dev/latest/) for data validation.
    - 🐛 [pytest](https://docs.pytest.org/en/stable/) for writing tests.
    - 🧶 [Ruff](https://docs.astral.sh/ruff/) for linting and code formatting.
- 💾 Database: [PostgreSQL](https://www.postgresql.org/).
- 🧩Other tools and libraries:
    - 🗓️ [Trello](https://trello.com/b/GufG4LeA/travelvloggers) for planning work.
    - 🐋 [Docker](https://www.docker.com/) for containerization.
    - 🟥 [Redis](https://pypi.org/project/redis/) for caching.
    - 💳 [Stripe SDK](https://docs.stripe.com/development) to integrate realistic payment process.
    - 💼 [uv](https://docs.astral.sh/uv/) as the Python package and project manager; see [pyproject.toml](pyproject.toml) for all dependencies.


## Features
The API is designed to evolve through versioned endpoints.
In version v1.0.0 the platform manually curates travel vloggers and their videos, while version v2.0.0 introduces a subscription-based upload system for vloggers who wish to manage their own content. 

For v1.0.0 (fully developed) the main technical objectives were:
- Administrators can manage vloggers profiles and link vlogs to their profiles.
- Integrate YouTube Data API v3 to fetch video metadata such as title, thumbnail, publish date, language.
- Import countries/cities from a reliable external dataset (e.g. GeoNames) to populate database.

For v2.0.0 (fully developed) the main technical objectives were:
- Integrate YouTube OAuth to let visitors make their own profiles on the platform.
- YouTube upload sync and cached (with Redis) upload retrieval for authenticated vloggers.
- Integrate a payment system (with Stripe) that allows users to upgrade their account to submit their own vlogs.

After releasing both v1.0.0 and v2.0.0 the API endpoints are:
![API endpoints design](https://i.imgur.com/yXEdZ5b.jpeg)

Read more about technical planning, design and objectives for each version on [NOTES.md](NOTES.md).


## Local installation
1. Clone the repository and navigate into the project folder:
   ```bash
   git clone https://github.com/vladutcretu/TravelVloggers.git
   cd TravelVloggers
   ```
2. Create a `.env` file in the TravelVloggers root with the following content:
    ```env
        POSTGRES_USER=
        POSTGRES_PASSWORD=
        POSTGRES_DB=

        POSTGRES_DB_TEST=

        SUPERUSER_EMAIL=

        ACCESS_TOKEN_SECRET_KEY=

        YOUTUBE_APP_API_KEY=

        GOOGLE_APP_CLIENT_ID=

        STRIPE_SECRET_KEY=
        STRIPE_MEMBERSHIP_PRICE_ID=
        STRIPE_WEBHOOK_SECRET=
    ```
3. Build and run the containers:
   ```bash
   docker-compose up --build -d
   ```
4. Open your web browser and navigate to: http://127.0.0.1:8000/docs/ for OpenAPI documentation.