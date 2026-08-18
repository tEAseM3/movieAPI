import time
from datetime import date

import requests
from sqlalchemy import select

from app.core.config import settings
from app.db.database import SessionLocal
from app.models.language import Language
from app.models.movie import Movie

TMDB_BASE = "https://api.themoviedb.org/3"


def fetch_popular_movies(pages: int = 1) -> list[dict]:
    movies = []

    for page in range(1, pages + 1):
        response = requests.get(
            f"{TMDB_BASE}/movie/popular",
            params={
                "api_key": settings.TMDB_API_KEY,
                "page": page,
            },
            timeout=10,
        )

        response.raise_for_status()
        movies.extend(response.json()["results"])

        time.sleep(0.05)

    return movies


def fetch_movie_details(movie_id: int) -> dict:
    response = requests.get(
        f"{TMDB_BASE}/movie/{movie_id}",
        params={
            "api_key": settings.TMDB_API_KEY,
        },
        timeout=10,
    )

    response.raise_for_status()
    return response.json()


def seed_movies(pages: int = 1) -> None:
    db = SessionLocal()

    try:
        tmdb_movies = fetch_popular_movies(pages)

        created_count = 0
        skipped_count = 0

        for tmdb_movie in tmdb_movies:
            title = tmdb_movie.get("title")
            release_date_raw = tmdb_movie.get("release_date")
            language_code = tmdb_movie.get("original_language")

            if not title or not release_date_raw or not language_code:
                skipped_count += 1
                continue

            try:
                release_date = date.fromisoformat(release_date_raw)
            except ValueError:
                skipped_count += 1
                continue

            language = db.scalar(select(Language).where(Language.code == language_code))

            if language is None:
                skipped_count += 1
                print(f"Skipped '{title}': language '{language_code}' not found")
                continue

            existing_movie = db.scalar(
                select(Movie).where(
                    Movie.title == title,
                    Movie.release_date == release_date,
                )
            )

            if existing_movie:
                skipped_count += 1
                continue

            details = fetch_movie_details(tmdb_movie["id"])

            runtime = details.get("runtime")

            if not runtime or runtime <= 0:
                skipped_count += 1
                print(f"Skipped '{title}': runtime is missing")
                continue

            description = details.get("overview") or None

            if description and len(description) > 2000:
                description = description[:2000]

            movie = Movie(
                language_id=language.id,
                title=title,
                description=description,
                release_date=release_date,
                duration_time=runtime,
            )

            db.add(movie)
            created_count += 1

            time.sleep(0.05)

        db.commit()

        print(f"Created = {created_count}, Skipped = {skipped_count}")

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


if __name__ == "__main__":
    seed_movies(pages=5)
