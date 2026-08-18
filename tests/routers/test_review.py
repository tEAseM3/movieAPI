from app.schemas.review import CreateReview
from app.services.review import create_review

# POST /movies/{movie_id}/reviews


def test_create_review_requires_auth(client, make_movie):
    movie = make_movie()

    response = client.post(f"/movies/{movie.id}/reviews", json={"content": "Excellent"})

    assert response.status_code == 401


def test_create_review_as_user(user_client, make_movie):
    movie = make_movie()

    response = user_client.post(f"/movies/{movie.id}/reviews", json={"content": "Excellent"})

    assert response.status_code == 200
    assert response.json()["content"] == "Excellent"


def test_create_review_duplicate_conflict(user_client, make_movie):
    movie = make_movie()
    user_client.post(f"/movies/{movie.id}/reviews", json={"content": "Excellent"})

    response = user_client.post(f"/movies/{movie.id}/reviews", json={"content": "Still excellent"})

    assert response.status_code == 409


def test_create_review_invalid_payload(user_client, make_movie):
    movie = make_movie()

    response = user_client.post(f"/movies/{movie.id}/reviews", json={"content": ""})

    assert response.status_code == 422


# GET /movies/{movie_id}/reviews and GET /reviews/{review_id}


def test_get_reviews_public(client, make_movie, make_user, db_session):
    movie = make_movie()
    user = make_user()
    create_review(movie.id, user.id, CreateReview(content="Excellent"), db_session)

    response = client.get(f"/movies/{movie.id}/reviews")

    assert response.status_code == 200
    assert response.json()[0]["content"] == "Excellent"


def test_get_reviews_movie_not_found(client):
    response = client.get("/movies/999/reviews")

    assert response.status_code == 404


def test_get_review_not_found(client):
    response = client.get("/reviews/999")

    assert response.status_code == 404


# GET /admin/reviews


def test_get_reviews_admin_requires_admin(client):
    response = client.get("/admin/reviews")

    assert response.status_code in (401, 403)


def test_get_reviews_admin(admin_client, make_movie, make_user, db_session):
    movie = make_movie()
    user = make_user()
    create_review(movie.id, user.id, CreateReview(content="Excellent"), db_session)

    response = admin_client.get("/admin/reviews")

    assert response.status_code == 200
    assert len(response.json()) == 1


# PATCH and DELETE /reviews/{review_id}


def test_update_review_as_author(user_client, make_movie):
    movie = make_movie()
    review_id = user_client.post(
        f"/movies/{movie.id}/reviews", json={"content": "Excellent"}
    ).json()["id"]

    response = user_client.patch(f"/reviews/{review_id}", json={"content": "Perfect"})

    assert response.status_code == 200
    assert response.json()["content"] == "Perfect"


def test_delete_review_as_author(user_client, make_movie):
    movie = make_movie()
    review_id = user_client.post(
        f"/movies/{movie.id}/reviews", json={"content": "Excellent"}
    ).json()["id"]

    response = user_client.delete(f"/reviews/{review_id}")

    assert response.status_code == 204


def test_delete_review_admin(admin_client, make_movie, make_user, db_session):
    movie = make_movie()
    user = make_user()
    review = create_review(movie.id, user.id, CreateReview(content="Excellent"), db_session)

    response = admin_client.delete(f"/admin/reviews/{review.id}")

    assert response.status_code == 204
