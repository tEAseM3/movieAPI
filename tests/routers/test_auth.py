def _register_user(client):
    return client.post(
        "/users/register",
        json={"username": "user", "email": "user@test.com", "password": "password123"},
    )


def _login(client, username="user", password="password123"):
    return client.post("/auth/login", data={"username": username, "password": password})


# POST /auth/login


def test_login_success(client):
    _register_user(client)

    response = _login(client)

    assert response.status_code == 200
    assert response.json()["token_type"] == "bearer"
    assert response.json()["access_token"]
    assert response.json()["refresh_token"]


def test_login_invalid_credentials(client):
    _register_user(client)

    response = _login(client, password="wrong-password")

    assert response.status_code == 401


def test_login_missing_form_fields(client):
    response = client.post("/auth/login", data={})

    assert response.status_code == 422


# POST /auth/refresh


def test_refresh_rotates_token(client):
    _register_user(client)
    tokens = _login(client).json()

    response = client.post("/auth/refresh", json={"refresh_token": tokens["refresh_token"]})

    assert response.status_code == 200
    assert response.json()["refresh_token"] != tokens["refresh_token"]


def test_refresh_revoked_token_is_unauthorized(client):
    _register_user(client)
    tokens = _login(client).json()
    client.post("/auth/refresh", json={"refresh_token": tokens["refresh_token"]})

    response = client.post("/auth/refresh", json={"refresh_token": tokens["refresh_token"]})

    assert response.status_code == 401


# POST /auth/logout


def test_logout_revokes_token(client):
    _register_user(client)
    tokens = _login(client).json()

    response = client.post("/auth/logout", json={"refresh_token": tokens["refresh_token"]})

    assert response.status_code == 204

    refresh_response = client.post("/auth/refresh", json={"refresh_token": tokens["refresh_token"]})
    assert refresh_response.status_code == 401
