# faber-template

An early-stage FastAPI service template with a layered structure, Beanie/MongoDB persistence, and Pydantic-based configuration.

[简体中文](README.md)

## Overview

`faber-template` is intended as a clean and extensible foundation for Python Web API services. It now provides a runnable FastAPI application factory, an ASGI entry point, MongoDB/Beanie startup and shutdown lifecycle management, and health endpoints with separate liveness and readiness semantics.

Current version: `0.1.0`

## Project Status

| Component | Status | Description |
| --- | --- | --- |
| Python project and dependency lock | Complete | Managed through `pyproject.toml` and `uv.lock` |
| Application settings | Complete | Reads values from `.env` and system environment variables |
| Layered directories | Established | Directories are reserved for APIs, models, repositories, services, database code, and middleware |
| FastAPI application factory | Complete | Creates the app, mounts the root router, and manages long-lived resources through lifespan |
| API router and health endpoints | Complete | Exposes separate liveness and MongoDB readiness endpoints |
| MongoDB / Beanie initialization | Complete | Connects and initializes models at startup, cleans up failures, and closes gracefully at shutdown |
| Redis integration | Out of current scope | No Redis dependency, setting, or runtime code is currently included |
| Tests and deployment | Partially complete | Settings, database lifecycle, app startup, and health checks are covered; container and production deployment configuration are pending |

MongoDB is a startup dependency. If the application cannot connect or initialize Beanie during startup, startup fails fast instead of serving as ready.

## Technology Stack

- Python `>=3.10.11,<3.14`
- FastAPI `0.141.1`
- Beanie `2.2.0`
- Pydantic `2.13.4`
- Pydantic Settings `2.15.0`
- MongoDB connected at application startup and initialized through Beanie
- uv as the recommended dependency and virtual environment manager

## Project Structure

```text
faber-template/
├── app/
│   ├── api/                 # API routers and endpoints
│   │   └── health/          # Health-check module
│   ├── core/                # Core configuration and application mechanisms
│   │   ├── config.py        # Pydantic Settings model
│   │   └── lifespan.py      # Application-level resource lifecycle
│   ├── database/            # Database connection and initialization
│   ├── middleware/          # HTTP middleware
│   ├── models/              # Beanie document models
│   ├── repositories/        # Data-access layer
│   ├── schemas/             # Request and response models, including health responses
│   ├── services/            # Business-logic layer, including dependency checks
│   ├── shared/              # Shared cross-module code
│   ├── utils/               # General utilities
│   └── app_factory.py       # FastAPI application factory
├── tests/                   # Standard-library unit tests
├── .env.example             # Environment variable example
├── main.py                  # ASGI application and local startup entry point
├── pyproject.toml           # Project metadata and direct dependencies
└── uv.lock                  # Complete dependency lock file
```

## Quick Start

### 1. Requirements

Install the following tools first:

