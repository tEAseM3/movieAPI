import pytest

from app.exceptions.favorite import FavoriteAlreadyExistsError, FavoriteNotFoundError
from app.exceptions.movie import MovieNotFoundError
from app.schemas.favorite import CreateFavorite
from app.services.favorite import (
    create_favorite,
    delete_favorite,
    get_favorite,
    get_favorites_by_user,
)

# create_favorite


def test_create_favorite_success(make_movie, make_user, db_session):
    movie = make_movie()
    user = make_user()

    favorite = create_favorite(movie.id, user.id, CreateFavorite(content="Watch again"), db_session)

    assert favorite.movie_id == movie.id
    assert favorite.content == "Watch again"


def test_create_favorite_duplicate_raises(make_movie, make_user, db_session):
    movie = make_movie()
    user = make_user()
    create_favorite(movie.id, user.id, CreateFavorite(), db_session)

    with pytest.raises(FavoriteAlreadyExistsError):
        create_favorite(movie.id, user.id, CreateFavorite(), db_session)


def test_create_favorite_movie_not_found_raises(make_user, db_session):
    user = make_user()

    with pytest.raises(MovieNotFoundError):
        create_favorite(999, user.id, CreateFavorite(), db_session)


# get_favorites_by_user


def test_get_favorites_by_user_returns_only_user_favorites(make_movie, make_user, db_session):
    first_movie = make_movie(title="First")
    second_movie = make_movie(title="Second")
    user = make_user()
    other_user = make_user()
    create_favorite(first_movie.id, user.id, CreateFavorite(), db_session)
    create_favorite(second_movie.id, other_user.id, CreateFavorite(), db_session)

    favorites = get_favorites_by_user(user.id, db_session)

    assert len(favorites) == 1
    assert favorites[0].movie_id == first_movie.id


def test_get_favorites_by_user_pagination(make_movie, make_user, db_session):
    user = make_user()
    for title in ["First", "Second", "Third"]:
        movie = make_movie(title=title)
        create_favorite(movie.id, user.id, CreateFavorite(), db_session)

    favorites = get_favorites_by_user(user.id, db_session, offset=0, limit=2)

    assert len(favorites) == 2


# delete_favorite


def test_delete_favorite_success(make_movie, make_user, db_session):
    movie = make_movie()
    user = make_user()
    favorite = create_favorite(movie.id, user.id, CreateFavorite(), db_session)

    delete_favorite(movie.id, user.id, db_session)

    with pytest.raises(FavoriteNotFoundError):
        get_favorite(favorite.id, db_session)


def test_delete_favorite_not_found_raises(make_movie, make_user, db_session):
    movie = make_movie()
    user = make_user()

    with pytest.raises(FavoriteNotFoundError):
        delete_favorite(movie.id, user.id, db_session)
