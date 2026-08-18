import pytest
from sqlalchemy import select

from app.exceptions.actor import ActorNotFoundError
from app.exceptions.language import LanguageAlreadyExistsError
from app.exceptions.movie import (
    MovieActorAlreadyExistsError,
    MovieActorNotFoundError,
    MovieNotFoundError,
)
from app.models.language import Language
from app.schemas.actor import CreateActor, CreateMovieActor, UpdateMovieActor
from app.schemas.language import CreateLanguage
from app.schemas.movie import CreateMovie
from app.services.actor.actor import create_actor
from app.services.actor.movie_actor import (
    create_movie_actor,
    delete_movie_actor,
    get_actor_movies,
    get_movie_actor,
    get_movie_actors,
    update_movie_actor,
)
from app.services.language import create_language
from app.services.movie import create_movie, soft_delete_movie


def _make_actor(db_session, name="Leonardo", surname="DiCaprio", birthdate="1974-11-11"):
    return create_actor(
        CreateActor(name=name, surname=surname, birthdate=birthdate, bio="Actor"),
        db_session,
    )


def _make_movie(db_session, title="Test Movie"):
    try:
        language = create_language(CreateLanguage(name="English", code="en"), db_session)
    except LanguageAlreadyExistsError:
        language = db_session.execute(select(Language).where(Language.code == "en")).scalar_one()

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


# create_movie_actor


def test_create_movie_actor_success(db_session):
    actor = _make_actor(db_session)
    movie = _make_movie(db_session)

    movie_actor = create_movie_actor(
        movie.id, actor.id, CreateMovieActor(character_name="Cobb"), db_session
    )

    assert movie_actor.movie_id == movie.id
    assert movie_actor.actor_id == actor.id
    assert movie_actor.character_name == "Cobb"


def test_create_movie_actor_duplicate_raises(db_session):
    actor = _make_actor(db_session)
    movie = _make_movie(db_session)

    create_movie_actor(movie.id, actor.id, CreateMovieActor(character_name="Cobb"), db_session)

    with pytest.raises(MovieActorAlreadyExistsError):
        create_movie_actor(movie.id, actor.id, CreateMovieActor(character_name="Cobb"), db_session)


def test_create_movie_actor_movie_not_found_raises(db_session):
    actor = _make_actor(db_session)

    with pytest.raises(MovieNotFoundError):
        create_movie_actor(999, actor.id, CreateMovieActor(character_name="Cobb"), db_session)


def test_create_movie_actor_actor_not_found_raises(db_session):
    movie = _make_movie(db_session)

    with pytest.raises(ActorNotFoundError):
        create_movie_actor(movie.id, 999, CreateMovieActor(character_name="Cobb"), db_session)


# get_movie_actor


def test_get_movie_actor_not_found_raises(db_session):
    actor = _make_actor(db_session)
    movie = _make_movie(db_session)

    with pytest.raises(MovieActorNotFoundError):
        get_movie_actor(movie.id, actor.id, db_session)


def test_get_movie_actor_success(db_session):
    actor = _make_actor(db_session)
    movie = _make_movie(db_session)
    create_movie_actor(movie.id, actor.id, CreateMovieActor(character_name="Cobb"), db_session)

    movie_actor = get_movie_actor(movie.id, actor.id, db_session)

    assert movie_actor.actor_id == actor.id
    assert movie_actor.movie_id == movie.id


# get_movie_actors


def test_get_movie_actors_returns_cast(db_session):
    dicaprio = _make_actor(db_session)  # Leonardo DiCaprio (default)
    hardy = _make_actor(db_session, name="Tom", surname="Hardy")
    movie = _make_movie(db_session)

    create_movie_actor(movie.id, dicaprio.id, CreateMovieActor(character_name="Cobb"), db_session)
    create_movie_actor(movie.id, hardy.id, CreateMovieActor(character_name="Eames"), db_session)

    cast = get_movie_actors(movie.id, db_session)

    assert len(cast) == 2
    characters = {c.character_name for c in cast}
    assert characters == {"Cobb", "Eames"}


def test_get_movie_actors_empty(db_session):
    movie = _make_movie(db_session)

    cast = get_movie_actors(movie.id, db_session)

    assert cast == []


def test_get_movie_actors_movie_not_found_raises(db_session):
    with pytest.raises(MovieNotFoundError):
        get_movie_actors(999, db_session)


# get_actor_movies


def test_get_actor_movies_returns_list(db_session):
    actor = _make_actor(db_session)
    movie1 = _make_movie(db_session, title="Movie 1")
    movie2 = _make_movie(db_session, title="Movie 2")

    create_movie_actor(movie1.id, actor.id, CreateMovieActor(character_name="Role 1"), db_session)
    create_movie_actor(movie2.id, actor.id, CreateMovieActor(character_name="Role 2"), db_session)

    movies = get_actor_movies(actor.id, db_session)

    assert len(movies) == 2
    assert {m.title for m in movies} == {"Movie 1", "Movie 2"}


def test_get_actor_movies_empty(db_session):
    actor = _make_actor(db_session)

    movies = get_actor_movies(actor.id, db_session)

    assert movies == []


def test_get_actor_movies_actor_not_found_raises(db_session):
    with pytest.raises(ActorNotFoundError):
        get_actor_movies(999, db_session)


def test_get_actor_movies_excludes_soft_deleted_movie(db_session):
    actor = _make_actor(db_session)
    movie = _make_movie(db_session)
    create_movie_actor(movie.id, actor.id, CreateMovieActor(character_name="Cobb"), db_session)
    soft_delete_movie(movie.id, db_session)

    assert get_actor_movies(actor.id, db_session) == []


# update_movie_actor


def test_update_movie_actor_character_name_success(db_session):
    actor = _make_actor(db_session)
    movie = _make_movie(db_session)
    create_movie_actor(movie.id, actor.id, CreateMovieActor(character_name="Cobb"), db_session)

    updated = update_movie_actor(
        movie.id, actor.id, UpdateMovieActor(character_name="Dom Cobb"), db_session
    )

    assert updated.character_name == "Dom Cobb"


def test_update_movie_actor_not_found_raises(db_session):
    actor = _make_actor(db_session)
    movie = _make_movie(db_session)

    with pytest.raises(MovieActorNotFoundError):
        update_movie_actor(movie.id, actor.id, UpdateMovieActor(character_name="Ghost"), db_session)


# delete_movie_actor


def test_delete_movie_actor_success(db_session):
    actor = _make_actor(db_session)
    movie = _make_movie(db_session)
    create_movie_actor(movie.id, actor.id, CreateMovieActor(character_name="Cobb"), db_session)

    delete_movie_actor(movie.id, actor.id, db_session)

    with pytest.raises(MovieActorNotFoundError):
        get_movie_actor(movie.id, actor.id, db_session)


def test_delete_movie_actor_not_found_raises(db_session):
    actor = _make_actor(db_session)
    movie = _make_movie(db_session)

    with pytest.raises(MovieActorNotFoundError):
        delete_movie_actor(movie.id, actor.id, db_session)
