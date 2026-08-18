import pytest

from app.exceptions.language import (
    LanguageAlreadyExistsError,
    LanguageInUseError,
    LanguageNotFoundError,
)
from app.schemas.language import UpdateLanguage
from app.services.language import (
    delete_language,
    get_language,
    get_language_movies,
    get_languages,
    update_language,
)
from app.services.movie import soft_delete_movie

# create_language


def test_create_language_success(make_language):
    language = make_language()

    assert language.id is not None
    assert language.name == "English"
    assert language.code == "en"


def test_create_language_duplicate_code_raises(make_language):
    make_language()  # name = "English", code = "en"

    with pytest.raises(LanguageAlreadyExistsError):
        make_language(name="English (United Kingdom)")  # code = "en"


def test_create_language_duplicate_name_raises(make_language):
    make_language()  # name = "English", code = "en"

    with pytest.raises(LanguageAlreadyExistsError):
        make_language(code="es")  # name = "English"


# get_language


def test_get_language_success(make_language, db_session):
    created = make_language()
    fetched = get_language(created.id, db_session)

    assert fetched.id == created.id


def test_get_language_not_found_raises(db_session):
    with pytest.raises(LanguageNotFoundError):
        get_language(999, db_session)


# get_languages


def test_get_languages_pagination(make_language, db_session):
    languages = [
        ("English", "en"),
        ("Spanish", "es"),
        ("French", "fr"),
        ("German", "de"),
        ("Japanese", "ja"),
    ]
    for name, code in languages:
        make_language(name=name, code=code)

    result = get_languages(db_session, offset=0, limit=3)
    assert len(result) == 3


# get_language_movies


def test_get_language_movies_returns_list(make_language, make_movie, db_session):
    language = make_language()
    make_movie(title="The Godfather", language_id=language.id)
    make_movie(title="Pulp Fiction", language_id=language.id)

    movies = get_language_movies(language.id, db_session)

    assert len(movies) == 2
    assert {m.title for m in movies} == {"The Godfather", "Pulp Fiction"}


def test_get_language_movies_empty(make_language, db_session):
    language = make_language()

    movies = get_language_movies(language.id, db_session)

    assert movies == []


def test_get_language_movies_not_found_raises(db_session):
    with pytest.raises(LanguageNotFoundError):
        get_language_movies(999, db_session)


def test_get_language_movies_excludes_soft_deleted(make_language, make_movie, db_session):
    language = make_language()
    movie = make_movie(language_id=language.id)
    soft_delete_movie(movie.id, db_session)

    movies = get_language_movies(language.id, db_session)

    assert movies == []


def test_get_language_movies_pagination(make_language, make_movie, db_session):
    language = make_language()
    titles = ["The Dark Knight", "Interstellar", "The Prestige"]
    for title in titles:
        make_movie(title=title, language_id=language.id)

    movies = get_language_movies(language.id, db_session, offset=0, limit=2)

    assert len(movies) == 2


# update_language


def test_update_language_name_success(make_language, db_session):
    created = make_language()
    updated = update_language(created.id, UpdateLanguage(name="English (US)"), db_session)

    assert updated.name == "English (US)"
    assert updated.code == "en"


def test_update_language_code_success(make_language, db_session):
    created = make_language()

    updated = update_language(created.id, UpdateLanguage(code="us"), db_session)

    assert updated.name == "English"
    assert updated.code == "us"


def test_update_language_conflicting_code_raises(make_language, db_session):
    make_language()  # name = "English", code = "en"
    target = make_language(name="Spanish", code="es")

    with pytest.raises(LanguageAlreadyExistsError):
        update_language(target.id, UpdateLanguage(code="en"), db_session)  # code = "en"


def test_update_language_conflicting_name_raises(make_language, db_session):
    make_language()  # name = "English", code = "en"
    target = make_language(name="Spanish", code="es")

    with pytest.raises(LanguageAlreadyExistsError):
        update_language(target.id, UpdateLanguage(name="English"), db_session)


def test_update_language_same_name_does_not_conflict_with_self(make_language, db_session):
    created = make_language()  # name = "English"

    updated = update_language(created.id, UpdateLanguage(name="English"), db_session)
    assert updated.name == "English"


def test_update_language_not_found_raises(db_session):
    with pytest.raises(LanguageNotFoundError):
        update_language(999, UpdateLanguage(name="Korean"), db_session)


# delete_language


def test_delete_language_success(make_language, db_session):
    created = make_language()
    delete_language(created.id, db_session)

    with pytest.raises(LanguageNotFoundError):
        get_language(created.id, db_session)


def test_delete_language_not_found_raises(db_session):
    with pytest.raises(LanguageNotFoundError):
        delete_language(999, db_session)


def test_delete_language_in_use_raises(make_language, make_movie, db_session):
    language = make_language()
    make_movie(language_id=language.id)

    with pytest.raises(LanguageInUseError):
        delete_language(language.id, db_session)
