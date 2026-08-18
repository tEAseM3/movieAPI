def _create_actor_via_api(client, name="Leonardo", surname="DiCaprio", birthdate="1974-11-11"):
    return client.post(
        "/admin/actors",
        json={"name": name, "surname": surname, "birthdate": birthdate, "bio": "Actor"},
    )


# POST /admin/actors


def test_create_actor_requires_admin(client):
    response = _create_actor_via_api(client)

    assert response.status_code in (401, 403)


def test_create_actor_as_admin(admin_client):
    response = _create_actor_via_api(admin_client)

    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Leonardo"
    assert "id" in data


def test_create_actor_duplicate_conflict(admin_client):
    _create_actor_via_api(admin_client)
    response = _create_actor_via_api(admin_client)

    assert response.status_code == 409


def test_create_actor_invalid_payload(admin_client):
    response = _create_actor_via_api(admin_client, name="")

    assert response.status_code == 422


# GET /actors


def test_get_actors_public(client, make_actor):
    make_actor()

    response = client.get("/actors")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["surname"] == "DiCaprio"


def test_get_actors_public_empty(client):
    response = client.get("/actors")

    assert response.status_code == 200
    assert response.json() == []


def test_get_actors_public_pagination(client, make_actor):
    for i in range(3):
        make_actor(name=f"Actor{i}", surname=f"Surname{i}")

    response = client.get("/actors?page=1&page_size=2")

    assert response.status_code == 200
    assert len(response.json()) == 2


def test_get_actors_public_excludes_soft_deleted(admin_client, make_actor):
    created = make_actor()
    admin_client.delete(f"/admin/actors/{created.id}")

    response = admin_client.get("/actors")

    assert response.status_code == 200
    assert response.json() == []


# GET /actors/{actor_id}


def test_get_actor_by_id_public(client, make_actor):
    actor = make_actor()

    response = client.get(f"/actors/{actor.id}")

    assert response.status_code == 200
    assert response.json()["name"] == "Leonardo"


def test_get_actor_by_id_not_found(client):
    response = client.get("/actors/999")

    assert response.status_code == 404


# GET /actors/{actor_id}/movies


def test_get_actor_movies_public_empty(client, make_actor):
    actor = make_actor()

    response = client.get(f"/actors/{actor.id}/movies")

    assert response.status_code == 200
    assert response.json() == []


def test_get_actor_movies_public(client, db_session, make_actor, make_movie):
    from app.schemas.actor import CreateMovieActor
    from app.services.actor.movie_actor import create_movie_actor

    actor = make_actor()
    movie = make_movie()
    create_movie_actor(movie.id, actor.id, CreateMovieActor(character_name="Cobb"), db_session)

    response = client.get(f"/actors/{actor.id}/movies")

    assert response.status_code == 200
    assert response.json()[0]["title"] == "Inception"


def test_get_actor_movies_not_found(client):
    response = client.get("/actors/999/movies")

    assert response.status_code == 404


# GET /admin/actors


def test_get_actors_admin_requires_admin(client):
    response = client.get("/admin/actors")

    assert response.status_code in (401, 403)


def test_get_actors_admin_includes_soft_deleted(admin_client, make_actor):
    created = make_actor()
    admin_client.delete(f"/admin/actors/{created.id}")

    response = admin_client.get("/admin/actors")

    assert response.status_code == 200
    assert len(response.json()) == 1


# GET /admin/actors/{actor_id}


def test_get_actor_admin_requires_admin(client, make_actor):
    actor = make_actor()

    response = client.get(f"/admin/actors/{actor.id}")

    assert response.status_code in (401, 403)


def test_get_actor_admin_not_found(admin_client):
    response = admin_client.get("/admin/actors/999")

    assert response.status_code == 404


def test_get_actor_admin_shows_soft_deleted(admin_client, make_actor):
    created = make_actor()
    admin_client.delete(f"/admin/actors/{created.id}")

    response = admin_client.get(f"/admin/actors/{created.id}")

    assert response.status_code == 200
    assert response.json()["deleted_at"] is not None


# PATCH /admin/actors/{actor_id}


def test_update_actor_requires_admin(client, make_actor):
    actor = make_actor()

    response = client.patch(f"/admin/actors/{actor.id}", json={"name": "New Name"})

    assert response.status_code in (401, 403)


def test_update_actor_as_admin(admin_client):
    create_response = _create_actor_via_api(admin_client)
    actor_id = create_response.json()["id"]

    response = admin_client.patch(f"/admin/actors/{actor_id}", json={"name": "Leo"})

    assert response.status_code == 200
    assert response.json()["name"] == "Leo"


def test_update_actor_not_found(admin_client):
    response = admin_client.patch("/admin/actors/999", json={"name": "Ghost"})

    assert response.status_code == 404


def test_update_actor_conflict(admin_client):
    _create_actor_via_api(admin_client, name="Leonardo", surname="DiCaprio")
    create_response = _create_actor_via_api(admin_client, name="Brad", surname="Pitt")
    actor_id = create_response.json()["id"]

    response = admin_client.patch(
        f"/admin/actors/{actor_id}",
        json={"name": "Leonardo", "surname": "DiCaprio", "birthdate": "1974-11-11"},
    )

    assert response.status_code == 409


# PATCH /admin/actors/{actor_id}/restore


def test_restore_actor_requires_admin(client, make_actor):
    actor = make_actor()

    response = client.patch(f"/admin/actors/{actor.id}/restore")

    assert response.status_code in (401, 403)


def test_restore_actor_as_admin(admin_client):
    create_response = _create_actor_via_api(admin_client)
    actor_id = create_response.json()["id"]
    admin_client.delete(f"/admin/actors/{actor_id}")

    response = admin_client.patch(f"/admin/actors/{actor_id}/restore")

    assert response.status_code == 200
    assert response.json()["deleted_at"] is None


def test_restore_actor_not_found(admin_client):
    response = admin_client.patch("/admin/actors/999/restore")

    assert response.status_code == 404


# DELETE /admin/actors/{actor_id}


def test_delete_actor_requires_admin(client, make_actor):
    actor = make_actor()

    response = client.delete(f"/admin/actors/{actor.id}")

    assert response.status_code in (401, 403)


def test_delete_actor_as_admin(admin_client):
    create_response = _create_actor_via_api(admin_client)
    actor_id = create_response.json()["id"]

    response = admin_client.delete(f"/admin/actors/{actor_id}")

    assert response.status_code == 200
    assert response.json()["deleted_at"] is not None

    get_response = admin_client.get(f"/actors/{actor_id}")
    assert get_response.status_code == 404


def test_delete_actor_not_found(admin_client):
    response = admin_client.delete("/admin/actors/999")

    assert response.status_code == 404
