from app.schemas.rating import CreateRating
from app.services.rating import create_rating

# POST /movies/{movie_id}/rating


def test_create_rating_requires_auth(client, make_movie):
    movie = make_movie()

    response = client.post(f"/movies/{movie.id}/rating", json={"rating": 8})

    assert response.status_code == 401


def test_create_rating_as_user(user_client, make_movie):
    movie = make_movie()

    response = user_client.post(f"/movies/{movie.id}/rating", json={"rating": 8})

    assert response.status_code == 201
    assert response.json()["rating"] == 8


def test_create_rating_duplicate_conflict(user_client, make_movie):
    movie = make_movie()
    user_client.post(f"/movies/{movie.id}/rating", json={"rating": 8})

    response = user_client.post(f"/movies/{movie.id}/rating", json={"rating": 9})

    assert response.status_code == 409


def test_create_rating_movie_not_found(user_client):
    response = user_client.post("/movies/999/rating", json={"rating": 8})

    assert response.status_code == 404


def test_create_rating_invalid_payload(user_client, make_movie):
    movie = make_movie()

    response = user_client.post(f"/movies/{movie.id}/rating", json={"rating": 11})

    assert response.status_code == 422


# GET /movies/{movie_id}/rating


def test_get_movie_rating_public(make_movie, make_user, client, db_session):
    movie = make_movie()
    first_user = make_user()
    second_user = make_user()
    create_rating(movie.id, first_user.id, CreateRating(rating=8), db_session)
    create_rating(movie.id, second_user.id, CreateRating(rating=9), db_session)

    response = client.get(f"/movies/{movie.id}/rating")

    assert response.status_code == 200
    assert response.json() == {"average_rating": 8.5, "ratings_count": 2}


def test_get_movie_rating_not_found(client):
    response = client.get("/movies/999/rating")

    assert response.status_code == 404


# PATCH /movies/{movie_id}/rating


def test_update_rating_as_user(user_client, make_movie):
    movie = make_movie()
    user_client.post(f"/movies/{movie.id}/rating", json={"rating": 8})

    response = user_client.patch(f"/movies/{movie.id}/rating", json={"rating": 10})

    assert response.status_code == 200
    assert response.json()["rating"] == 10


def test_update_rating_not_found(user_client, make_movie):
    movie = make_movie()

    response = user_client.patch(f"/movies/{movie.id}/rating", json={"rating": 8})

    assert response.status_code == 404


# DELETE /movies/{movie_id}/rating


def test_delete_rating_as_user(user_client, make_movie):
    movie = make_movie()
    user_client.post(f"/movies/{movie.id}/rating", json={"rating": 8})

    response = user_client.delete(f"/movies/{movie.id}/rating")

    assert response.status_code == 204
