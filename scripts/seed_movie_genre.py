import time
from datetime import date

import requests
from sqlalchemy import select

from app.core.config import settings
from app.db.database import SessionLocal
from app.models.genre import Genre
from app.models.movie import Movie
from app.models.movie_genre import MovieGenre

TMDB_BASE = "https://api.themoviedb.org/3"


def search_movie(title: str, release_date: date) -> dict | None:
    response = requests.get(
        f"{TMDB_BASE}/search/movie",
        params={
            "api_key": settings.TMDB_API_KEY,
            "query": title,
            "year": release_date.year,
        },
        timeout=10,
    )

    response.raise_for_status()

    results = response.json().get("results", [])

    for movie in results:
        if movie.get("title") != title:
            continue

        if movie.get("release_date") == str(release_date):
            return movie

    return None


def fetch_movie_details(tmdb_movie_id: int) -> dict:
    response = requests.get(
        f"{TMDB_BASE}/movie/{tmdb_movie_id}",
        params={
            "api_key": settings.TMDB_API_KEY,
        },
        timeout=10,
    )

    response.raise_for_status()

    return response.json()


def seed_movie_genres() -> None:
    db = SessionLocal()

    try:
        movies = db.scalars(select(Movie).where(Movie.deleted_at.is_(None))).all()

        created_count = 0
        skipped_count = 0

        for movie in movies:
            print(f"\nProcessing movie: {movie.title} ({movie.release_date})")

            # Ищем конкретный фильм в TMDB
            tmdb_movie = search_movie(
                movie.title,
                movie.release_date,
            )

            if tmdb_movie is None:
                skipped_count += 1

                print(f"Skipped movie '{movie.title}' - not found in TMDB")

                continue

            # Получаем жанры конкретного фильма
            details = fetch_movie_details(tmdb_movie["id"])

            genres = details.get("genres", [])

            for tmdb_genre in genres:
                genre_name = tmdb_genre.get("name")

                if not genre_name:
                    continue

                # Ищем жанр среди уже существующих
                # в нашей БД
                genre = db.scalar(select(Genre).where(Genre.name == genre_name))

                if genre is None:
                    skipped_count += 1

                    print(
                        f"Skipped genre '{genre_name}' "
                        f"for movie '{movie.title}' - "
                        f"genre not found in database"
                    )

                    continue

                # Проверяем существующую связь
                existing_relation = db.scalar(
                    select(MovieGenre).where(
                        MovieGenre.movie_id == movie.id,
                        MovieGenre.genre_id == genre.id,
                    )
                )

                if existing_relation:
                    skipped_count += 1
                    continue

                db.add(
                    MovieGenre(
                        movie_id=movie.id,
                        genre_id=genre.id,
                    )
                )

                created_count += 1

            time.sleep(0.05)

        db.commit()

        print(f"\nCreated = {created_count}, Skipped = {skipped_count}")

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


if __name__ == "__main__":
    seed_movie_genres()
