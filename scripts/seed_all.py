from app.db import base_models  # noqa F401

from scripts.seed_actor import seed_actors
from scripts.seed_director import seed_directors
from scripts.seed_genre import seed_genres
from scripts.seed_language import seed_languages
from scripts.seed_media_asset import seed_media_assets
from scripts.seed_movie import seed_movies
from scripts.seed_movie_actor import seed_movie_actors
from scripts.seed_movie_director import seed_movie_directors
from scripts.seed_movie_genre import seed_movie_genres
from scripts.seed_user import seed_users


def seed_all() -> None:
    print("Languages")
    seed_languages()

    print("\nGenres")
    seed_genres()

    print("\nMovies")
    seed_movies()

    print("\nActors")
    seed_actors()

    print("\nDirectors")
    seed_directors()

    print("\nMovie genres")
    seed_movie_genres()

    print("\nMovie actors")
    seed_movie_actors()

    print("\nMovie directors")
    seed_movie_directors()

    print("\nMedia assets")
    seed_media_assets()

    print("\nUsers")
    seed_users()

    print("\nAll seeds completed")


if __name__ == "__main__":
    seed_all()
