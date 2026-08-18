from sqlalchemy import select

from app.exceptions.language import LanguageAlreadyExistsError
from app.models.language import Language
from app.schemas.language import CreateLanguage
from app.schemas.movie import CreateMovie
from app.services.language import create_language
from app.services.movie import create_movie, soft_delete_movie


def _get_or_create_language(db_session, name="English", code="en"):
    try:
        return create_language(CreateLanguage(name=name, code=code), db_session)
    except LanguageAlreadyExistsError:
        return db_session.execute(select(Language).where(Language.code == code)).scalar_one()


def _make_movie(db_session, title="Test Movie", release_date="2020-01-01"):
    language = _get_or_create_language(db_session)
    return create_movie(
        CreateMovie(
            language_id=language.id,
            title=title,
            description="Test description",
            release_date=release_date,
            duration_time=120,
        ),
        db_session,
    )


def _create_movie_via_api(client, db_session, title="Test Movie", release_date="2020-01-01"):
    language = _get_or_create_language(db_session)
    return client.post(
        "/admin/movies",
        json={
            "language_id": language.id,
            "title": title,
            "description": "Test description",
            "release_date": release_date,
            "duration_time": 120,
        },
    )


# POST /admin/movies


def test_create_movie_requires_admin(client, db_session):
    response = _create_movie_via_api(client, db_session)

    assert response.status_code in (401, 403)


def test_create_movie_as_admin(admin_client, db_session):
    response = _create_movie_via_api(admin_client, db_session)

    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Test Movie"
    assert "id" in data


def test_create_movie_duplicate_conflict(admin_client, db_session):
    _create_movie_via_api(admin_client, db_session)
    response = _create_movie_via_api(admin_client, db_session)

    assert response.status_code == 409


def test_create_movie_language_not_found(admin_client):
    response = admin_client.post(
        "/admin/movies",
        json={
            "language_id": 999,
            "title": "Test Movie",
            "description": "Test description",
            "release_date": "2020-01-01",
            "duration_time": 120,
        },
    )

    assert response.status_code == 404


def test_create_movie_invalid_payload(admin_client, db_session):
    language = _get_or_create_language(db_session)

    response = admin_client.post(
        "/admin/movies",
        json={
            "language_id": language.id,
            "title": "",
            "release_date": "2020-01-01",
            "duration_time": 0,
        },
    )

    assert response.status_code == 422


# GET /movies/{movie_id}


def test_get_movie_public(client, db_session):
    movie = _make_movie(db_session)

    response = client.get(f"/movies/{movie.id}")

    assert response.status_code == 200
    assert response.json()["title"] == "Test Movie"


def test_get_movie_by_id_not_found(client):
    response = client.get("/movies/999")

    assert response.status_code == 404


# GET /movies


def test_get_movies_public(client, db_session):
    _make_movie(db_session)

    response = client.get("/movies")

    assert response.status_code == 200
    assert len(response.json()) == 1


def test_get_movies_public_empty(client):
    response = client.get("/movies")

    assert response.status_code == 200
    assert response.json() == []


def test_get_movies_public_pagination(client, db_session):
    for i in range(3):
        _make_movie(db_session, title=f"Movie {i}", release_date=f"200{i}-01-01")

    response = client.get("/movies?page=1&page_size=2")

    assert response.status_code == 200
    assert len(response.json()) == 2


def test_get_movies_public_excludes_soft_deleted(client, db_session):
    movie = _make_movie(db_session)
    soft_delete_movie(movie.id, db_session)

    response = client.get("/movies")

    assert response.status_code == 200
    assert response.json() == []


# GET /movies/search


def test_search_movies_partial_match(client, db_session):
    _make_movie(db_session, title="Inception")

    response = client.get("/movies/search?movie_title=incep")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["title"] == "Inception"


def test_search_movies_no_match(client, db_session):
    _make_movie(db_session, title="Inception")

    response = client.get("/movies/search?movie_title=nonexistent")

    assert response.status_code == 200
    assert response.json() == []


def test_search_movies_missing_query_param(client):
    response = client.get("/movies/search")

    assert response.status_code == 422


def test_search_movies_pagination(client, db_session):
    for i in range(3):
        _make_movie(db_session, title=f"Inception {i}", release_date=f"200{i}-01-01")

    response = client.get("/movies/search?movie_title=incep&page=1&page_size=2")

    assert response.status_code == 200
    assert len(response.json()) == 2


def test_search_movies_excludes_soft_deleted(client, db_session):
    movie = _make_movie(db_session, title="Inception")
    soft_delete_movie(movie.id, db_session)

    response = client.get("/movies/search?movie_title=incep")

    assert response.status_code == 200
    assert response.json() == []


