from sqlalchemy import select

from app.core.security import password_hash
from app.db.database import SessionLocal
from app.models.user import RoleEnum, User

USERS = [
    {
        "username": "admin",
        "password": "qwerty123",
        "email": "admin@example.com",
        "role": RoleEnum.admin,
    },
    {
        "username": "user",
        "password": "qwerty123",
        "email": "user@example.com",
        "role": RoleEnum.user,
    },
]


def seed_users() -> None:
    db = SessionLocal()

    try:
        created_count = 0
        skipped_count = 0

        for user_data in USERS:
            existing_user = db.scalar(
                select(User).where(
                    (User.username == user_data["username"]) | (User.email == user_data["email"])
                )
            )

            if existing_user:
                skipped_count += 1

                print(f"Skipped user '{user_data['username']}' - username or email already exists")

                continue

            user = User(
                username=user_data["username"],
                password_hash=password_hash.hash(user_data["password"]),
                email=user_data["email"],
                role=user_data["role"],
            )

            db.add(user)
            created_count += 1

            print(f"Created user: {user_data['username']} ({user_data['role'].value})")

        db.commit()

        print(f"\nCreated = {created_count}, Skipped = {skipped_count}")

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


if __name__ == "__main__":
    seed_users()
