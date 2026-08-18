from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.auth import get_current_admin
from app.db.database import get_db
from app.models.user import User
from app.schemas.review import DisplayReview
from app.services.review import delete_review_admin, get_reviews_admin

router = APIRouter(prefix="/admin/reviews", tags=["Admin Reviews"])

# GET


@router.get("", response_model=list[DisplayReview])
def get_reviews_admin_endpoint(
    db: Annotated[Session, Depends(get_db)],
    current_admin: Annotated[User, Depends(get_current_admin)],
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=100)] = 20,
):
    offset = (page - 1) * page_size
    return get_reviews_admin(db, offset, page_size)


# DELETE


@router.delete("/{review_id}", status_code=204)
def delete_review_admin_endpoint(
    review_id: int,
    db: Annotated[Session, Depends(get_db)],
    current_admin: Annotated[User, Depends(get_current_admin)],
):
    delete_review_admin(review_id, db)
