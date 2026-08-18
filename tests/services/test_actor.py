import pytest

from app.exceptions.actor import ActorAlreadyExistsError, ActorNotFoundError
from app.schemas.actor import UpdateActor
from app.services.actor.actor import (
    get_actor,
    get_actor_admin,
    get_actors,
    get_actors_admin,
    restore_actor,
    soft_delete_actor,
    update_actor,
)

# create_actor


def test_create_actor_success(make_actor):
    actor = make_actor()

    assert actor.id is not None
    assert actor.name == "Leonardo"
    assert actor.surname == "DiCaprio"


def test_create_actor_duplicate_raises(make_actor):
    make_actor()

    with pytest.raises(ActorAlreadyExistsError):
        make_actor()


def test_create_actor_same_name_different_birthdate_ok(make_actor):
    make_actor()  # birthdate по умолчанию "1974-11-11"
    actor = make_actor(birthdate="1980-01-01")  # другая дата — не дубликат

    assert actor.id is not None


# get_actor


def test_get_actor_not_found_raises(db_session):
    with pytest.raises(ActorNotFoundError):
        get_actor(999, db_session)


def test_get_actor_success(db_session, make_actor):
    created = make_actor()
    fetched = get_actor(created.id, db_session)

    assert fetched.id == created.id


def test_get_actor_hides_soft_deleted(db_session, make_actor):
    created = make_actor()
    soft_delete_actor(created.id, db_session)

    with pytest.raises(ActorNotFoundError):
        get_actor(created.id, db_session)


def test_get_actor_admin_shows_soft_deleted(db_session, make_actor):
    created = make_actor()
    soft_delete_actor(created.id, db_session)

    fetched = get_actor_admin(created.id, db_session)
    assert fetched.id == created.id
    assert fetched.deleted_at is not None


# get_actors / get_actors_admin


def test_get_actors_pagination(db_session, make_actor):
    for i in range(5):
        make_actor(name=f"Actor{i}", surname=f"Surname{i}")

    result = get_actors(db_session, offset=0, limit=3)
    assert len(result) == 3


def test_get_actors_excludes_soft_deleted(db_session, make_actor):
    active = make_actor(name="Active", surname="Actor")
    deleted = make_actor(name="Deleted", surname="Actor")
    soft_delete_actor(deleted.id, db_session)

    result = get_actors(db_session)

    assert len(result) == 1
    assert result[0].id == active.id


def test_get_actors_admin_includes_soft_deleted(db_session, make_actor):
    active = make_actor(name="Active", surname="Actor")
    deleted = make_actor(name="Deleted", surname="Actor")
    soft_delete_actor(deleted.id, db_session)

    result = get_actors_admin(db_session)

    assert len(result) == 2
    assert {active.id, deleted.id} == {a.id for a in result}


# update_actor


def test_update_actor_name_success(db_session, make_actor):
    created = make_actor()
    updated = update_actor(created.id, UpdateActor(name="Leo"), db_session)

    assert updated.name == "Leo"
    assert updated.surname == "DiCaprio"


def test_update_actor_conflicting_identity_raises(db_session, make_actor):
    make_actor()  # Leonardo DiCaprio, 1974-11-11 (default)
    target = make_actor(name="Brad", surname="Pitt", birthdate="1963-12-18")

    with pytest.raises(ActorAlreadyExistsError):
        update_actor(
            target.id,
            UpdateActor(name="Leonardo", surname="DiCaprio", birthdate="1974-11-11"),
            db_session,
        )


def test_update_actor_same_identity_does_not_conflict_with_self(db_session, make_actor):
    created = make_actor()

    updated = update_actor(created.id, UpdateActor(bio="Updated bio"), db_session)
    assert updated.name == "Leonardo"


def test_update_actor_partial_change_does_not_trigger_conflict_check(db_session, make_actor):
    created = make_actor()

    updated = update_actor(created.id, UpdateActor(bio="New bio"), db_session)
    assert updated.bio == "New bio"


def test_update_actor_not_found_raises(db_session):
    with pytest.raises(ActorNotFoundError):
        update_actor(999, UpdateActor(name="Ghost"), db_session)


# soft_delete_actor / restore_actor


def test_soft_delete_actor_success(db_session, make_actor):
    created = make_actor()
    deleted = soft_delete_actor(created.id, db_session)

    assert deleted.deleted_at is not None

    with pytest.raises(ActorNotFoundError):
        get_actor(created.id, db_session)


def test_soft_delete_actor_not_found_raises(db_session):
    with pytest.raises(ActorNotFoundError):
        soft_delete_actor(999, db_session)


def test_restore_actor_success(db_session, make_actor):
    created = make_actor()
    soft_delete_actor(created.id, db_session)

    restored = restore_actor(created.id, db_session)

    assert restored.deleted_at is None
    fetched = get_actor(created.id, db_session)
    assert fetched.id == created.id


def test_restore_actor_not_found_raises(db_session):
    with pytest.raises(ActorNotFoundError):
        restore_actor(999, db_session)
