from sqlalchemy import select

from app.models.language import Language
from app.schemas.actor import CreateActor, CreateMovieActor
from app.schemas.language import CreateLanguage
from app.schemas.movie import CreateMovie
from app.services.actor.actor import create_actor
from app.services.actor.movie_actor import create_movie_actor
from app.services.language import create_language
from app.services.movie import create_movie


def _make_actor(db_session, name="Leonardo", surname="DiCaprio", birthdate="1974-11-11"):
    return create_actor(
        CreateActor(name=name, surname=surname, birthdate=birthdate, bio="Actor"),
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


# POST /admin/movies/{movie_id}/actors/{actor_id}


def test_create_movie_actor_requires_admin(client, db_session):
    actor = _make_actor(db_session)
    movie = _make_movie(db_session)

    response = client.post(
        f"/admin/movies/{movie.id}/actors/{actor.id}", json={"character_name": "Cobb"}
    )

    assert response.status_code in (401, 403)


def test_create_movie_actor_as_admin(admin_client, db_session):
    actor = _make_actor(db_session)
    movie = _make_movie(db_session)

    response = admin_client.post(
        f"/admin/movies/{movie.id}/actors/{actor.id}", json={"character_name": "Cobb"}
    )

    assert response.status_code == 201


def test_create_movie_actor_duplicate_conflict(admin_client, db_session):
    actor = _make_actor(db_session)
    movie = _make_movie(db_session)

    admin_client.post(
        f"/admin/movies/{movie.id}/actors/{actor.id}", json={"character_name": "Cobb"}
    )
    response = admin_client.post(
        f"/admin/movies/{movie.id}/actors/{actor.id}", json={"character_name": "Cobb"}
    )

    assert response.status_code == 409


def test_create_movie_actor_movie_not_found(admin_client, db_session):
    actor = _make_actor(db_session)

    response = admin_client.post(
        f"/admin/movies/999/actors/{actor.id}", json={"character_name": "Cobb"}
    )

    assert response.status_code == 404


def test_create_movie_actor_actor_not_found(admin_client, db_session):
    movie = _make_movie(db_session)

    response = admin_client.post(
        f"/admin/movies/{movie.id}/actors/999", json={"character_name": "Cobb"}
    )

    assert response.status_code == 404


def test_create_movie_actor_invalid_payload(admin_client, db_session):
    actor = _make_actor(db_session)
    movie = _make_movie(db_session)

    response = admin_client.post(
        f"/admin/movies/{movie.id}/actors/{actor.id}", json={"character_name": ""}
    )

    assert response.status_code == 422


# GET /movies/{movie_id}/actors (public, lives in movie.py)


def test_get_movie_actors_public(client, db_session):
    actor = _make_actor(db_session)
    movie = _make_movie(db_session)
    create_movie_actor(movie.id, actor.id, CreateMovieActor(character_name="Cobb"), db_session)

    response = client.get(f"/movies/{movie.id}/actors")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["character_name"] == "Cobb"


def test_get_movie_actors_public_empty(client, db_session):
    movie = _make_movie(db_session)

    response = client.get(f"/movies/{movie.id}/actors")

    assert response.status_code == 200
    assert response.json() == []


def test_get_movie_actors_movie_not_found(client):
    response = client.get("/movies/999/actors")

    assert response.status_code == 404


def test_get_movie_actors_excludes_soft_deleted_actor(client, admin_client, db_session):
    actor = _make_actor(db_session)
    movie = _make_movie(db_session)
    create_movie_actor(movie.id, actor.id, CreateMovieActor(character_name="Cobb"), db_session)
    admin_client.delete(f"/admin/actors/{actor.id}")

    response = client.get(f"/movies/{movie.id}/actors")

    assert response.status_code == 200
    assert response.json() == []


# PATCH /admin/movies/{movie_id}/actors/{actor_id}


def test_update_movie_actor_requires_admin(client, db_session):
    actor = _make_actor(db_session)
    movie = _make_movie(db_session)
    create_movie_actor(movie.id, actor.id, CreateMovieActor(character_name="Cobb"), db_session)

    response = client.patch(
        f"/admin/movies/{movie.id}/actors/{actor.id}", json={"character_name": "Dom"}
    )

    assert response.status_code in (401, 403)


def test_update_movie_actor_as_admin(admin_client, db_session):
    actor = _make_actor(db_session)
    movie = _make_movie(db_session)
    create_movie_actor(movie.id, actor.id, CreateMovieActor(character_name="Cobb"), db_session)

    response = admin_client.patch(
        f"/admin/movies/{movie.id}/actors/{actor.id}", json={"character_name": "Dom Cobb"}
    )

    assert response.status_code == 200
    assert response.json()["character_name"] == "Dom Cobb"


def test_update_movie_actor_not_found(admin_client, db_session):
    actor = _make_actor(db_session)
    movie = _make_movie(db_session)

    response = admin_client.patch(
        f"/admin/movies/{movie.id}/actors/{actor.id}", json={"character_name": "Ghost"}
    )

    assert response.status_code == 404


def test_update_movie_actor_invalid_payload(admin_client, db_session):
    actor = _make_actor(db_session)
    movie = _make_movie(db_session)
    create_movie_actor(movie.id, actor.id, CreateMovieActor(character_name="Cobb"), db_session)

    response = admin_client.patch(
        f"/admin/movies/{movie.id}/actors/{actor.id}", json={"character_name": ""}
    )

    assert response.status_code == 422


# DELETE /admin/movies/{movie_id}/actors/{actor_id}


def test_delete_movie_actor_requires_admin(client, db_session):
    actor = _make_actor(db_session)
    movie = _make_movie(db_session)
    create_movie_actor(movie.id, actor.id, CreateMovieActor(character_name="Cobb"), db_session)

    response = client.delete(f"/admin/movies/{movie.id}/actors/{actor.id}")

    assert response.status_code in (401, 403)


def test_delete_movie_actor_as_admin(admin_client, db_session):
    actor = _make_actor(db_session)
    movie = _make_movie(db_session)
    create_movie_actor(movie.id, actor.id, CreateMovieActor(character_name="Cobb"), db_session)

    response = admin_client.delete(f"/admin/movies/{movie.id}/actors/{actor.id}")

    assert response.status_code == 204


def test_delete_movie_actor_not_found(admin_client, db_session):
    actor = _make_actor(db_session)
    movie = _make_movie(db_session)

    response = admin_client.delete(f"/admin/movies/{movie.id}/actors/{actor.id}")

    assert response.status_code == 404
