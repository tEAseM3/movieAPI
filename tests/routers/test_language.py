from app.services.movie import soft_delete_movie


def _create_language_api(client, name="English", code="en"):
    return client.post("/admin/languages", json={"name": name, "code": code})


# POST /admin/languages


def test_create_language_requires_admin(client):
    response = _create_language_api(client)

    assert response.status_code in (401, 403)


def test_create_language_as_admin(admin_client):
    response = _create_language_api(admin_client)

    assert response.status_code == 201
    data = response.json()
    assert data["code"] == "en"
    assert "id" in data


def test_create_language_duplicate_code_conflict(admin_client):
    _create_language_api(admin_client)  # name = "English", code = "en"
    response = _create_language_api(admin_client, name="English (United Kingdom)")  # code = "en"

    assert response.status_code == 409


def test_create_language_duplicate_name_conflict(admin_client):
    _create_language_api(admin_client)
    response = _create_language_api(admin_client, code="us")

    assert response.status_code == 409


def test_create_language_invalid_payload(admin_client):
    response = admin_client.post("/admin/languages", json={"name": "", "code": "e"})

    assert response.status_code == 422


# GET /languages


def test_get_languages_public(client, make_language):
    make_language()

    response = client.get("/languages")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["code"] == "en"


def test_get_languages_public_empty(client):
    response = client.get("/languages")

    assert response.status_code == 200
    assert response.json() == []


def test_get_languages_public_pagination(client, make_language):
    for name, code in [("English", "en"), ("Spanish", "es"), ("French", "fr")]:
        make_language(name=name, code=code)

    response = client.get("/languages?page=1&page_size=2")

    assert response.status_code == 200
    assert len(response.json()) == 2


def test_get_languages_invalid_pagination(client):
    response = client.get("/languages?page_size=101")

    assert response.status_code == 422


# GET /languages/{language_id}


def test_get_language_by_id_public(client, make_language):
    language = make_language()

    response = client.get(f"/languages/{language.id}")

    assert response.status_code == 200
    assert response.json()["name"] == "English"


def test_get_language_by_id_not_found(client):
    response = client.get("/languages/999")

    assert response.status_code == 404


# GET /languages/{language_id}/movies


def test_get_language_movies_public(client, make_language, make_movie):
    language = make_language()
    make_movie(title="Inception", language_id=language.id)
    make_movie(title="The Dark Knight", language_id=language.id)

    response = client.get(f"/languages/{language.id}/movies")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2


def test_get_language_movies_public_empty(client, make_language):
    language = make_language()

    response = client.get(f"/languages/{language.id}/movies")

    assert response.status_code == 200
    assert response.json() == []


def test_get_language_movies_not_found(client):
    response = client.get("/languages/999/movies")

    assert response.status_code == 404


def test_get_language_movies_public_excludes_soft_deleted(
    client, make_language, make_movie, db_session
):
    language = make_language()
    movie = make_movie(language_id=language.id)
    soft_delete_movie(movie.id, db_session)

    response = client.get(f"/languages/{language.id}/movies")

    assert response.status_code == 200
    assert response.json() == []


def test_get_language_movies_public_pagination(client, make_language, make_movie):
    language = make_language()
    for title in ["Inception", "The Dark Knight", "Interstellar"]:
        make_movie(title=title, language_id=language.id)

    response = client.get(f"/languages/{language.id}/movies?page=1&page_size=2")

    assert response.status_code == 200
    assert len(response.json()) == 2


# PATCH /admin/languages/{language_id}


def test_update_language_requires_admin(client, make_language):
    language = make_language()

    response = client.patch(f"/admin/languages/{language.id}", json={"name": "English (US)"})

    assert response.status_code in (401, 403)


def test_update_language_as_admin(admin_client):
    create_response = _create_language_api(admin_client)
    language_id = create_response.json()["id"]

    response = admin_client.patch(f"/admin/languages/{language_id}", json={"name": "English (US)"})

    assert response.status_code == 200
    assert response.json()["name"] == "English (US)"


def test_update_language_code(admin_client):
    language_id = _create_language_api(admin_client).json()["id"]

    response = admin_client.patch(f"/admin/languages/{language_id}", json={"code": "us"})

    assert response.status_code == 200
    assert response.json()["code"] == "us"


def test_update_language_duplicate_conflict(admin_client):
    _create_language_api(admin_client)
    language_id = _create_language_api(admin_client, name="Spanish", code="es").json()["id"]

    response = admin_client.patch(f"/admin/languages/{language_id}", json={"name": "English"})

    assert response.status_code == 409


def test_update_language_not_found(admin_client):
    response = admin_client.patch("/admin/languages/999", json={"name": "English (US)"})

    assert response.status_code == 404


def test_update_language_partial(admin_client):
    language_id = _create_language_api(admin_client).json()["id"]

    response = admin_client.patch(f"/admin/languages/{language_id}", json={})

    assert response.status_code == 200
    assert response.json()["name"] == "English"


def test_update_language_invalid_payload(admin_client):
    language_id = _create_language_api(admin_client).json()["id"]

    response = admin_client.patch(f"/admin/languages/{language_id}", json={"code": "e"})

    assert response.status_code == 422


# DELETE /admin/languages/{language_id}


def test_delete_language_requires_admin(client, make_language):
    language = make_language()

    response = client.delete(f"/admin/languages/{language.id}")

    assert response.status_code in (401, 403)


def test_delete_language_as_admin(admin_client):
    create_response = _create_language_api(admin_client)
    language_id = create_response.json()["id"]

    response = admin_client.delete(f"/admin/languages/{language_id}")

    assert response.status_code == 204

    get_response = admin_client.get(f"/languages/{language_id}")
    assert get_response.status_code == 404


def test_delete_language_not_found(admin_client):
    response = admin_client.delete("/admin/languages/999")

    assert response.status_code == 404


def test_delete_language_in_use_conflict(admin_client, make_movie):
    create_response = _create_language_api(admin_client)
    language_id = create_response.json()["id"]

    make_movie(language_id=language_id)

    response = admin_client.delete(f"/admin/languages/{language_id}")

    assert response.status_code == 409
