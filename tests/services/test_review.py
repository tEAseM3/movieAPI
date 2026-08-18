import pytest

from app.exceptions.movie import MovieNotFoundError
from app.exceptions.review import (
    ReviewAlreadyExistsError,
    ReviewNotFoundError,
    ReviewPermissionError,
)
from app.schemas.review import CreateReview, UpdateReview
from app.services.review import (
    create_review,
    delete_review,
    delete_review_admin,
    get_review,
    get_reviews,
    get_reviews_admin,
    update_review,
)

# create_review


def test_create_review_success(make_movie, make_user, db_session):
    movie = make_movie()
    user = make_user()

    review = create_review(movie.id, user.id, CreateReview(content="Excellent"), db_session)

    assert review.content == "Excellent"


def test_create_review_duplicate_raises(make_movie, make_user, db_session):
    movie = make_movie()
    user = make_user()
    create_review(movie.id, user.id, CreateReview(content="Excellent"), db_session)

    with pytest.raises(ReviewAlreadyExistsError):
        create_review(movie.id, user.id, CreateReview(content="Still excellent"), db_session)


def test_create_review_movie_not_found_raises(make_user, db_session):
    user = make_user()

    with pytest.raises(MovieNotFoundError):
        create_review(999, user.id, CreateReview(content="Excellent"), db_session)


# get_review and get_reviews


def test_get_reviews_returns_movie_reviews(make_movie, make_user, db_session):
    movie = make_movie()
    first_user = make_user()
    second_user = make_user()
    create_review(movie.id, first_user.id, CreateReview(content="Excellent"), db_session)
    create_review(movie.id, second_user.id, CreateReview(content="Great"), db_session)

    reviews = get_reviews(movie.id, db_session)

    assert len(reviews) == 2


def test_get_reviews_movie_not_found_raises(db_session):
    with pytest.raises(MovieNotFoundError):
        get_reviews(999, db_session)


def test_get_review_not_found_raises(db_session):
    with pytest.raises(ReviewNotFoundError):
        get_review(999, db_session)


# update_review


def test_update_review_success(make_movie, make_user, db_session):
    movie = make_movie()
    user = make_user()
    review = create_review(movie.id, user.id, CreateReview(content="Excellent"), db_session)

    updated = update_review(review.id, user.id, UpdateReview(content="Perfect"), db_session)

    assert updated.content == "Perfect"


def test_update_review_forbidden_for_other_user(make_movie, make_user, db_session):
    movie = make_movie()
    author = make_user()
    other_user = make_user()
    review = create_review(movie.id, author.id, CreateReview(content="Excellent"), db_session)

    with pytest.raises(ReviewPermissionError):
        update_review(review.id, other_user.id, UpdateReview(content="Perfect"), db_session)


# delete_review


def test_delete_review_success(make_movie, make_user, db_session):
    movie = make_movie()
    user = make_user()
    review = create_review(movie.id, user.id, CreateReview(content="Excellent"), db_session)

    delete_review(review.id, user.id, db_session)

    with pytest.raises(ReviewNotFoundError):
        get_review(review.id, db_session)


def test_delete_review_forbidden_for_other_user(make_movie, make_user, db_session):
    movie = make_movie()
    author = make_user()
    other_user = make_user()
    review = create_review(movie.id, author.id, CreateReview(content="Excellent"), db_session)

    with pytest.raises(ReviewPermissionError):
        delete_review(review.id, other_user.id, db_session)


def test_delete_review_admin_success(make_movie, make_user, db_session):
    movie = make_movie()
    user = make_user()
    review = create_review(movie.id, user.id, CreateReview(content="Excellent"), db_session)

    delete_review_admin(review.id, db_session)

    assert get_reviews_admin(db_session) == []
