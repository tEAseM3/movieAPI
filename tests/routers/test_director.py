def _create_director_via_api(client, name="Christopher", surname="Nolan", birthdate="1970-07-30"):
    return client.post(
        "/admin/directors",
        json={"name": name, "surname": surname, "birthdate": birthdate, "bio": "Director"},
    )


# POST /admin/directors


def test_create_director_requires_admin(client):
    response = _create_director_via_api(client)

    assert response.status_code in (401, 403)


def test_create_director_as_admin(admin_client):
    response = _create_director_via_api(admin_client)

    assert response.status_code == 201
    data = response.json()
    assert data["surname"] == "Nolan"
    assert "id" in data


def test_create_director_duplicate_conflict(admin_client):
    _create_director_via_api(admin_client)
    response = _create_director_via_api(admin_client)

    assert response.status_code == 409


def test_create_director_invalid_payload(admin_client):
    response = _create_director_via_api(admin_client, name="")

    assert response.status_code == 422


# GET /directors


def test_get_directors_public(client, make_director):
    make_director()

    response = client.get("/directors")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["surname"] == "Nolan"


def test_get_directors_public_excludes_soft_deleted(client, admin_client, make_director):
    director = make_director()
    admin_client.delete(f"/admin/directors/{director.id}")

    response = client.get("/directors")

    assert response.status_code == 200
    assert response.json() == []


def test_get_directors_public_empty(client):
    response = client.get("/directors")

    assert response.status_code == 200
    assert response.json() == []


def test_get_directors_public_pagination(client, make_director):
    for i in range(3):
        make_director(name=f"Director{i}", surname="Test")

    response = client.get("/directors?page=1&page_size=2")

    assert response.status_code == 200
    assert len(response.json()) == 2


# GET /directors/{director_id}


def test_get_director_by_id_public(client, make_director):
    director = make_director()

    response = client.get(f"/directors/{director.id}")

    assert response.status_code == 200
    assert response.json()["surname"] == "Nolan"


def test_get_director_by_id_not_found(client):
    response = client.get("/directors/999")

    assert response.status_code == 404


# PATCH /admin/directors/{director_id}


def test_update_director_as_admin(admin_client):
    create_response = _create_director_via_api(admin_client)
    director_id = create_response.json()["id"]

    response = admin_client.patch(f"/admin/directors/{director_id}", json={"bio": "Updated bio"})

    assert response.status_code == 200
    assert response.json()["bio"] == "Updated bio"


def test_update_director_requires_admin(client, make_director):
    director = make_director()

    response = client.patch(f"/admin/directors/{director.id}", json={"bio": "Updated bio"})

    assert response.status_code in (401, 403)


def test_update_director_not_found(admin_client):
    response = admin_client.patch("/admin/directors/999", json={"bio": "New bio"})

    assert response.status_code == 404


# PATCH /admin/directors/{director_id}/restore


def test_restore_director_as_admin(admin_client):
    create_response = _create_director_via_api(admin_client)
    director_id = create_response.json()["id"]

    admin_client.delete(f"/admin/directors/{director_id}")

    response = admin_client.patch(f"/admin/directors/{director_id}/restore")

    assert response.status_code == 200
    assert response.json()["deleted_at"] is None


def test_restore_director_not_found(admin_client):
    response = admin_client.patch("/admin/directors/999/restore")

    assert response.status_code == 404


def test_restore_director_requires_admin(client, make_director):
    director = make_director()

    response = client.patch(f"/admin/directors/{director.id}/restore")

    assert response.status_code in (401, 403)


# DELETE /admin/directors/{director_id} (soft delete)


def test_soft_delete_director_as_admin(admin_client):
    create_response = _create_director_via_api(admin_client)
    director_id = create_response.json()["id"]

    response = admin_client.delete(f"/admin/directors/{director_id}")

    assert response.status_code == 200
    assert response.json()["deleted_at"] is not None

    get_response = admin_client.get(f"/directors/{director_id}")
    assert get_response.status_code == 404


def test_soft_delete_director_requires_admin(client, make_director):
    director = make_director()

    response = client.delete(f"/admin/directors/{director.id}")

    assert response.status_code in (401, 403)
