from sqlalchemy import select

from app.exceptions.language import LanguageAlreadyExistsError
from app.models.language import Language
from app.schemas.language import CreateLanguage
from app.schemas.media_asset import CreateMediaAsset
from app.schemas.movie import CreateMovie
from app.services.language import create_language
from app.services.media_asset import create_media_asset, soft_delete_media_asset
from app.services.movie import create_movie


def _get_or_create_language(db_session, name="English", code="en"):
    try:
        return create_language(CreateLanguage(name=name, code=code), db_session)
    except LanguageAlreadyExistsError:
        return db_session.execute(select(Language).where(Language.code == code)).scalar_one()


def _make_movie(db_session, title="Test Movie"):
    language = _get_or_create_language(db_session)
    return create_movie(
        CreateMovie(
            language_id=language.id,
            title=title,
            description="Test description",
            release_date="2020-01-01",
            duration_time=120,
        ),
        db_session,
    )


def _make_media_asset(
    db_session, movie_id, asset_type="poster", url="http://example.com/poster.jpg"
):
    return create_media_asset(
        movie_id, CreateMediaAsset(asset_type=asset_type, url=url), db_session
    )


def _create_media_asset_via_api(
    client, movie_id, asset_type="poster", url="http://example.com/poster.jpg"
):
    return client.post(
        f"/admin/media-assets/{movie_id}",
        json={"asset_type": asset_type, "url": url},
    )


# POST /admin/media-assets/{movie_id}


def test_create_media_asset_requires_admin(client, db_session):
    movie = _make_movie(db_session)

    response = _create_media_asset_via_api(client, movie.id)

    assert response.status_code in (401, 403)


def test_create_media_asset_as_admin(admin_client, db_session):
    movie = _make_movie(db_session)

    response = _create_media_asset_via_api(admin_client, movie.id)

    assert response.status_code == 201
    data = response.json()
    assert data["asset_type"] == "poster"
    assert "id" in data


def test_create_media_asset_movie_not_found(admin_client):
    response = _create_media_asset_via_api(admin_client, 999)

    assert response.status_code == 404


def test_create_media_asset_invalid_payload(admin_client, db_session):
    movie = _make_movie(db_session)

    response = admin_client.post(f"/admin/media-assets/{movie.id}", json={"asset_type": "poster"})

    assert response.status_code == 422


# GET /admin/media-assets/{media_asset_id}


def test_get_media_asset_admin_requires_admin(client, db_session):
    movie = _make_movie(db_session)
    asset = _make_media_asset(db_session, movie.id)

    response = client.get(f"/admin/media-assets/{asset.id}")

    assert response.status_code in (401, 403)


def test_get_media_asset_admin_not_found(admin_client):
    response = admin_client.get("/admin/media-assets/999")

    assert response.status_code == 404


def test_get_media_asset_admin_shows_soft_deleted_router(admin_client, db_session):
    movie = _make_movie(db_session)
    create_response = _create_media_asset_via_api(admin_client, movie.id)
    asset_id = create_response.json()["id"]
    admin_client.delete(f"/admin/media-assets/{asset_id}")

    response = admin_client.get(f"/admin/media-assets/{asset_id}")

    assert response.status_code == 200
    assert response.json()["deleted_at"] is not None


# GET /movies/{movie_id}/media-assets (public, lives in movie.py)


def test_get_movie_media_assets_public(client, db_session):
    movie = _make_movie(db_session)
    _make_media_asset(db_session, movie.id)

    response = client.get(f"/movies/{movie.id}/media-assets")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["asset_type"] == "poster"


def test_get_movie_media_assets_public_empty(client, db_session):
    movie = _make_movie(db_session)

    response = client.get(f"/movies/{movie.id}/media-assets")

    assert response.status_code == 200
    assert response.json() == []


def test_get_movie_media_assets_movie_not_found(client):
    response = client.get("/movies/999/media-assets")

    assert response.status_code == 404


def test_get_movie_media_assets_excludes_soft_deleted(client, db_session):
    movie = _make_movie(db_session)
    asset = _make_media_asset(db_session, movie.id)
    soft_delete_media_asset(asset.id, db_session)

    response = client.get(f"/movies/{movie.id}/media-assets")

    assert response.status_code == 200
    assert response.json() == []


# PATCH /admin/media-assets/{media_asset_id}


def test_update_media_asset_requires_admin(client, db_session):
    movie = _make_movie(db_session)
    asset = _make_media_asset(db_session, movie.id)

    response = client.patch(
        f"/admin/media-assets/{asset.id}", json={"url": "http://example.com/new.jpg"}
    )

    assert response.status_code in (401, 403)


def test_update_media_asset_as_admin(admin_client, db_session):
    movie = _make_movie(db_session)
    create_response = _create_media_asset_via_api(admin_client, movie.id)
    asset_id = create_response.json()["id"]

    response = admin_client.patch(
        f"/admin/media-assets/{asset_id}", json={"url": "http://example.com/new.jpg"}
    )

    assert response.status_code == 200
    assert response.json()["url"] == "http://example.com/new.jpg"


def test_update_media_asset_not_found(admin_client):
    response = admin_client.patch(
        "/admin/media-assets/999", json={"url": "http://example.com/x.jpg"}
    )

    assert response.status_code == 404


def test_update_media_asset_invalid_payload(admin_client, db_session):
    movie = _make_movie(db_session)
    asset = _make_media_asset(db_session, movie.id)

    response = admin_client.patch(f"/admin/media-assets/{asset.id}", json={"url": "u" * 1001})

    assert response.status_code == 422


# PATCH /admin/media-assets/{media_asset_id}/restore


def test_restore_media_asset_requires_admin(client, db_session):
    movie = _make_movie(db_session)
    asset = _make_media_asset(db_session, movie.id)
    soft_delete_media_asset(asset.id, db_session)

    response = client.patch(f"/admin/media-assets/{asset.id}/restore")

    assert response.status_code in (401, 403)


def test_restore_media_asset_as_admin(admin_client, db_session):
    movie = _make_movie(db_session)
    create_response = _create_media_asset_via_api(admin_client, movie.id)
    asset_id = create_response.json()["id"]
    admin_client.delete(f"/admin/media-assets/{asset_id}")

    response = admin_client.patch(f"/admin/media-assets/{asset_id}/restore")

    assert response.status_code == 200
    assert response.json()["deleted_at"] is None


def test_restore_media_asset_not_found(admin_client):
    response = admin_client.patch("/admin/media-assets/999/restore")

    assert response.status_code == 404


# DELETE /admin/media-assets/{media_asset_id}


def test_delete_media_asset_requires_admin(client, db_session):
    movie = _make_movie(db_session)
    asset = _make_media_asset(db_session, movie.id)

    response = client.delete(f"/admin/media-assets/{asset.id}")

    assert response.status_code in (401, 403)


def test_delete_media_asset_as_admin(admin_client, db_session):
    movie = _make_movie(db_session)
    create_response = _create_media_asset_via_api(admin_client, movie.id)
    asset_id = create_response.json()["id"]

    response = admin_client.delete(f"/admin/media-assets/{asset_id}")

    assert response.status_code == 200
    assert response.json()["deleted_at"] is not None


def test_delete_media_asset_not_found(admin_client):
    response = admin_client.delete("/admin/media-assets/999")

    assert response.status_code == 404
