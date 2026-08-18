from app.services.genre.movie_genre import create_movie_genre
from app.services.movie import soft_delete_movie


def _create_genre_api(client, name="Action"):
    return client.post("/admin/genres", json={"name": name})


# POST /admin/genres


def test_create_genre_requires_admin(client):
    response = _create_genre_api(client)

    assert response.status_code in (401, 403)


def test_create_genre_as_admin(admin_client):
    response = _create_genre_api(admin_client)

    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Action"
    assert "id" in data


def test_create_genre_duplicate_conflict(admin_client):
    _create_genre_api(admin_client)  # name = "Action"
    response = _create_genre_api(admin_client)  # name = "Action"

    assert response.status_code == 409


def test_create_genre_invalid_payload(admin_client):
    response = admin_client.post("/admin/genres", json={"name": ""})

    assert response.status_code == 422


# GET /genres


def test_get_genres_public(client, make_genre):
    make_genre()

    response = client.get("/genres")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["name"] == "Action"


def test_get_genres_public_empty(client):
    response = client.get("/genres")

    assert response.status_code == 200
    assert response.json() == []


def test_get_genres_public_pagination(client, make_genre):
    for name in ["Action", "Comedy", "Drama"]:
        make_genre(name=name)

    response = client.get("/genres?page=1&page_size=2")

    assert response.status_code == 200
    assert len(response.json()) == 2


def test_get_genres_invalid_pagination(client):
    response = client.get("/genres?page=0")

    assert response.status_code == 422


# GET /genres/{genre_id}


def test_get_genre_by_id_public(client, make_genre):
    genre = make_genre()

    response = client.get(f"/genres/{genre.id}")

    assert response.status_code == 200
    assert response.json()["name"] == "Action"


def test_get_genre_by_id_not_found(client):
    response = client.get("/genres/999")

    assert response.status_code == 404


# GET /genres/{genre_id}/movies


def test_get_genre_movies_public(client, make_genre, make_movie, db_session):
    genre = make_genre()
    movie = make_movie()
    create_movie_genre(movie.id, genre.id, db_session)

    response = client.get(f"/genres/{genre.id}/movies")

    assert response.status_code == 200
    assert response.json()[0]["title"] == "Inception"


def test_get_genre_movies_public_empty(client, make_genre):
    genre = make_genre()

    response = client.get(f"/genres/{genre.id}/movies")

    assert response.status_code == 200
    assert response.json() == []


def test_get_genre_movies_not_found(client):
    response = client.get("/genres/999/movies")

    assert response.status_code == 404


def test_get_genre_movies_public_pagination(client, make_genre, make_movie, db_session):
    genre = make_genre()
    for title in ["Inception", "Interstellar", "The Dark Knight"]:
        movie = make_movie(title=title)
        create_movie_genre(movie.id, genre.id, db_session)

    response = client.get(f"/genres/{genre.id}/movies?page=1&page_size=2")

    assert response.status_code == 200
    assert len(response.json()) == 2


def test_get_genre_movies_excludes_soft_deleted(client, make_genre, make_movie, db_session):
    genre = make_genre()
    movie = make_movie()
    create_movie_genre(movie.id, genre.id, db_session)
    soft_delete_movie(movie.id, db_session)

    response = client.get(f"/genres/{genre.id}/movies")

    assert response.status_code == 200
    assert response.json() == []


# PATCH /admin/genres/{genre_id}


def test_update_genre_requires_admin(client, make_genre):
    genre = make_genre()

    response = client.patch(f"/admin/genres/{genre.id}", json={"name": "New Name"})

    assert response.status_code in (401, 403)


def test_update_genre_as_admin(admin_client):
    create_response = _create_genre_api(admin_client)
    genre_id = create_response.json()["id"]

    response = admin_client.patch(f"/admin/genres/{genre_id}", json={"name": "Action & Adventure"})

    assert response.status_code == 200
    assert response.json()["name"] == "Action & Adventure"


def test_update_genre_not_found(admin_client):
    response = admin_client.patch("/admin/genres/999", json={"name": "New Name"})

    assert response.status_code == 404


def test_update_genre_duplicate_conflict(admin_client):
    _create_genre_api(admin_client, name="Action")
    genre_id = _create_genre_api(admin_client, name="Comedy").json()["id"]

    response = admin_client.patch(f"/admin/genres/{genre_id}", json={"name": "Action"})

    assert response.status_code == 409


def test_update_genre_invalid_payload(admin_client):
    genre_id = _create_genre_api(admin_client).json()["id"]

    response = admin_client.patch(f"/admin/genres/{genre_id}", json={"name": "a" * 56})

    assert response.status_code == 422


def test_update_genre_partial(admin_client):
    create_response = _create_genre_api(admin_client, name="Original")
    genre_id = create_response.json()["id"]

    response = admin_client.patch(f"/admin/genres/{genre_id}", json={})

    assert response.status_code == 200
    assert response.json()["name"] == "Original"


# DELETE /admin/genres/{genre_id}


def test_delete_genre_requires_admin(client, make_genre):
    genre = make_genre()

    response = client.delete(f"/admin/genres/{genre.id}")

    assert response.status_code in (401, 403)


def test_delete_genre_as_admin(admin_client):
    create_response = _create_genre_api(admin_client)
    genre_id = create_response.json()["id"]

    response = admin_client.delete(f"/admin/genres/{genre_id}")

    assert response.status_code == 204

    get_response = admin_client.get(f"/genres/{genre_id}")
    assert get_response.status_code == 404


def test_delete_genre_not_found(admin_client):
    response = admin_client.delete("/admin/genres/999")

    assert response.status_code == 404
