import pytest

from app.exceptions.genre import GenreAlreadyExistsError, GenreNotFoundError
from app.schemas.genre import UpdateGenre
from app.services.genre.genre import (
    delete_genre,
    get_genre,
    get_genre_movies,
    get_genres,
    update_genre,
)
from app.services.genre.movie_genre import create_movie_genre
from app.services.movie import soft_delete_movie

# create_genre


def test_create_genre_success(make_genre):
    genre = make_genre()

    assert genre.id is not None
    assert genre.name == "Action"


def test_create_genre_duplicate_name_raises(make_genre):
    make_genre()

    with pytest.raises(GenreAlreadyExistsError):
        make_genre()


# get_genre


def test_get_genre_not_found_raises(db_session):
    with pytest.raises(GenreNotFoundError):
        get_genre(999, db_session)


def test_get_genre_success(make_genre, db_session):
    created = make_genre()
    fetched = get_genre(created.id, db_session)

    assert fetched.id == created.id
    assert fetched.name == "Action"


# get_genres


def test_get_genres_pagination(make_genre, db_session):
    for name in ["Action", "Comedy", "Drama", "Horror", "Thriller"]:
        make_genre(name=name)

    result = get_genres(db_session, offset=0, limit=3)
    assert len(result) == 3


# get_genre_movies


def test_get_genre_movies_returns_list(make_genre, make_movie, db_session):
    genre = make_genre()
    inception = make_movie(title="Inception")
    interstellar = make_movie(title="Interstellar")

    create_movie_genre(inception.id, genre.id, db_session)
    create_movie_genre(interstellar.id, genre.id, db_session)

    movies = get_genre_movies(genre.id, db_session)

    assert len(movies) == 2
    assert {m.title for m in movies} == {"Inception", "Interstellar"}


def test_get_genre_movies_empty(make_genre, db_session):
    genre = make_genre()

    movies = get_genre_movies(genre.id, db_session)

    assert movies == []


def test_get_genre_movies_not_found_raises(db_session):
    with pytest.raises(GenreNotFoundError):
        get_genre_movies(999, db_session)


def test_get_genre_movies_pagination(make_genre, make_movie, db_session):
    genre = make_genre()
    for title in ["Inception", "Interstellar", "The Dark Knight", "Dunkirk", "Tenet"]:
        movie = make_movie(title=title)
        create_movie_genre(movie.id, genre.id, db_session)

    result = get_genre_movies(genre.id, db_session, offset=0, limit=3)
    assert len(result) == 3


def test_get_genre_movies_excludes_soft_deleted(make_genre, make_movie, db_session):
    genre = make_genre()
    movie = make_movie()
    create_movie_genre(movie.id, genre.id, db_session)
    soft_delete_movie(movie.id, db_session)

    movies = get_genre_movies(genre.id, db_session)

    assert movies == []


# update_genre


def test_update_genre_name_success(make_genre, db_session):
    created = make_genre()
    updated = update_genre(created.id, UpdateGenre(name="Action & Adventure"), db_session)

    assert updated.name == "Action & Adventure"


def test_update_genre_conflicting_name_raises(make_genre, db_session):
    make_genre(name="Action")
    target = make_genre(name="Comedy")

    with pytest.raises(GenreAlreadyExistsError):
        update_genre(target.id, UpdateGenre(name="Action"), db_session)


def test_update_genre_same_name_does_not_conflict_with_self(make_genre, db_session):
    created = make_genre()  # name = "Action"

    updated = update_genre(created.id, UpdateGenre(name="Action"), db_session)
    assert updated.name == "Action"


def test_update_genre_not_found_raises(db_session):
    with pytest.raises(GenreNotFoundError):
        update_genre(999, UpdateGenre(name="Action"), db_session)


# delete_genre


def test_delete_genre_success(make_genre, db_session):
    created = make_genre()
    delete_genre(created.id, db_session)

    with pytest.raises(GenreNotFoundError):
        get_genre(created.id, db_session)


def test_delete_genre_not_found_raises(db_session):
    with pytest.raises(GenreNotFoundError):
        delete_genre(999, db_session)
