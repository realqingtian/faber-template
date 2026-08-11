# faber-template

An early-stage FastAPI service template with a layered structure, Beanie/MongoDB-oriented persistence, and Pydantic-based configuration.

[简体中文](README.md)

## Overview

`faber-template` is intended as a clean and extensible foundation for Python Web API services. The repository currently includes project metadata, locked dependencies, a layered directory structure, and an application settings model. It is still at the scaffold stage and does not yet expose a runnable FastAPI application.

Current version: `0.1.0`

## Project Status

| Component | Status | Description |
| --- | --- | --- |
| Python project and dependency lock | Complete | Managed through `pyproject.toml` and `uv.lock` |
| Application settings | Complete | Reads values from `.env` and system environment variables |
| Layered directories | Established | Directories are reserved for APIs, models, repositories, services, database code, and middleware |
| FastAPI application factory | Pending | `app/app_factory.py` does not yet create an application instance |
| API router and health endpoint | Pending | The corresponding files exist but contain no endpoints |
| MongoDB / Beanie initialization | Complete | Supports connection, ping, model registration, failure cleanup, and graceful shutdown |
| Redis integration | Pending | Redis is mentioned in the project description but is not included as a dependency or setting |
| Tests and deployment | Partially complete | Configuration tests are included; container and production deployment configuration are pending |

The current code can install its dependencies and validate configuration loading, but it cannot yet run as an HTTP service.

## Technology Stack

- Python `>=3.10.11,<3.14`
- FastAPI `0.141.1`
- Beanie `2.2.0`
- Pydantic `2.13.4`
- Pydantic Settings `2.15.0`
- MongoDB with Beanie as the persistence layer
- uv as the recommended dependency and virtual environment manager

## Project Structure

```text
faber-template/
├── app/
│   ├── api/                 # API routers and endpoints
│   │   └── health/          # Health-check module
│   ├── core/                # Core configuration
│   │   └── config.py        # Pydantic Settings model
│   ├── database/            # Database connection and initialization
│   ├── middleware/          # HTTP middleware
│   ├── models/              # Beanie document models
│   ├── repositories/        # Data-access layer
│   ├── schemas/             # Request and response models
│   ├── services/            # Business-logic layer
│   ├── shared/              # Shared cross-module code
│   ├── utils/               # General utilities
│   └── app_factory.py       # FastAPI application factory (pending)
├── tests/                   # Standard-library unit tests
├── .env.example             # Environment variable example
├── main.py                  # Application entry point (pending)
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
APP_DESCRIPTION=A FastAPI service template powered by Beanie and Redis
APP_VERSION=0.1.0
APP_RUN_MODE=production
APP_DEBUG=false
APP_API_DOCS=/docs
APP_API_REDOC=/redoc
MONGODB_URI=mongodb://127.0.0.1:27017
MONGODB_DATABASE=faber-template
MONGODB_SERVER_SELECTION_TIMEOUT_MS=5000
```

### 4. Validate configuration loading

```bash
uv run python -c "from app.core.config import get_settings; print(get_settings().model_dump())"
```

If this command prints a settings dictionary, the dependencies and implemented configuration layer are working correctly.

### 5. Validate the MongoDB connection

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

The FastAPI application factory can compose `mongodb_lifespan()` in its lifespan handler. After adding a Beanie `Document` model, register it in `app.models.DOCUMENT_MODELS`.

## Configuration

Environment variable names are case-insensitive, and system environment variables override values from `.env`. `APP_RUN_MODE` accepts only `development`, `testing`, or `production`; `get_settings()` returns the corresponding settings type. The result is cached, so application code should read configuration through this function:

```python
from app.core.config import get_settings

settings = get_settings()
print(settings.APP_NAME)
print(settings.MONGODB_URI)
```

The `.env` path is resolved from the project root, so loading still works when the process starts from another working directory. Set `APP_API_DOCS` or `APP_API_REDOC` to `null` to disable the corresponding documentation endpoint.

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
| `APP_DEBUG` | `false` | Debug flag |
| `APP_API_DOCS` | `None` | Swagger UI path; effective after the application factory is implemented |
| `APP_API_REDOC` | `None` | ReDoc path; effective after the application factory is implemented |
| `MONGODB_URI` | `mongodb://127.0.0.1:27017` | MongoDB connection URI |
| `MONGODB_DATABASE` | `faber-template` | MongoDB database name |
| `MONGODB_SERVER_SELECTION_TIMEOUT_MS` | `5000` | MongoDB server-selection timeout in milliseconds |

Do not commit a `.env` file containing credentials or production addresses. The current `.gitignore` already excludes `.env`.

## Recommended Implementation Order

1. Create the FastAPI application and lifecycle management in `app/app_factory.py`.
2. Define the root router in `app/api/router.py` and implement the health endpoint.
3. Expose an ASGI `app` from `main.py` and add an ASGI server such as Uvicorn.
4. Decide whether Redis is actually required so the project description and implementation remain consistent.
5. Add tests for subsequent modules, plus code-quality checks, containerization, and deployment configuration.

## Development Conventions

- Keep protocol handling and parameter parsing in the API layer, and place business logic in `services/`.
- Keep data-access details in `repositories/` and Beanie document models in `models/`.
- Define request and response structures in `schemas/` instead of exposing persistence models as public API contracts.
- Update both `.env.example` and the documentation whenever a setting is added.
- Before committing, validate the lock file and run all available tests or static checks.

## License

The repository does not currently include a standalone `LICENSE` file. Do not assume redistribution or commercial-use rights until a license is explicitly added.
