import pytest
from sqlalchemy import select

from app.exceptions.language import LanguageAlreadyExistsError, LanguageNotFoundError
from app.exceptions.movie import MovieAlreadyExistsError, MovieNotFoundError
from app.models.language import Language
from app.schemas.language import CreateLanguage
from app.schemas.movie import CreateMovie, UpdateMovie
from app.services.language import create_language
from app.services.movie import (
    create_movie,
    get_movie,
    get_movie_admin,
    get_movie_by_title,
    get_movies,
    get_movies_admin,
    restore_movie,
    soft_delete_movie,
    update_movie,
)


def _get_or_create_language(db_session, name="English", code="en"):
    try:
        return create_language(CreateLanguage(name=name, code=code), db_session)
    except LanguageAlreadyExistsError:
        return db_session.execute(select(Language).where(Language.code == code)).scalar_one()


def _make_movie(db_session, title="Test Movie", release_date="2020-01-01"):
    language = _get_or_create_language(db_session)
    return create_movie(
        CreateMovie(
            language_id=language.id,
            title=title,
            description="Test description",
            release_date=release_date,
            duration_time=120,
        ),
        db_session,
    )


# create_movie


def test_create_movie_success(db_session):
    movie = _make_movie(db_session)

    assert movie.id is not None
    assert movie.title == "Test Movie"


def test_create_movie_duplicate_raises(db_session):
    _make_movie(db_session)

    with pytest.raises(MovieAlreadyExistsError):
        _make_movie(db_session)


def test_create_movie_same_title_different_release_date_ok(db_session):
    _make_movie(db_session)  # release_date="2020-01-01" (default)
    movie = _make_movie(db_session, release_date="1999-01-01")  # remake, different date

    assert movie.id is not None


def test_create_movie_language_not_found_raises(db_session):
    with pytest.raises(LanguageNotFoundError):
        create_movie(
            CreateMovie(
                language_id=999,
                title="Test Movie",
                description="Test description",
                release_date="2020-01-01",
                duration_time=120,
            ),
            db_session,
        )


# get_movie


def test_get_movie_not_found_raises(db_session):
    with pytest.raises(MovieNotFoundError):
        get_movie(999, db_session)


def test_get_movie_success(db_session):
    created = _make_movie(db_session)
    fetched = get_movie(created.id, db_session)

    assert fetched.id == created.id


def test_get_movie_hides_soft_deleted(db_session):
    created = _make_movie(db_session)
    soft_delete_movie(created.id, db_session)

    with pytest.raises(MovieNotFoundError):
        get_movie(created.id, db_session)


def test_get_movie_admin_shows_soft_deleted(db_session):
    created = _make_movie(db_session)
    soft_delete_movie(created.id, db_session)

    fetched = get_movie_admin(created.id, db_session)
    assert fetched.id == created.id
    assert fetched.deleted_at is not None


# get_movies / get_movies_admin


def test_get_movies_pagination(db_session):
    for i in range(5):
        _make_movie(db_session, title=f"Movie {i}", release_date=f"200{i}-01-01")

    result = get_movies(db_session, offset=0, limit=3)
    assert len(result) == 3


def test_get_movies_excludes_soft_deleted(db_session):
    active = _make_movie(db_session, title="Active")
    deleted = _make_movie(db_session, title="Deleted", release_date="1999-01-01")
    soft_delete_movie(deleted.id, db_session)

    result = get_movies(db_session)

    assert len(result) == 1
    assert result[0].id == active.id


def test_get_movies_admin_includes_soft_deleted(db_session):
    active = _make_movie(db_session, title="Active")
    deleted = _make_movie(db_session, title="Deleted", release_date="1999-01-01")
    soft_delete_movie(deleted.id, db_session)

    result = get_movies_admin(db_session)

    assert len(result) == 2
    assert {active.id, deleted.id} == {m.id for m in result}


# get_movie_by_title


def test_get_movie_by_title_partial_match(db_session):
    _make_movie(db_session, title="Inception")

    result = get_movie_by_title("incep", db_session)

    assert len(result) == 1
    assert result[0].title == "Inception"


def test_get_movie_by_title_no_match(db_session):
    _make_movie(db_session, title="Inception")

    result = get_movie_by_title("nonexistent", db_session)

    assert result == []


def test_get_movie_by_title_excludes_soft_deleted(db_session):
    created = _make_movie(db_session, title="Inception")
    soft_delete_movie(created.id, db_session)

    result = get_movie_by_title("incep", db_session)

    assert result == []


def test_get_movie_by_title_pagination(db_session):
    for i in range(3):
        _make_movie(db_session, title=f"Inception {i}", release_date=f"200{i}-01-01")

    result = get_movie_by_title("incep", db_session, offset=0, limit=2)

    assert len(result) == 2


# update_movie


def test_update_movie_title_success(db_session):
    created = _make_movie(db_session)
    updated = update_movie(created.id, UpdateMovie(title="New Title"), db_session)

    assert updated.title == "New Title"


def test_update_movie_not_found_raises(db_session):
    with pytest.raises(MovieNotFoundError):
        update_movie(999, UpdateMovie(title="Ghost"), db_session)


def test_update_movie_conflicting_title_and_release_date_raises(db_session):
    _make_movie(db_session, title="Inception", release_date="2010-07-16")
    target = _make_movie(db_session, title="Interstellar", release_date="2014-11-07")

    with pytest.raises(MovieAlreadyExistsError):
        update_movie(
            target.id,
            UpdateMovie(title="Inception", release_date="2010-07-16"),
            db_session,
        )


def test_update_movie_language_not_found_raises(db_session):
    movie = _make_movie(db_session)

    with pytest.raises(LanguageNotFoundError):
        update_movie(movie.id, UpdateMovie(language_id=999), db_session)


# soft_delete_movie / restore_movie


def test_soft_delete_movie_success(db_session):
    created = _make_movie(db_session)
    deleted = soft_delete_movie(created.id, db_session)

    assert deleted.deleted_at is not None

    with pytest.raises(MovieNotFoundError):
        get_movie(created.id, db_session)


def test_soft_delete_movie_not_found_raises(db_session):
    with pytest.raises(MovieNotFoundError):
        soft_delete_movie(999, db_session)


def test_restore_movie_success(db_session):
    created = _make_movie(db_session)
    soft_delete_movie(created.id, db_session)

    restored = restore_movie(created.id, db_session)

    assert restored.deleted_at is None
    fetched = get_movie(created.id, db_session)
    assert fetched.id == created.id


def test_restore_movie_not_found_raises(db_session):
    with pytest.raises(MovieNotFoundError):
        restore_movie(999, db_session)
