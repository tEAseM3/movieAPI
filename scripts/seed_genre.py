import requests
from sqlalchemy.exc import IntegrityError

from app.core.config import settings
from app.db.database import SessionLocal
from app.exceptions.genre import GenreAlreadyExistsError
from app.schemas.genre import CreateGenre
from app.services.genre.genre import create_genre

TMDB_BASE = "https://api.themoviedb.org/3"


def fetch_genres() -> list[dict]:
    response = requests.get(
        f"{TMDB_BASE}/genre/movie/list",
        params={"api_key": settings.TMDB_API_KEY},
    )
    response.raise_for_status()
    return response.json()["genres"]


def seed_genres() -> None:
    db = SessionLocal()

    try:
        genres = fetch_genres()

        created_count = 0
        skipped_count = 0

        for genre in genres:
            name = genre["name"]

            try:
                create_genre(CreateGenre(name=name), db)
                created_count += 1
            except GenreAlreadyExistsError:
                skipped_count += 1
            except IntegrityError:
                db.rollback()
                skipped_count += 1

        print(f"Created = {created_count}, Skipped = {skipped_count}")

    finally:
        db.close()


if __name__ == "__main__":
    seed_genres()
