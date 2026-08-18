# POST /movies/{movie_id}/favorite


def test_create_favorite_requires_auth(client, make_movie):
    movie = make_movie()

    response = client.post(f"/movies/{movie.id}/favorite", json={})

    assert response.status_code == 401


def test_create_favorite_as_user(user_client, make_movie):
    movie = make_movie()

    response = user_client.post(f"/movies/{movie.id}/favorite", json={"content": "Watch again"})

    assert response.status_code == 201
    assert response.json()["movie_id"] == movie.id


def test_create_favorite_duplicate_conflict(user_client, make_movie):
    movie = make_movie()
    user_client.post(f"/movies/{movie.id}/favorite", json={})

    response = user_client.post(f"/movies/{movie.id}/favorite", json={})

    assert response.status_code == 409


def test_create_favorite_movie_not_found(user_client):
    response = user_client.post("/movies/999/favorite", json={})

    assert response.status_code == 404


def test_create_favorite_invalid_payload(user_client, make_movie):
    movie = make_movie()

    response = user_client.post(f"/movies/{movie.id}/favorite", json={"content": "x" * 1001})

    assert response.status_code == 422


# GET /users/me/favorites


def test_get_my_favorites_as_user(user_client, make_movie):
    first_movie = make_movie(title="First")
    second_movie = make_movie(title="Second")
    user_client.post(f"/movies/{first_movie.id}/favorite", json={})
    user_client.post(f"/movies/{second_movie.id}/favorite", json={})

    response = user_client.get("/users/me/favorites?page=1&page_size=1")

    assert response.status_code == 200
    assert len(response.json()) == 1


def test_get_my_favorites_requires_auth(client):
    response = client.get("/users/me/favorites")

    assert response.status_code == 401


# DELETE /movies/{movie_id}/favorite


def test_delete_favorite_as_user(user_client, make_movie):
    movie = make_movie()
    user_client.post(f"/movies/{movie.id}/favorite", json={})

    response = user_client.delete(f"/movies/{movie.id}/favorite")

    assert response.status_code == 204


def test_delete_favorite_not_found(user_client, make_movie):
    movie = make_movie()

    response = user_client.delete(f"/movies/{movie.id}/favorite")

    assert response.status_code == 404
