import pytest

from app.exceptions.user import CannotModifyOwnRoleError, UserAlreadyExistsError, UserNotFoundError
from app.models.user import RoleEnum, User
from app.schemas.user import UpdateUser, UpdateUserRole, UserCreate
from app.services.user import (
    create_user,
    get_user,
    get_user_admin,
    get_users,
    get_users_admin,
    restore_user,
    soft_delete_user,
    update_user,
    update_user_role,
)


def _create_user(db_session, username="user", email="user@test.com", password="password123"):
    return create_user(
        db_session,
        UserCreate(username=username, email=email, password=password),
    )


# create_user


def test_create_user_success(db_session):
    user = _create_user(db_session)

    assert user.id is not None
    assert user.password_hash != "password123"


def test_create_user_duplicate_username_raises(db_session):
    _create_user(db_session)

    with pytest.raises(UserAlreadyExistsError):
        _create_user(db_session, email="other@test.com")


def test_create_user_duplicate_email_raises(db_session):
    _create_user(db_session)

    with pytest.raises(UserAlreadyExistsError):
        _create_user(db_session, username="other")


# get_user and get_users


def test_get_user_hides_soft_deleted(db_session):
    user = _create_user(db_session)
    soft_delete_user(user.id, db_session)

    with pytest.raises(UserNotFoundError):
        get_user(user.id, db_session)


def test_get_user_admin_shows_soft_deleted(db_session):
    user = _create_user(db_session)
    soft_delete_user(user.id, db_session)

    assert get_user_admin(user.id, db_session).id == user.id


def test_get_users_excludes_soft_deleted(db_session):
    active = _create_user(db_session)
    deleted = _create_user(db_session, username="deleted", email="deleted@test.com")
    soft_delete_user(deleted.id, db_session)

    assert [user.id for user in get_users(db_session)] == [active.id]


def test_get_users_admin_includes_soft_deleted(db_session):
    active = _create_user(db_session)
    deleted = _create_user(db_session, username="deleted", email="deleted@test.com")
    soft_delete_user(deleted.id, db_session)

    assert {user.id for user in get_users_admin(db_session)} == {active.id, deleted.id}


# update_user and update_user_role


def test_update_user_success(db_session):
    user = _create_user(db_session)

    updated = update_user(user.id, UpdateUser(username="updated"), db_session)

    assert updated.username == "updated"


def test_update_user_duplicate_email_raises(db_session):
    _create_user(db_session)
    target = _create_user(db_session, username="target", email="target@test.com")

    with pytest.raises(UserAlreadyExistsError):
        update_user(target.id, UpdateUser(email="user@test.com"), db_session)


def test_update_user_not_found_raises(db_session):
    with pytest.raises(UserNotFoundError):
        update_user(999, UpdateUser(username="updated"), db_session)


def test_update_user_role_success(db_session):
    user = _create_user(db_session)
    admin = User(id=999, username="admin", email="admin@test.com", password_hash="hash")

    updated = update_user_role(user.id, UpdateUserRole(role=RoleEnum.admin), admin, db_session)

    assert updated.role == RoleEnum.admin


def test_update_user_role_cannot_change_own_role(db_session):
    admin = _create_user(db_session, username="admin", email="admin@test.com")

    with pytest.raises(CannotModifyOwnRoleError):
        update_user_role(admin.id, UpdateUserRole(role=RoleEnum.admin), admin, db_session)


# soft_delete_user and restore_user


def test_soft_delete_and_restore_user(db_session):
    user = _create_user(db_session)
    soft_delete_user(user.id, db_session)

    restored = restore_user(user.id, db_session)

    assert restored.deleted_at is None
    assert get_user(user.id, db_session).id == user.id
