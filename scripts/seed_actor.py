import time
from datetime import date

import requests
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.core.config import settings
from app.db.database import SessionLocal
from app.exceptions.actor import ActorAlreadyExistsError
from app.models.movie import Movie
from app.schemas.actor import CreateActor
from app.services.actor.actor import create_actor

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


def fetch_movie_credits(movie_id: int) -> list[dict]:
    response = requests.get(
        f"{TMDB_BASE}/movie/{movie_id}/credits",
        params={
            "api_key": settings.TMDB_API_KEY,
        },
        timeout=10,
    )

    response.raise_for_status()

    return response.json().get("cast", [])


def fetch_person_details(person_id: int) -> dict:
    response = requests.get(
        f"{TMDB_BASE}/person/{person_id}",
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


def seed_actors() -> None:
    db = SessionLocal()

    try:
        movies = db.scalars(select(Movie).where(Movie.deleted_at.is_(None))).all()

        created_count = 0
        skipped_count = 0

        for movie in movies:
            print(f"\nProcessing movie: {movie.title} ({movie.release_date})")

            tmdb_movie = search_movie(
                movie.title,
                movie.release_date,
            )

            if tmdb_movie is None:
                skipped_count += 1

                print(f"Skipped movie '{movie.title}' - not found in TMDB")

                continue

            cast = fetch_movie_credits(tmdb_movie["id"])

            for member in cast[:3]:
                if not isinstance(member, dict):
                    skipped_count += 1
                    print(f"Skipped invalid cast member: {member}")
                    continue

                person_id = member.get("id")
                full_name = member.get("name")

                if not person_id or not full_name:
                    skipped_count += 1
                    continue

                name, surname = split_name(full_name)

                if not surname.strip():
                    skipped_count += 1

                    print(f"Skipped actor without surname: {full_name}")

                    continue

                details = fetch_person_details(person_id)

                birthdate = details.get("birthday")
                bio = details.get("biography") or None

                if bio and len(bio) > 2000:
                    bio = bio[:2000]

                try:
                    create_actor(
                        CreateActor(
                            name=name,
                            surname=surname,
                            birthdate=birthdate,
                            bio=bio,
                        ),
                        db,
                    )

                    created_count += 1

                    print(f"Created actor: {full_name}")

                except ActorAlreadyExistsError:
                    skipped_count += 1

                except IntegrityError:
                    db.rollback()
                    skipped_count += 1

                time.sleep(0.05)

            time.sleep(0.05)

        print(f"\nCreated = {created_count}, Skipped = {skipped_count}")

    finally:
        db.close()


if __name__ == "__main__":
    seed_actors()
