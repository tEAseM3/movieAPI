import pytest

from app.exceptions.director import DirectorAlreadyExistsError, DirectorNotFoundError
from app.schemas.director import CreateDirector, UpdateDirector
from app.services.director.director import (
    create_director,
    get_director,
    get_director_admin,
    get_directors,
    get_directors_admin,
    restore_director,
    soft_delete_director,
    update_director,
)


def _make_director(
    db_session, name="Christopher", surname="Nolan", birthdate="1970-07-30", bio="Director"
):
    return create_director(
        CreateDirector(name=name, surname=surname, birthdate=birthdate, bio=bio),
        db_session,
    )


# create_director


def test_create_director_success(db_session):
    director = _make_director(db_session)

    assert director.id is not None
    assert director.name == "Christopher"
    assert director.surname == "Nolan"


def test_create_director_duplicate_raises(db_session):
    _make_director(db_session)

    with pytest.raises(DirectorAlreadyExistsError):
        _make_director(db_session)


def test_create_director_same_name_different_birthdate_ok(db_session):
    _make_director(db_session)
    director = _make_director(db_session, birthdate="1980-01-01")

    assert director.id is not None


# get_director and get_directors


def test_get_director_not_found_raises(db_session):
    with pytest.raises(DirectorNotFoundError):
        get_director(999, db_session)


def test_get_director_success(db_session):
    created = _make_director(db_session)
    fetched = get_director(created.id, db_session)

    assert fetched.id == created.id


def test_get_director_excludes_soft_deleted(db_session):
    created = _make_director(db_session)
    soft_delete_director(created.id, db_session)

    with pytest.raises(DirectorNotFoundError):
        get_director(created.id, db_session)


def test_get_director_admin_includes_soft_deleted(db_session):
    created = _make_director(db_session)
    soft_delete_director(created.id, db_session)

    fetched = get_director_admin(created.id, db_session)
    assert fetched.id == created.id
    assert fetched.deleted_at is not None


def test_get_directors_pagination(db_session):
    for i in range(5):
        _make_director(db_session, name=f"Director{i}", surname="Test")

    result = get_directors(db_session, offset=0, limit=3)
    assert len(result) == 3


def test_get_directors_excludes_soft_deleted(db_session):
    created = _make_director(db_session)
    soft_delete_director(created.id, db_session)

    result = get_directors(db_session)
    assert created.id not in [d.id for d in result]


def test_get_directors_admin_includes_soft_deleted(db_session):
    created = _make_director(db_session)
    soft_delete_director(created.id, db_session)

    result = get_directors_admin(db_session)
    assert created.id in [d.id for d in result]


# update_director


def test_update_director_success(db_session):
    created = _make_director(db_session)
    updated = update_director(created.id, UpdateDirector(bio="New bio"), db_session)

    assert updated.bio == "New bio"
    assert updated.name == "Christopher"


def test_update_director_conflicting_identity_raises(db_session):
    _make_director(db_session)
    target = _make_director(db_session, name="Quentin", surname="Tarantino", birthdate="1963-03-27")

    with pytest.raises(DirectorAlreadyExistsError):
        update_director(
            target.id,
            UpdateDirector(name="Christopher", surname="Nolan", birthdate="1970-07-30"),
            db_session,
        )


def test_update_director_same_identity_does_not_conflict_with_self(db_session):
    created = _make_director(db_session)

    updated = update_director(created.id, UpdateDirector(bio="Updated"), db_session)
    assert updated.name == "Christopher"


def test_update_director_not_found_raises(db_session):
    with pytest.raises(DirectorNotFoundError):
        update_director(999, UpdateDirector(bio="New bio"), db_session)


# soft_delete_director and restore_director


def test_soft_delete_director_sets_deleted_at(db_session):
    created = _make_director(db_session)
    deleted = soft_delete_director(created.id, db_session)

    assert deleted.deleted_at is not None


def test_soft_delete_director_not_found_raises(db_session):
    with pytest.raises(DirectorNotFoundError):
        soft_delete_director(999, db_session)


def test_restore_director_success(db_session):
    created = _make_director(db_session)
    soft_delete_director(created.id, db_session)

    restored = restore_director(created.id, db_session)

    assert restored.deleted_at is None

    fetched = get_director(created.id, db_session)
    assert fetched.id == created.id


def test_restore_director_not_found_raises(db_session):
    with pytest.raises(DirectorNotFoundError):
        restore_director(999, db_session)
