import os

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.auth import get_current_admin, get_current_user
from app.db.base import Base
from app.db.database import get_db
from app.main import app
from app.models.user import RoleEnum, User
from app.schemas.actor import CreateActor
from app.schemas.director import CreateDirector
from app.schemas.genre import CreateGenre
from app.schemas.language import CreateLanguage
from app.schemas.movie import CreateMovie
from app.services.actor.actor import create_actor
from app.services.director.director import create_director
from app.services.genre.genre import create_genre
from app.services.language import create_language
from app.services.movie import create_movie

TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL", "postgresql+psycopg2://test:test@localhost:5432/test_db"
)

engine = create_engine(TEST_DATABASE_URL)
TestingSessionLocal = sessionmaker(bind=engine)


@pytest.fixture()
def db_session():
    Base.metadata.create_all(engine)
    session = TestingSessionLocal()
    yield session
    session.close()
    Base.metadata.drop_all(engine)


@pytest.fixture()
def client(db_session):
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()


@pytest.fixture()
def admin_client(db_session):
    fake_admin = User(id=1, username="admin", email="admin@test.com", role="admin")

    def override_get_db():
        yield db_session

    def override_get_current_admin():
        return fake_admin

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_admin] = override_get_current_admin
    yield TestClient(app)
    app.dependency_overrides.clear()


@pytest.fixture()
def make_user(db_session):
    counter = 0

    def _make_user(username=None, email=None):
        nonlocal counter
        counter += 1
        username = username or f"user{counter}"
        email = email or f"{username}@test.com"
        user = User(
            username=username,
            email=email,
            password_hash="test-password",
            role=RoleEnum.user,
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        return user

    return _make_user


@pytest.fixture()
def user_client(db_session, make_user):
    user = make_user()

    def override_get_db():
        yield db_session

    def override_get_current_user():
        return user

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = override_get_current_user
    yield TestClient(app)
    app.dependency_overrides.clear()


@pytest.fixture()
def make_language(db_session):
    def _make_language(name="English", code="en"):
        return create_language(CreateLanguage(name=name, code=code), db_session)

    return _make_language


@pytest.fixture()
def make_movie(db_session, make_language):
    cache = {}

    def _make_movie(
        title="Inception",
        language_id=None,
        release_date="2010-07-16",
        description="A thief who steals corporate secrets through dream-sharing technology",
        duration_time=148,
    ):
        if language_id is None:
            if "default" not in cache:
                cache["default"] = make_language().id
            language_id = cache["default"]

        return create_movie(
            CreateMovie(
                language_id=language_id,
                title=title,
                description=description,
                release_date=release_date,
                duration_time=duration_time,
            ),
            db_session,
        )

    return _make_movie


@pytest.fixture()
def make_genre(db_session):
    def _make_genre(name="Action"):
        return create_genre(CreateGenre(name=name), db_session)

    return _make_genre


@pytest.fixture()
def make_actor(db_session):
    def _make_actor(name="Leonardo", surname="DiCaprio", birthdate="1974-11-11"):
        return create_actor(
            CreateActor(name=name, surname=surname, birthdate=birthdate, bio="Actor"),
            db_session,
        )

    return _make_actor


@pytest.fixture()
def make_director(db_session):
    def _make_director(name="Christopher", surname="Nolan", birthdate="1970-07-30"):
        return create_director(
            CreateDirector(name=name, surname=surname, birthdate=birthdate, bio="Director"),
            db_session,
        )

    return _make_director
