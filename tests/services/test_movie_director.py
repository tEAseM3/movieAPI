import pytest
from sqlalchemy import select

from app.exceptions.director import DirectorNotFoundError
from app.exceptions.movie import (
    MovieDirectorAlreadyExistsError,
    MovieDirectorNotFoundError,
    MovieNotFoundError,
)
from app.models.language import Language
from app.schemas.director import CreateDirector
from app.schemas.language import CreateLanguage
from app.schemas.movie import CreateMovie
from app.services.director.director import create_director
from app.services.director.movie_director import (
    create_movie_director,
    delete_movie_director,
    get_director_movies,
    get_movie_director,
    get_movie_directors,
)
from app.services.language import create_language
from app.services.movie import create_movie, soft_delete_movie


def _make_director(db_session, name="Christopher", surname="Nolan", birthdate="1970-07-30"):
    return create_director(
        CreateDirector(name=name, surname=surname, birthdate=birthdate, bio="Director"),
        db_session,
    )


def _make_movie(db_session, title="Test Movie"):
    language = db_session.execute(
        select(Language).where(Language.code == "en")
    ).scalar_one_or_none()
    if language is None:
        language = create_language(CreateLanguage(name="English", code="en"), db_session)
    return create_movie(
        CreateMovie(
            language_id=language.id,
            title=title,
            description="Test description",
            release_date="2020-01-01",
            duration_time=120,
        ),
        db_session,
    )


# create_movie_director


def test_create_movie_director_success(db_session):
    director = _make_director(db_session)
    movie = _make_movie(db_session)

    movie_director = create_movie_director(movie.id, director.id, db_session)

    assert movie_director.movie_id == movie.id
    assert movie_director.director_id == director.id


def test_create_movie_director_duplicate_raises(db_session):
    director = _make_director(db_session)
    movie = _make_movie(db_session)

    create_movie_director(movie.id, director.id, db_session)

    with pytest.raises(MovieDirectorAlreadyExistsError):
        create_movie_director(movie.id, director.id, db_session)


def test_create_movie_director_movie_not_found_raises(db_session):
    director = _make_director(db_session)

    with pytest.raises(MovieNotFoundError):
        create_movie_director(999, director.id, db_session)


def test_create_movie_director_director_not_found_raises(db_session):
    movie = _make_movie(db_session)

    with pytest.raises(DirectorNotFoundError):
        create_movie_director(movie.id, 999, db_session)


# get_movie_director and get_movie_directors


def test_get_movie_director_not_found_raises(db_session):
    director = _make_director(db_session)
    movie = _make_movie(db_session)

    with pytest.raises(MovieDirectorNotFoundError):
        get_movie_director(movie.id, director.id, db_session)


def test_get_movie_director_success(db_session):
    director = _make_director(db_session)
    movie = _make_movie(db_session)
    create_movie_director(movie.id, director.id, db_session)

    movie_director = get_movie_director(movie.id, director.id, db_session)

    assert movie_director.director_id == director.id
    assert movie_director.movie_id == movie.id


def test_get_movie_directors_returns_list(db_session):
    nolan = _make_director(db_session, name="Christopher", surname="Nolan", birthdate="1970-07-30")
    tarantino = _make_director(
        db_session, name="Quentin", surname="Tarantino", birthdate="1963-03-27"
    )
    movie = _make_movie(db_session)

    create_movie_director(movie.id, nolan.id, db_session)
    create_movie_director(movie.id, tarantino.id, db_session)

    directors = get_movie_directors(movie.id, db_session)

    assert len(directors) == 2
    assert {d.surname for d in directors} == {"Nolan", "Tarantino"}


def test_get_movie_directors_empty(db_session):
    movie = _make_movie(db_session)

    directors = get_movie_directors(movie.id, db_session)

    assert directors == []


def test_get_movie_directors_movie_not_found_raises(db_session):
    with pytest.raises(MovieNotFoundError):
        get_movie_directors(999, db_session)


def test_get_movie_directors_excludes_soft_deleted_director(db_session):
    director = _make_director(db_session)
    movie = _make_movie(db_session)
    create_movie_director(movie.id, director.id, db_session)

    from app.services.director.director import soft_delete_director

    soft_delete_director(director.id, db_session)

    assert get_movie_directors(movie.id, db_session) == []


# get_director_movies


def test_get_director_movies_returns_list(db_session):
    director = _make_director(db_session)
    movie1 = _make_movie(db_session, title="Movie 1")
    movie2 = _make_movie(db_session, title="Movie 2")

    create_movie_director(movie1.id, director.id, db_session)
    create_movie_director(movie2.id, director.id, db_session)

    movies = get_director_movies(director.id, db_session)

    assert len(movies) == 2
    assert {m.title for m in movies} == {"Movie 1", "Movie 2"}


def test_get_director_movies_empty(db_session):
    director = _make_director(db_session)

    movies = get_director_movies(director.id, db_session)

    assert movies == []


def test_get_director_movies_director_not_found_raises(db_session):
    with pytest.raises(DirectorNotFoundError):
        get_director_movies(999, db_session)


def test_get_director_movies_excludes_soft_deleted_movie(db_session):
    director = _make_director(db_session)
    movie = _make_movie(db_session)
    create_movie_director(movie.id, director.id, db_session)
    soft_delete_movie(movie.id, db_session)

    assert get_director_movies(director.id, db_session) == []


# delete_movie_director


def test_delete_movie_director_success(db_session):
    director = _make_director(db_session)
    movie = _make_movie(db_session)
    create_movie_director(movie.id, director.id, db_session)

    delete_movie_director(movie.id, director.id, db_session)

    with pytest.raises(MovieDirectorNotFoundError):
        get_movie_director(movie.id, director.id, db_session)


def test_delete_movie_director_not_found_raises(db_session):
    director = _make_director(db_session)
    movie = _make_movie(db_session)

    with pytest.raises(MovieDirectorNotFoundError):
        delete_movie_director(movie.id, director.id, db_session)
