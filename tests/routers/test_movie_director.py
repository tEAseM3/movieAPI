from sqlalchemy import select

from app.models.language import Language
from app.schemas.director import CreateDirector
from app.schemas.language import CreateLanguage
from app.schemas.movie import CreateMovie
from app.services.director.director import create_director
from app.services.director.movie_director import create_movie_director
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


# POST /admin/directors/{director_id}/movies/{movie_id}


def test_add_movie_director_requires_admin(client, db_session):
    director = _make_director(db_session)
    movie = _make_movie(db_session)

    response = client.post(f"/admin/directors/{director.id}/movies/{movie.id}")

    assert response.status_code in (401, 403)


def test_add_movie_director_as_admin(admin_client, db_session):
    director = _make_director(db_session)
    movie = _make_movie(db_session)

    response = admin_client.post(f"/admin/directors/{director.id}/movies/{movie.id}")

    assert response.status_code == 201


def test_add_movie_director_duplicate_conflict(admin_client, db_session):
    director = _make_director(db_session)
    movie = _make_movie(db_session)

    admin_client.post(f"/admin/directors/{director.id}/movies/{movie.id}")
    response = admin_client.post(f"/admin/directors/{director.id}/movies/{movie.id}")

    assert response.status_code == 409


def test_add_movie_director_movie_not_found(admin_client, db_session):
    director = _make_director(db_session)

    response = admin_client.post(f"/admin/directors/{director.id}/movies/999")

    assert response.status_code == 404


def test_add_movie_director_director_not_found(admin_client, db_session):
    movie = _make_movie(db_session)

    response = admin_client.post(f"/admin/directors/999/movies/{movie.id}")

    assert response.status_code == 404


# GET /directors/{director_id}/movies (director/public.py)


def test_get_director_movies_public(client, db_session):
    director = _make_director(db_session)
    movie = _make_movie(db_session)
    create_movie_director(movie.id, director.id, db_session)

    response = client.get(f"/directors/{director.id}/movies")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["title"] == "Test Movie"


def test_get_director_movies_public_empty(client, db_session):
    director = _make_director(db_session)

    response = client.get(f"/directors/{director.id}/movies")

    assert response.status_code == 200
    assert response.json() == []


def test_get_director_movies_not_found(client):
    response = client.get("/directors/999/movies")

    assert response.status_code == 404


def test_get_director_movies_excludes_soft_deleted_movie(client, db_session):
    director = _make_director(db_session)
    movie = _make_movie(db_session)
    create_movie_director(movie.id, director.id, db_session)
    soft_delete_movie(movie.id, db_session)

    response = client.get(f"/directors/{director.id}/movies")

    assert response.status_code == 200
    assert response.json() == []


# GET /movies/{movie_id}/directors (movie.py)


def test_get_movie_directors_public(client, db_session):
    director = _make_director(db_session)
    movie = _make_movie(db_session)
    create_movie_director(movie.id, director.id, db_session)

    response = client.get(f"/movies/{movie.id}/directors")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["surname"] == "Nolan"


def test_get_movie_directors_public_empty(client, db_session):
    movie = _make_movie(db_session)

    response = client.get(f"/movies/{movie.id}/directors")

    assert response.status_code == 200
    assert response.json() == []


def test_get_movie_directors_movie_not_found(client):
    response = client.get("/movies/999/directors")

    assert response.status_code == 404


def test_get_movie_directors_excludes_soft_deleted_director(client, admin_client, db_session):
    director = _make_director(db_session)
    movie = _make_movie(db_session)
    create_movie_director(movie.id, director.id, db_session)
    admin_client.delete(f"/admin/directors/{director.id}")

    response = client.get(f"/movies/{movie.id}/directors")

    assert response.status_code == 200
    assert response.json() == []


# DELETE /admin/directors/{director_id}/movies/{movie_id}


def test_delete_movie_director_requires_admin(client, db_session):
    director = _make_director(db_session)
    movie = _make_movie(db_session)
    create_movie_director(movie.id, director.id, db_session)

    response = client.delete(f"/admin/directors/{director.id}/movies/{movie.id}")

    assert response.status_code in (401, 403)


def test_delete_movie_director_as_admin(admin_client, db_session):
    director = _make_director(db_session)
    movie = _make_movie(db_session)
    create_movie_director(movie.id, director.id, db_session)

    response = admin_client.delete(f"/admin/directors/{director.id}/movies/{movie.id}")

    assert response.status_code == 204


def test_delete_movie_director_not_found(admin_client, db_session):
    director = _make_director(db_session)
    movie = _make_movie(db_session)

    response = admin_client.delete(f"/admin/directors/{director.id}/movies/{movie.id}")

    assert response.status_code == 404
