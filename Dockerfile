FROM ghcr.io/astral-sh/uv:debian-slim

WORKDIR /app

COPY pyproject.toml uv.lock /app/

RUN apt-get update && apt-get install -y ca-certificates && update-ca-certificates
RUN uv sync --locked

COPY . /app/

EXPOSE 8000

CMD ["uv", "run", "fastapi", "dev", "--host", "0.0.0.0", "--port", "8000"]