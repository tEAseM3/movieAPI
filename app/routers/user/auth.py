from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.auth import RefreshRequest, TokenResponse
from app.services.auth import login_user, logout_user, refresh_access_token

router = APIRouter(prefix="/auth", tags=["Auth"])

# POST


@router.post("/login", response_model=TokenResponse)
def login_endpoint(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Annotated[Session, Depends(get_db)],
):
    return login_user(form_data.username, form_data.password, db)


@router.post("/refresh", response_model=TokenResponse)
def refresh_endpoint(
    body: RefreshRequest,
    db: Annotated[Session, Depends(get_db)],
):
    return refresh_access_token(body.refresh_token, db)


@router.post("/logout", status_code=204)
def logout_endpoint(
    body: RefreshRequest,
    db: Annotated[Session, Depends(get_db)],
):
    logout_user(body.refresh_token, db)
