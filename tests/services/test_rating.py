import pytest

from app.exceptions.movie import MovieNotFoundError
from app.exceptions.rating import RatingAlreadyExistsError, RatingNotFoundError
from app.schemas.rating import CreateRating, UpdateRating
from app.services.rating import (
    create_rating,
    delete_rating,
    get_movie_rating,
    get_rating,
    update_rating,
)

# create_rating


def test_create_rating_success(make_movie, make_user, db_session):
    movie = make_movie()
    user = make_user()

    rating = create_rating(movie.id, user.id, CreateRating(rating=8), db_session)

    assert rating.rating == 8


def test_create_rating_duplicate_raises(make_movie, make_user, db_session):
    movie = make_movie()
    user = make_user()
    create_rating(movie.id, user.id, CreateRating(rating=8), db_session)

    with pytest.raises(RatingAlreadyExistsError):
        create_rating(movie.id, user.id, CreateRating(rating=9), db_session)


def test_create_rating_movie_not_found_raises(make_user, db_session):
    user = make_user()

    with pytest.raises(MovieNotFoundError):
        create_rating(999, user.id, CreateRating(rating=8), db_session)


# get_movie_rating


def test_get_movie_rating_returns_average_and_count(make_movie, make_user, db_session):
    movie = make_movie()
    first_user = make_user()
    second_user = make_user()
    create_rating(movie.id, first_user.id, CreateRating(rating=8), db_session)
    create_rating(movie.id, second_user.id, CreateRating(rating=10), db_session)

    average, count = get_movie_rating(movie.id, db_session)

    assert average == 9.0
    assert count == 2


def test_get_movie_rating_empty(make_movie, db_session):
    movie = make_movie()

    average, count = get_movie_rating(movie.id, db_session)

    assert average == 0.0
    assert count == 0


def test_get_movie_rating_movie_not_found_raises(db_session):
    with pytest.raises(MovieNotFoundError):
        get_movie_rating(999, db_session)


# update_rating


def test_update_rating_success(make_movie, make_user, db_session):
    movie = make_movie()
    user = make_user()
    create_rating(movie.id, user.id, CreateRating(rating=8), db_session)

    updated = update_rating(movie.id, user.id, UpdateRating(rating=10), db_session)

    assert updated.rating == 10


def test_update_rating_not_found_raises(make_movie, make_user, db_session):
    movie = make_movie()
    user = make_user()

    with pytest.raises(RatingNotFoundError):
        update_rating(movie.id, user.id, UpdateRating(rating=8), db_session)


# delete_rating


def test_delete_rating_success(make_movie, make_user, db_session):
    movie = make_movie()
    user = make_user()
    rating = create_rating(movie.id, user.id, CreateRating(rating=8), db_session)

    delete_rating(movie.id, user.id, db_session)

    with pytest.raises(RatingNotFoundError):
        get_rating(rating.id, db_session)


def test_delete_rating_not_found_raises(make_movie, make_user, db_session):
    movie = make_movie()
    user = make_user()

    with pytest.raises(RatingNotFoundError):
        delete_rating(movie.id, user.id, db_session)
