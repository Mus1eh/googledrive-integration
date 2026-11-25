from typing import Annotated

from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm

from app.dependencies.authentication import CurrentUser, DBSession
from app.models.user import User
from app.schemas.auth import RefreshTokenRequest, TokenResponse
from app.schemas.user import UserCreate, UserMe
from app.services.authentication.login import login_user
from app.services.authentication.logout import (
    logout_all_devices,
    logout_user,
)
from app.services.authentication.refresh import refresh_access_token
from app.services.authentication.register import register_user as register_user_service

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)

LoginForm = Annotated[OAuth2PasswordRequestForm, Depends()]


@router.post("/register", response_model=UserMe, status_code=status.HTTP_201_CREATED)
def register(user_create: UserCreate, db: DBSession) -> User:
    user = register_user_service(db, user_create)
    return user


@router.post("/login", response_model=TokenResponse)
def login(form_data: LoginForm, db: DBSession) -> TokenResponse:
    tokens = login_user(db, form_data.username, form_data.password)
    return tokens


@router.post("/refresh", response_model=TokenResponse)
def refresh_token(refresh_request: RefreshTokenRequest, db: DBSession) -> TokenResponse:
    new_tokens = refresh_access_token(db, refresh_request.refresh_token)
    return new_tokens


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(refresh_request: RefreshTokenRequest, db: DBSession) -> None:
    logout_user(db, refresh_request.refresh_token)


@router.post("/logout-all", status_code=status.HTTP_204_NO_CONTENT)
def logout_all(current_user: CurrentUser, db: DBSession) -> None:
    logout_all_devices(db, current_user.id)


@router.get("/me", response_model=UserMe)
def get_me(current_user: CurrentUser) -> User:
    return current_user
