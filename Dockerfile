FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt \
    alembic==1.18.5 \
    argon2-cffi==25.1.0 \
    email-validator==2.3.0 \
    pydantic-settings==2.13.1 \
    psycopg2-binary==2.9.12 \
    pwdlib==0.3.0 \
    python-jose==3.5.0 \
    python-multipart==0.0.22

COPY . .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
