from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.exceptions.user import (
    CannotModifyOwnRoleError,
    UserAlreadyExistsError,
    UserNotFoundError,
)
from app.models.user import User
from app.schemas.user import UpdateUser, UpdateUserRole, UserCreate

# CREATE


def create_user(db: Session, user_data: UserCreate) -> User:
    if get_user_by_username(user_data.username, db) is not None:
        raise UserAlreadyExistsError(f"Username '{user_data.username}' is already taken")

    if get_user_by_email(user_data.email, db) is not None:
        raise UserAlreadyExistsError(f"Email '{user_data.email}' is already taken")

    user = User(
        username=user_data.username,
        email=user_data.email,
        password_hash=hash_password(user_data.password),
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user


# READ


def get_user_by_email(email: str, db: Session) -> User | None:
    result = db.execute(select(User).where(User.email == email))

    return result.scalar_one_or_none()


def get_user_by_username(username: str, db: Session) -> User | None:
    result = db.execute(select(User).where(User.username == username))

    return result.scalar_one_or_none()


def get_user(user_id: int, db: Session) -> User:
    result = db.execute(select(User).where(User.id == user_id, User.deleted_at.is_(None)))

    user = result.scalar_one_or_none()
    if user is None:
        raise UserNotFoundError(f"User with id = {user_id} not found")

    return user


def get_user_admin(user_id: int, db: Session) -> User:
    result = db.execute(select(User).where(User.id == user_id))

    user = result.scalar_one_or_none()
    if user is None:
        raise UserNotFoundError(f"User with id = {user_id} not found")

    return user


def get_users(db: Session, offset: int = 0, limit: int = 20) -> list[User]:
    result = db.execute(
        select(User).where(User.deleted_at.is_(None)).order_by(User.id).offset(offset).limit(limit)
    )

    return list(result.scalars().all())


def get_users_admin(db: Session, offset: int = 0, limit: int = 20) -> list[User]:
    result = db.execute(select(User).order_by(User.id).offset(offset).limit(limit))

    return list(result.scalars().all())


# UPDATE


def update_user(user_id: int, user_data: UpdateUser, db: Session) -> User:
    user = get_user(user_id, db)

    update_data = user_data.model_dump(exclude_unset=True)

    if "username" in update_data:
        existing = get_user_by_username(update_data["username"], db)
        if existing is not None and existing.id != user_id:
            raise UserAlreadyExistsError(f"Username '{update_data['username']}' is already taken")

    if "email" in update_data:
        existing = get_user_by_email(update_data["email"], db)
        if existing is not None and existing.id != user_id:
            raise UserAlreadyExistsError(f"Email '{update_data['email']}' is already taken")

    for field, value in update_data.items():
        setattr(user, field, value)

    db.commit()
    db.refresh(user)

    return user


def update_user_role(
    user_id: int, role_data: UpdateUserRole, current_admin: User, db: Session
) -> User:
    if user_id == current_admin.id:
        raise CannotModifyOwnRoleError()

    user = get_user_admin(user_id, db)
    user.role = role_data.role

    db.commit()
    db.refresh(user)

    return user


def restore_user(user_id: int, db: Session) -> User:
    user = get_user_admin(user_id, db)

    user.deleted_at = None

    db.commit()
    db.refresh(user)

    return user


# DELETE


def soft_delete_user(user_id: int, db: Session) -> User:
    user = get_user(user_id, db)

    user.deleted_at = datetime.now(UTC)

    db.commit()
    db.refresh(user)

    return user
