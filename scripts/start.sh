#!/bin/sh

alembic upgrade head

python -m scripts.seed_all

exec uvicorn app.main:app --host 0.0.0.0 --port 8000