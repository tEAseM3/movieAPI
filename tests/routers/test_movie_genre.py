from app.services.genre.movie_genre import create_movie_genre

# POST /admin/movies/{movie_id}/genres/{genre_id}


def test_add_movie_genre_requires_admin(client, make_genre, make_movie):
    genre = make_genre()
    movie = make_movie()

    response = client.post(f"/admin/movies/{movie.id}/genres/{genre.id}")

    assert response.status_code in (401, 403)


def test_add_movie_genre_as_admin(admin_client, make_genre, make_movie):
    genre = make_genre()
    movie = make_movie()

    response = admin_client.post(f"/admin/movies/{movie.id}/genres/{genre.id}")

    assert response.status_code == 201


def test_add_movie_genre_duplicate_conflict(admin_client, make_genre, make_movie):
    genre = make_genre()
    movie = make_movie()

    admin_client.post(f"/admin/movies/{movie.id}/genres/{genre.id}")
    response = admin_client.post(f"/admin/movies/{movie.id}/genres/{genre.id}")

    assert response.status_code == 409


def test_add_movie_genre_movie_not_found(admin_client, make_genre):
    genre = make_genre()

    response = admin_client.post(f"/admin/movies/999/genres/{genre.id}")

    assert response.status_code == 404


def test_add_movie_genre_genre_not_found(admin_client, make_movie):
    movie = make_movie()

    response = admin_client.post(f"/admin/movies/{movie.id}/genres/999")

    assert response.status_code == 404


# GET /movies/{movie_id}/genres (public, lives in movie.py)


def test_get_movie_genres_public(client, make_genre, make_movie, db_session):
    genre = make_genre()
    movie = make_movie()
    create_movie_genre(movie.id, genre.id, db_session)

    response = client.get(f"/movies/{movie.id}/genres")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["name"] == "Action"


def test_get_movie_genres_public_empty(client, make_movie):
    movie = make_movie()

    response = client.get(f"/movies/{movie.id}/genres")

    assert response.status_code == 200
    assert response.json() == []


def test_get_movie_genres_movie_not_found(client):
    response = client.get("/movies/999/genres")

    assert response.status_code == 404


# DELETE /admin/movies/{movie_id}/genres/{genre_id}


def test_delete_movie_genre_requires_admin(client, make_genre, make_movie, db_session):
    genre = make_genre()
    movie = make_movie()
    create_movie_genre(movie.id, genre.id, db_session)

    response = client.delete(f"/admin/movies/{movie.id}/genres/{genre.id}")

    assert response.status_code in (401, 403)


def test_delete_movie_genre_as_admin(admin_client, make_genre, make_movie, db_session):
    genre = make_genre()
    movie = make_movie()
    create_movie_genre(movie.id, genre.id, db_session)

    response = admin_client.delete(f"/admin/movies/{movie.id}/genres/{genre.id}")

    assert response.status_code == 204


def test_delete_movie_genre_not_found(admin_client, make_genre, make_movie):
    genre = make_genre()
    movie = make_movie()

    response = admin_client.delete(f"/admin/movies/{movie.id}/genres/{genre.id}")

    assert response.status_code == 404
