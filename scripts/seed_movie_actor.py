import time
from datetime import date

import requests
from sqlalchemy import select

from app.core.config import settings
from app.db.database import SessionLocal
from app.models.actor import Actor
from app.models.movie import Movie
from app.models.movie_actor import MovieActor

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


def seed_movie_actors() -> None:
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

            # Получаем cast конкретного фильма
            credits = fetch_movie_credits(tmdb_movie["id"])

            cast = credits.get("cast", [])

            # Берём только первых 3 актёров
            for member in cast[:3]:
                if not isinstance(member, dict):
                    skipped_count += 1
                    continue

                full_name = member.get("name")

                if not full_name:
                    skipped_count += 1
                    continue

                name, surname = split_name(full_name)

                # Наша модель требует фамилию
                if not surname.strip():
                    skipped_count += 1

                    print(f"Skipped actor without surname: {full_name}")

                    continue

                # Ищем актёра в нашей БД
                actor = db.scalar(
                    select(Actor).where(
                        Actor.name == name,
                        Actor.surname == surname,
                        Actor.deleted_at.is_(None),
                    )
                )

                if actor is None:
                    skipped_count += 1

                    print(
                        f"Skipped actor '{full_name}' "
                        f"for movie '{movie.title}' - "
                        f"actor not found in database"
                    )

                    continue

                # Проверяем существующую связь
                existing_relation = db.scalar(
                    select(MovieActor).where(
                        MovieActor.movie_id == movie.id,
                        MovieActor.actor_id == actor.id,
                    )
                )

                if existing_relation:
                    skipped_count += 1
                    continue

                character_name = member.get("character") or "Unknown"

                db.add(
                    MovieActor(
                        movie_id=movie.id,
                        actor_id=actor.id,
                        character_name=character_name,
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
    seed_movie_actors()