# GET /movies (filters and sorting)


def test_get_movies_uses_simple_pagination(client, db_session):
    _make_movie(db_session, title="Later", release_date="2020-01-01")
    _make_movie(db_session, title="Earlier", release_date="2010-01-01")

    response = client.get("/movies?page=1&page_size=1")

    assert response.status_code == 200
    assert len(response.json()) == 1


# GET /admin/movies/{movie_id}


def test_get_movie_admin_requires_admin(client):
    response = client.get("/admin/movies/1")

    assert response.status_code in (401, 403)


def test_get_movie_admin_not_found(admin_client):
    response = admin_client.get("/admin/movies/999")

    assert response.status_code == 404


def test_get_movie_admin_shows_soft_deleted(admin_client, db_session):
    create_response = _create_movie_via_api(admin_client, db_session)
    movie_id = create_response.json()["id"]
    admin_client.delete(f"/admin/movies/{movie_id}")

    response = admin_client.get(f"/admin/movies/{movie_id}")

    assert response.status_code == 200
    assert response.json()["deleted_at"] is not None


# GET /admin/movies


def test_get_movies_admin_requires_admin(client):
    response = client.get("/admin/movies")

    assert response.status_code in (401, 403)


def test_get_movies_admin_includes_soft_deleted(admin_client, db_session):
    create_response = _create_movie_via_api(admin_client, db_session)
    movie_id = create_response.json()["id"]
    admin_client.delete(f"/admin/movies/{movie_id}")

    response = admin_client.get("/admin/movies")

    assert response.status_code == 200
    assert len(response.json()) == 1


# PATCH /admin/movies/{movie_id}


def test_update_movie_requires_admin(client, db_session):
    movie = _make_movie(db_session)

    response = client.patch(f"/admin/movies/{movie.id}", json={"title": "New Title"})

    assert response.status_code in (401, 403)


def test_update_movie_as_admin(admin_client, db_session):
    create_response = _create_movie_via_api(admin_client, db_session)
    movie_id = create_response.json()["id"]

    response = admin_client.patch(f"/admin/movies/{movie_id}", json={"title": "New Title"})

    assert response.status_code == 200
    assert response.json()["title"] == "New Title"


def test_update_movie_not_found(admin_client):
    response = admin_client.patch("/admin/movies/999", json={"title": "Ghost"})

    assert response.status_code == 404


def test_update_movie_duplicate_conflict(admin_client, db_session):
    _create_movie_via_api(admin_client, db_session, title="Inception", release_date="2010-07-16")
    movie_id = _create_movie_via_api(
        admin_client, db_session, title="Interstellar", release_date="2014-11-07"
    ).json()["id"]

    response = admin_client.patch(
        f"/admin/movies/{movie_id}",
        json={"title": "Inception", "release_date": "2010-07-16"},
    )

    assert response.status_code == 409


# PATCH /admin/movies/{movie_id}/restore


def test_restore_movie_requires_admin(client, db_session):
    movie = _make_movie(db_session)
    soft_delete_movie(movie.id, db_session)

    response = client.patch(f"/admin/movies/{movie.id}/restore")

    assert response.status_code in (401, 403)


def test_restore_movie_as_admin(admin_client, db_session):
    create_response = _create_movie_via_api(admin_client, db_session)
    movie_id = create_response.json()["id"]
    admin_client.delete(f"/admin/movies/{movie_id}")

    response = admin_client.patch(f"/admin/movies/{movie_id}/restore")

    assert response.status_code == 200
    assert response.json()["deleted_at"] is None


def test_restore_movie_not_found(admin_client):
    response = admin_client.patch("/admin/movies/999/restore")

    assert response.status_code == 404


# DELETE /admin/movies/{movie_id}


def test_delete_movie_requires_admin(client, db_session):
    movie = _make_movie(db_session)

    response = client.delete(f"/admin/movies/{movie.id}")

    assert response.status_code in (401, 403)


def test_delete_movie_as_admin(admin_client, db_session):
    create_response = _create_movie_via_api(admin_client, db_session)
    movie_id = create_response.json()["id"]

    response = admin_client.delete(f"/admin/movies/{movie_id}")

    assert response.status_code == 200
    assert response.json()["deleted_at"] is not None

    get_response = admin_client.get(f"/movies/{movie_id}")
    assert get_response.status_code == 404


def test_delete_movie_not_found(admin_client):
    response = admin_client.delete("/admin/movies/999")

    assert response.status_code == 404
