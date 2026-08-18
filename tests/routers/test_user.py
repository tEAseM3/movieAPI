from app.models.user import RoleEnum


def _register_user(client, username="user", email="user@test.com", password="password123"):
    return client.post(
        "/users/register",
        json={"username": username, "email": email, "password": password},
    )


# POST /users/register


def test_register_user_success(client):
    response = _register_user(client)

    assert response.status_code == 201
    assert response.json()["username"] == "user"
    assert "password" not in response.json()


def test_register_user_duplicate_conflict(client):
    _register_user(client)

    response = _register_user(client)

    assert response.status_code == 409


def test_register_user_invalid_payload(client):
    response = _register_user(client, username="ab", email="invalid", password="short")

    assert response.status_code == 422


# GET /users/me


def test_get_me_requires_auth(client):
    response = client.get("/users/me")

    assert response.status_code == 401


def test_get_me_as_user(user_client):
    response = user_client.get("/users/me")

    assert response.status_code == 200
    assert response.json()["username"] == "user1"


# GET /users/me/profile


def test_get_my_profile_includes_user_activity(user_client, make_movie):
    movie = make_movie()
    user_client.post(f"/movies/{movie.id}/reviews", json={"content": "Great"})
    user_client.post(f"/movies/{movie.id}/rating", json={"rating": 9})
    user_client.post(f"/movies/{movie.id}/favorite", json={"content": "Rewatch"})

    response = user_client.get("/users/me/profile")

    assert response.status_code == 200
    profile = response.json()
    assert profile["reviews"][0]["movie_id"] == movie.id
    assert profile["ratings"][0]["rating"] == 9
    assert profile["favorites"][0]["content"] == "Rewatch"


# PATCH /users/me


def test_update_me_as_user(user_client):
    response = user_client.patch("/users/me", json={"username": "updated"})

    assert response.status_code == 200
    assert response.json()["username"] == "updated"


def test_update_me_duplicate_conflict(user_client, make_user):
    make_user(username="taken", email="taken@test.com")

    response = user_client.patch("/users/me", json={"username": "taken"})

    assert response.status_code == 409


# DELETE /users/me


def test_delete_me_as_user(user_client):
    response = user_client.delete("/users/me")

    assert response.status_code == 204


# GET /admin/users


def test_get_users_admin_requires_admin(client):
    response = client.get("/admin/users")

    assert response.status_code in (401, 403)


def test_get_users_admin(admin_client, make_user):
    make_user()

    response = admin_client.get("/admin/users")

    assert response.status_code == 200
    assert len(response.json()) == 1


def test_get_user_admin_not_found(admin_client):
    response = admin_client.get("/admin/users/999")

    assert response.status_code == 404


# PATCH /admin/users/{user_id}/role


def test_update_user_role_as_admin(admin_client, make_user):
    make_user()
    user = make_user()

    response = admin_client.patch(f"/admin/users/{user.id}/role", json={"role": "admin"})

    assert response.status_code == 200
    assert response.json()["role"] == RoleEnum.admin


def test_update_own_role_conflict(admin_client, make_user):
    admin = make_user()

    response = admin_client.patch(f"/admin/users/{admin.id}/role", json={"role": "admin"})

    assert response.status_code == 409


# DELETE /admin/users/{user_id} and PATCH /admin/users/{user_id}/restore


def test_soft_delete_and_restore_user_as_admin(admin_client, make_user):
    user = make_user()

    delete_response = admin_client.delete(f"/admin/users/{user.id}")
    restore_response = admin_client.patch(f"/admin/users/{user.id}/restore")

    assert delete_response.status_code == 204
    assert restore_response.status_code == 200
