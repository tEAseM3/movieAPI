import time
from datetime import date

import requests
from sqlalchemy import select

from app.core.config import settings
from app.db.database import SessionLocal
from app.models.director import Director
from app.models.movie import Movie
from app.models.movie_director import MovieDirector

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


def fetch_movie_credits(movie_id: int) -> dict:
    response = requests.get(
        f"{TMDB_BASE}/movie/{movie_id}/credits",
        params={
            "api_key": settings.TMDB_API_KEY,
        },
        timeout=10,
    )

    response.raise_for_status()

    return response.json()


def split_name(full_name: str) -> tuple[str, str]:
    parts = full_name.strip().split(" ", 1)

    if len(parts) == 1:
        return parts[0], ""

    return parts[0], parts[1]


def seed_movie_directors() -> None:
    db = SessionLocal()

    try:
        # Берём только фильмы, которые уже существуют в нашей БД
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

            # Получаем crew фильма
            credits = fetch_movie_credits(tmdb_movie["id"])

            crew = credits.get("crew", [])

            # Берём только режиссёров
            directors = [
                member
                for member in crew
                if isinstance(member, dict) and member.get("job") == "Director"
            ]

            for member in directors:
                full_name = member.get("name")

                if not full_name:
                    skipped_count += 1
                    continue

                name, surname = split_name(full_name)

                # Наша модель требует фамилию
                if not surname.strip():
                    skipped_count += 1

                    print(f"Skipped director without surname: {full_name}")

                    continue

                # Ищем режиссёра в нашей БД
                director = db.scalar(
                    select(Director).where(
                        Director.name == name,
                        Director.surname == surname,
                        Director.deleted_at.is_(None),
                    )
                )

                if director is None:
                    skipped_count += 1

                    print(
                        f"Skipped director '{full_name}' "
                        f"for movie '{movie.title}' - "
                        f"director not found in database"
                    )

                    continue

                # Проверяем, существует ли уже связь
                existing_relation = db.scalar(
                    select(MovieDirector).where(
                        MovieDirector.movie_id == movie.id,
                        MovieDirector.director_id == director.id,
                    )
                )

                if existing_relation:
                    skipped_count += 1
                    continue

                db.add(
                    MovieDirector(
                        movie_id=movie.id,
                        director_id=director.id,
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
    seed_movie_directors()
