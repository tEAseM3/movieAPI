import pytest

from app.exceptions.genre import GenreNotFoundError
from app.exceptions.movie import (
    MovieGenreAlreadyExistsError,
    MovieGenreNotFoundError,
    MovieNotFoundError,
)
from app.services.genre.movie_genre import (
    create_movie_genre,
    delete_movie_genre,
    get_movie_genre,
    get_movie_genres,
)

# create_movie_genre


def test_create_movie_genre_success(make_genre, make_movie, db_session):
    genre = make_genre()
    movie = make_movie()

    movie_genre = create_movie_genre(movie.id, genre.id, db_session)

    assert movie_genre.movie_id == movie.id
    assert movie_genre.genre_id == genre.id


def test_create_movie_genre_duplicate_raises(make_genre, make_movie, db_session):
    genre = make_genre()
    movie = make_movie()

    create_movie_genre(movie.id, genre.id, db_session)

    with pytest.raises(MovieGenreAlreadyExistsError):
        create_movie_genre(movie.id, genre.id, db_session)


def test_create_movie_genre_genre_not_found_raises(make_movie, db_session):
    movie = make_movie()

    with pytest.raises(GenreNotFoundError):
        create_movie_genre(movie.id, 999, db_session)


def test_create_movie_genre_movie_not_found_raises(make_genre, db_session):
    genre = make_genre()

    with pytest.raises(MovieNotFoundError):
        create_movie_genre(999, genre.id, db_session)


# get_movie_genre


def test_get_movie_genre_not_found_raises(make_genre, make_movie, db_session):
    genre = make_genre()
    movie = make_movie()

    with pytest.raises(MovieGenreNotFoundError):
        get_movie_genre(movie.id, genre.id, db_session)


def test_get_movie_genre_success(make_genre, make_movie, db_session):
    genre = make_genre()
    movie = make_movie()
    create_movie_genre(movie.id, genre.id, db_session)

    movie_genre = get_movie_genre(movie.id, genre.id, db_session)

    assert movie_genre.genre_id == genre.id
    assert movie_genre.movie_id == movie.id


# get_movie_genres


def test_get_movie_genres_returns_list(make_genre, make_movie, db_session):
    action = make_genre()  # name="Action"
    comedy = make_genre(name="Comedy")
    movie = make_movie()

    create_movie_genre(movie.id, action.id, db_session)
    create_movie_genre(movie.id, comedy.id, db_session)

    genres = get_movie_genres(movie.id, db_session)

    assert len(genres) == 2
    assert {g.name for g in genres} == {"Action", "Comedy"}


def test_get_movie_genres_empty(make_movie, db_session):
    movie = make_movie()

    genres = get_movie_genres(movie.id, db_session)

    assert genres == []


def test_get_movie_genres_movie_not_found_raises(db_session):
    with pytest.raises(MovieNotFoundError):
        get_movie_genres(999, db_session)


# delete_movie_genre


def test_delete_movie_genre_success(make_genre, make_movie, db_session):
    genre = make_genre()
    movie = make_movie()
    create_movie_genre(movie.id, genre.id, db_session)

    delete_movie_genre(movie.id, genre.id, db_session)

    with pytest.raises(MovieGenreNotFoundError):
        get_movie_genre(movie.id, genre.id, db_session)


def test_delete_movie_genre_not_found_raises(make_genre, make_movie, db_session):
    genre = make_genre()
    movie = make_movie()

    with pytest.raises(MovieGenreNotFoundError):
        delete_movie_genre(movie.id, genre.id, db_session)