- Python 3.10.11 through 3.13
- [uv](https://docs.astral.sh/uv/)

MongoDB must be running before validating the database connection.

### 2. Install dependencies

```bash
uv sync --locked
```

This command creates or updates the local `.venv` and installs the exact dependency versions recorded in `uv.lock`.

### 3. Configure environment variables

```bash
cp .env.example .env
```

`.env.example` lists all currently supported settings. Copy it and adjust the values for the target environment:

```dotenv
APP_NAME=faber-template
APP_DESCRIPTION=A FastAPI service template powered by Beanie and MongoDB
APP_VERSION=0.1.0
APP_RUN_MODE=production
APP_HOST=127.0.0.1
APP_PORT=8000
APP_DEBUG=false
APP_API_DOCS=/docs
APP_API_REDOC=/redoc
APP_API_OPENAPI=/openapi.json
MONGODB_URI=mongodb://127.0.0.1:27017
MONGODB_DATABASE=faber-template
MONGODB_SERVER_SELECTION_TIMEOUT_MS=5000
```

### 4. Start the application

```bash
uv run python main.py
```

You can also use the Uvicorn CLI:

```bash
uv run uvicorn main:app --host 127.0.0.1 --port 8000
```

The configured MongoDB instance must be reachable before startup. The app pings MongoDB and initializes Beanie first; either failure aborts startup.

### 5. Call the health endpoints

```bash
curl http://127.0.0.1:8000/health/live
curl http://127.0.0.1:8000/health/ready
```

| Endpoint | Successful response | Semantics |
| --- | --- | --- |
| `GET /health/live` | `200 {"status":"ok"}` | Checks only the application process and does not query external dependencies |
| `GET /health/ready` | `200 {"status":"ready","checks":{"mongodb":"up"}}` | Pings MongoDB on every request |
| `GET /health/ready` | `503 {"status":"not_ready","checks":{"mongodb":"down"}}` | MongoDB fails the ping or raises a connection error |

Neither readiness responses nor logs expose the MongoDB URI, username, or password.

### 6. Validate the MongoDB connection separately

```bash
uv run python - <<'PY'
import asyncio
from app.database import mongodb

async def main():
    await mongodb.connect()
    try:
        print(await mongodb.ping())
    finally:
        await mongodb.disconnect()

asyncio.run(main())
PY
```

The application-level lifespan in `app/core/lifespan.py` manages MongoDB, while the application factory only injects resources and assembles FastAPI. After adding a Beanie `Document` model, register it in `app.models.DOCUMENT_MODELS`.

## Configuration

Environment variable names are case-insensitive, and system environment variables override values from `.env`. `APP_RUN_MODE` accepts only `development`, `testing`, or `production`; `get_settings()` returns the corresponding settings type. The result is cached, so application code should read configuration through this function:

```python
from app.core.config import get_settings

settings = get_settings()
print(settings.APP_NAME)
print(settings.MONGODB_URI)
```

The `.env` path is resolved from the project root, so loading still works when the process starts from another working directory. Set `APP_API_DOCS`, `APP_API_REDOC`, or `APP_API_OPENAPI` to `null` to disable the corresponding endpoint.

| Run mode | Settings type | Default `APP_DEBUG` for the type |
| --- | --- | --- |
| `development` | `DevelopmentSettings` | `true` |
| `testing` | `TestingSettings` | `false` |
| `production` | `ProductionSettings` | `false` |

If neither the system environment nor `.env` provides `APP_RUN_MODE`, the environment selector falls back to `development`; the repository's `.env.example` explicitly uses `production`. Any explicit `APP_DEBUG` value overrides the type default shown above.

| Variable | Default | Purpose |
| --- | --- | --- |
| `APP_NAME` | `faber-template` | Application name |
| `APP_DESCRIPTION` | Chinese project description | OpenAPI and application description |
| `APP_VERSION` | `0.1.0` | Application version |
| `APP_RUN_MODE` | `production` | Runtime mode: `development`, `testing`, or `production` |
| `APP_HOST` | `127.0.0.1` | Uvicorn bind host used by the local startup entry point |
| `APP_PORT` | `8000` | Local startup port, constrained to 1-65535 |
| `APP_DEBUG` | `false` | Debug flag |
| `APP_API_DOCS` | `None` | Swagger UI path; set it to `null` to disable the endpoint |
| `APP_API_REDOC` | `None` | ReDoc path; set it to `null` to disable the endpoint |
| `APP_API_OPENAPI` | `None` | OpenAPI JSON path; set it to `null` to disable the endpoint |
| `MONGODB_URI` | `mongodb://127.0.0.1:27017` | MongoDB connection URI |
| `MONGODB_DATABASE` | `faber-template` | MongoDB database name |
| `MONGODB_SERVER_SELECTION_TIMEOUT_MS` | `5000` | MongoDB server-selection timeout in milliseconds |

Do not commit a `.env` file containing credentials or production addresses. The current `.gitignore` already excludes `.env`.

## Tests and Validation

```bash
uv lock --check
uv run python -m unittest discover -s tests -v
uv run python -m compileall -q app tests
```

Unit tests use a mocked database, require no local MongoDB, and write no data. The separate MongoDB connection command above is a real-dependency check that only runs `ping` and Beanie initialization.

## Recommended Implementation Order

1. Add business schemas, services, repositories, and models as real requirements emerge, and register each new Beanie document model.
2. Decide whether Redis is actually required so the project description and implementation remain consistent.
3. Add a stable API error envelope, logging configuration, and observability.
4. Add containerization, production startup settings, and continuous integration for the target deployment environment.

## Development Conventions

- Keep protocol handling and parameter parsing in the API layer, and place business logic in `services/`.
- Keep data-access details in `repositories/` and Beanie document models in `models/`.
- Define request and response structures in `schemas/` instead of exposing persistence models as public API contracts.
- Update both `.env.example` and the documentation whenever a setting is added.
- Before committing, validate the lock file and run all available tests or static checks.

## License

The repository does not currently include a standalone `LICENSE` file. Do not assume redistribution or commercial-use rights until a license is explicitly added.
