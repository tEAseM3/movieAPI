# Movie API

## Description

Movie API is a RESTful backend service for managing a movie database. It provides endpoints to create, read, update, and delete . The API is built with FastAPI and uses PostgreSQL (with SQLAlchemy ORM and Alembic) for database migrations. Input validation is handled by Pydantic schemas. Tests are written using Pytest. Code quality is maintained with Ruff (linter and formater). The project is containerized with Docker and includes a GitHub Actions CI workflow that runs on push. Swagger UI and ReDoc documentation are available in development environments. This README summarizes tech stack, setup, usage, and deployment.

## Tech Stack

Python 3.14.5 with FastAPI framework

PostgreSQL 16 database

SQLAlchemy ORM for models and DB access

Alembic for database migrations

Pydantic for data models (schemas)

Pytest for automated testing

Ruff for linting and formatting

Docker & Docker Compose for containerization

GitHub Actions for CI/CD

## Deployment

The API is deployed on Render and is available for testing:

Swagger UI: https://movieapi-sii0.onrender.com/docs

Redoc https://movieapi-sii0.onrender.com/redoc


The deployed service is intended primarily for testing and demonstration purposes.

1. Render Free Tier

The API is currently hosted using Render's Free instance.

Because of the free-tier limitations, the service may spin down after a period of inactivity. As a result, the first request after inactivity can take noticeably longer than subsequent requests.

2. Test Accounts

Admin: username: admin, password: qwerty123

User: username: user, password: qwerty123

## Environment Variables 
Main:

DATABASE_URL: Connection string for your Postgres database. 

TEST_DATABASE_URL: Database URL for running pytest. 

SECRET_KEY: Used for cryptographic signing.

TMDB_API_KEY: API key for The Movie Database. 

ENVIRONMENT: Set to development, test, or production. The app disables /docs and /redoc when ENVIRONMENT=production. 

CORS_ORIGINS: JSON array of allowed CORS origins

Other: 

ALGORITHM: Algorithm used for JWT token signing.

ACCESS_TOKEN_EXPIRE_MINUTES: Access token expiration time in minutes.

REFRESH_TOKEN_EXPIRE_DAYS: Refresh token expiration time in days.

Adjust as needed



## Quick Start

### Local Development

#### Linux

1. Clone the repository and create a virtual environment:

```bash
git clone https://github.com/tEAseM3/movieAPI.git
cd movieAPI

python3 -m venv venv
source venv/bin/activate

pip install -r requirements.txt
```

2. Configure environment:
```bash
cp .env.example .env
```
change keys and urls

3. Run database migrations:
```bash
alembic upgrade head
```

4. Seed the database:
```bash
python Scripts/seed_all.py
```

5. Run the development server:
```bash
uvicorn app.main:app --reload
```

6. Run tests:
```bash
pytest -q
```

API:
http://localhost:8000

Swagger UI:
http://localhost:8000/docs

ReDoc:
http://localhost:8000/redoc

#### Windows
1. Clone the repository and create a virtual environment:
```powershell
git clone https://github.com/tEAseM3/movieAPI
cd movieAPI

python -m venv venv
.\venv\Scripts\Activate.ps1

pip install -r requirements.txt
```

2. Configure environment:
```powershell
Copy-Item .env.example .env
```

change keys and urls

3. Run database migrations:
```powershell
alembic upgrade head
```

4. Seed the database
```powershell
python Scripts/seed_all.py
```

5. Run test
```powershell
pytest -q
```

6. Run development server
```powershell
uvicorn app.main:app --reload
```

API:
http://localhost:8000

Swagger UI:
http://localhost:8000/docs

ReDoc:
http://localhost:8000/redoc

### Docker

1. Build and run:
```
docker compose up --build -d
```

2. Run database seed:
```
docker compose run --rm seed
```

3. Run test in Docker:
```
docker compose -f docker-compose.test.yml up --build --exit-code-from app
```
#Container stops after test finished

4. Stop containers
```
docker compose down
```

## Database Migrations
Database schema changes are managed by Alembic. After modifying models, create new migrations with: 

alembic revision --autogenerate -m "Describe change" 

and apply migrations with: 

alembic upgrade head 

This updates the database to the latest schema. The CI pipeline also runs migrations automatically on the test database. 

## Testing and Linting
Run tests with Pytest: 

pytest -q 

Linting and formating: 

ruff check .
ruff format . 

## API Documentation

FastAPI automatically generates OpenAPI docs. In development, you can access: 

Swagger UI (interactive docs) at http://localhost:8000/docs

ReDoc (alternative docs) at http://localhost:8000/redoc

OpenAPI JSON schema at http://localhost:8000/openapi.json

In production, the docs_url and redoc_url are set to None, so /docs and /redoc are disabled to avoid exposing docs publicly. 

## Continuous Integration and Badges 

This project uses GitHub Actions for CI, triggered on every push and pull request. The workflow (.github/workflows/ci.yml) does the following: 

Sets up Python. 

Brings up a PostgreSQL 16. 

Installs dependencies. 

Runs Ruff to check code style and format. 

Applies Alembic migrations. 

Runs Pytest on the test database. 

If all steps pass, the CI is green.

![CI](https://github.com/tEAseM3/movieAPI/actions/workflows/ci.yml/badge.svg)

## Security

Secrets: Never commit real secrets to Git. Only .env.example should be in the repo. If you accidentally commit a key or password, change it and remove it from Git history. 

.gitignore: Ensure .env, any virtual environments, and other build artifacts are in .gitignore. 

CI Branch Protection: Consider protecting the main branch so that all changes must pass CI before merge. 

Dependencies: Use a requirements.txt or pyproject.toml and review dependency updates. 

## Contact

For questions contact artemprohorenko1@gmail.com