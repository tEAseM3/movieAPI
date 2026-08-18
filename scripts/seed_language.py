import requests
from sqlalchemy.exc import IntegrityError

from app.core.config import settings
from app.db.database import SessionLocal
from app.exceptions.language import LanguageAlreadyExistsError
from app.schemas.language import CreateLanguage
from app.services.language import create_language

TMDB_BASE = "https://api.themoviedb.org/3"


def fetch_languages() -> list[dict]:
    response = requests.get(
        f"{TMDB_BASE}/configuration/languages",
        params={"api_key": settings.TMDB_API_KEY},
    )
    response.raise_for_status()
    return response.json()


def seed_languages() -> None:
    db = SessionLocal()

    try:
        languages = fetch_languages()

        created_count = 0
        skipped_count = 0
        invalid_count = 0

        for lang in languages:
            code = lang["iso_639_1"]

            if len(code) != 2:
                invalid_count += 1
                continue

            name = lang["english_name"] or lang["name"] or code

            try:
                create_language(CreateLanguage(name=name, code=code), db)
                created_count += 1
            except LanguageAlreadyExistsError:
                skipped_count += 1
            except IntegrityError:
                db.rollback()
                skipped_count += 1

        print(f"Created = {created_count}, Skipped = {skipped_count}, Invalid = {invalid_count}")

    finally:
        db.close()


if __name__ == "__main__":
    seed_languages()
