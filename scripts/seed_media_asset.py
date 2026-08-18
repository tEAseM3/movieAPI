import time
from datetime import date

import requests
from sqlalchemy import select

from app.core.config import settings
from app.db.database import SessionLocal
from app.models.media_asset import MediaAsset
from app.models.movie import Movie

TMDB_BASE = "https://api.themoviedb.org/3"
TMDB_IMAGE_BASE = "https://image.tmdb.org/t/p/original"


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


def seed_media_assets() -> None:
    db = SessionLocal()

    try:
        movies = db.scalars(select(Movie).where(Movie.deleted_at.is_(None))).all()

        created_count = 0
        skipped_count = 0

        for movie in movies:
            print(f"\nProcessing movie: {movie.title} ({movie.release_date})")

            # Ищем фильм в TMDB
            tmdb_movie = search_movie(
                movie.title,
                movie.release_date,
            )

            if tmdb_movie is None:
                skipped_count += 1

                print(f"Skipped movie '{movie.title}' - not found in TMDB")

                continue

            assets = [
                {
                    "asset_type": "poster",
                    "filepath": None,
                    "url": tmdb_movie.get("poster_path"),
                },
                {
                    "asset_type": "backdrop",
                    "filepath": None,
                    "url": tmdb_movie.get("backdrop_path"),
                },
            ]

            for asset in assets:
                image_path = asset["url"]

                if not image_path:
                    skipped_count += 1

                    print(
                        f"Skipped {asset['asset_type']} for movie '{movie.title}' - image not found"
                    )

                    continue

                # Формируем полный URL изображения
                image_url = f"{TMDB_IMAGE_BASE}{image_path}"

                # Проверяем, существует ли уже такой asset
                existing_asset = db.scalar(
                    select(MediaAsset).where(
                        MediaAsset.movie_id == movie.id,
                        MediaAsset.asset_type == asset["asset_type"],
                        MediaAsset.deleted_at.is_(None),
                    )
                )

                if existing_asset:
                    skipped_count += 1
                    continue

                db.add(
                    MediaAsset(
                        movie_id=movie.id,
                        asset_type=asset["asset_type"],
                        filepath=None,
                        url=image_url,
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
    seed_media_assets()
