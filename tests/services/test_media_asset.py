import pytest
from sqlalchemy import select

from app.exceptions.language import LanguageAlreadyExistsError
from app.exceptions.media_asset import MediaAssetNotFoundError
from app.exceptions.movie import MovieNotFoundError
from app.models.language import Language
from app.schemas.language import CreateLanguage
from app.schemas.media_asset import CreateMediaAsset, UpdateMediaAsset
from app.schemas.movie import CreateMovie
from app.services.language import create_language
from app.services.media_asset import (
    create_media_asset,
    get_media_asset,
    get_media_asset_admin,
    get_movie_media_assets,
    restore_media_asset,
    soft_delete_media_asset,
    update_media_asset,
)
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


# create_media_asset


def test_create_media_asset_success(db_session):
    movie = _make_movie(db_session)
    asset = _make_media_asset(db_session, movie.id)

    assert asset.id is not None
    assert asset.movie_id == movie.id
    assert asset.asset_type == "poster"


def test_create_media_asset_movie_not_found_raises(db_session):
    with pytest.raises(MovieNotFoundError):
        _make_media_asset(db_session, 999)


def test_create_media_asset_with_filepath_only(db_session):
    movie = _make_movie(db_session)

    asset = create_media_asset(
        movie.id,
        CreateMediaAsset(asset_type="poster", filepath="/images/poster.jpg"),
        db_session,
    )

    assert asset.filepath == "/images/poster.jpg"
    assert asset.url is None


# get_media_asset


def test_get_media_asset_not_found_raises(db_session):
    with pytest.raises(MediaAssetNotFoundError):
        get_media_asset(999, db_session)


def test_get_media_asset_success(db_session):
    movie = _make_movie(db_session)
    created = _make_media_asset(db_session, movie.id)

    fetched = get_media_asset(created.id, db_session)
    assert fetched.id == created.id


def test_get_media_asset_hides_soft_deleted(db_session):
    movie = _make_movie(db_session)
    created = _make_media_asset(db_session, movie.id)
    soft_delete_media_asset(created.id, db_session)

    with pytest.raises(MediaAssetNotFoundError):
        get_media_asset(created.id, db_session)


def test_get_media_asset_admin_shows_soft_deleted(db_session):
    movie = _make_movie(db_session)
    created = _make_media_asset(db_session, movie.id)
    soft_delete_media_asset(created.id, db_session)

    fetched = get_media_asset_admin(created.id, db_session)
    assert fetched.id == created.id
    assert fetched.deleted_at is not None


# get_movie_media_assets


def test_get_movie_media_assets_returns_list(db_session):
    movie = _make_movie(db_session)
    _make_media_asset(db_session, movie.id, asset_type="poster", url="http://example.com/1.jpg")
    _make_media_asset(db_session, movie.id, asset_type="backdrop", url="http://example.com/2.jpg")

    assets = get_movie_media_assets(movie.id, db_session)

    assert len(assets) == 2
    assert {a.asset_type for a in assets} == {"poster", "backdrop"}


def test_get_movie_media_assets_empty(db_session):
    movie = _make_movie(db_session)

    assets = get_movie_media_assets(movie.id, db_session)

    assert assets == []


def test_get_movie_media_assets_movie_not_found_raises(db_session):
    with pytest.raises(MovieNotFoundError):
        get_movie_media_assets(999, db_session)


def test_get_movie_media_assets_excludes_soft_deleted(db_session):
    movie = _make_movie(db_session)
    asset = _make_media_asset(db_session, movie.id)
    soft_delete_media_asset(asset.id, db_session)

    assets = get_movie_media_assets(movie.id, db_session)

    assert assets == []


# update_media_asset


def test_update_media_asset_success(db_session):
    movie = _make_movie(db_session)
    created = _make_media_asset(db_session, movie.id)

    updated = update_media_asset(
        created.id, UpdateMediaAsset(url="http://example.com/new.jpg"), db_session
    )

    assert updated.url == "http://example.com/new.jpg"


def test_update_media_asset_not_found_raises(db_session):
    with pytest.raises(MediaAssetNotFoundError):
        update_media_asset(999, UpdateMediaAsset(url="http://example.com/x.jpg"), db_session)


# soft_delete_media_asset / restore_media_asset


def test_soft_delete_media_asset_success(db_session):
    movie = _make_movie(db_session)
    created = _make_media_asset(db_session, movie.id)

    deleted = soft_delete_media_asset(created.id, db_session)

    assert deleted.deleted_at is not None
    with pytest.raises(MediaAssetNotFoundError):
        get_media_asset(created.id, db_session)


def test_soft_delete_media_asset_not_found_raises(db_session):
    with pytest.raises(MediaAssetNotFoundError):
        soft_delete_media_asset(999, db_session)


def test_restore_media_asset_success(db_session):
    movie = _make_movie(db_session)
    created = _make_media_asset(db_session, movie.id)
    soft_delete_media_asset(created.id, db_session)

    restored = restore_media_asset(created.id, db_session)

    assert restored.deleted_at is None
    fetched = get_media_asset(created.id, db_session)
    assert fetched.id == created.id


def test_restore_media_asset_not_found_raises(db_session):
    with pytest.raises(MediaAssetNotFoundError):
        restore_media_asset(999, db_session)
