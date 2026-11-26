from typing import Annotated

from fastapi import APIRouter, Cookie, Depends, Query, Response, status
from fastapi.security import OAuth2PasswordRequestForm

from app.core.config import settings
from app.core.enums import OAuthPurpose
from app.core.exceptions import (
    GoogleOAuthExchangeError,
    InvalidOAuthStateError,
)
from app.dependencies.authentication import CurrentUser, DBSession
from app.integrations.google.oauth import generate_authorization_url
from app.models.user import User
from app.schemas.auth import RefreshTokenRequest, TokenResponse
from app.schemas.google import GoogleLoginResponse
from app.schemas.user import UserCreate, UserMe
from app.services.authentication.google_login import login_with_google
from app.services.authentication.login import login_user
from app.services.authentication.logout import (
    logout_all_devices,
    logout_user,
)
from app.services.authentication.refresh import refresh_access_token
from app.services.authentication.register import register_user as register_user_service
from app.services.google_accounts.oauth_state import create_oauth_state

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


@router.get("/login/google", response_model=GoogleLoginResponse)
def google_login(db: DBSession, response: Response) -> GoogleLoginResponse:
    state, code_verifier = create_oauth_state(
        db=db,
        purpose=OAuthPurpose.LOGIN,
    )

    authorization_url = generate_authorization_url(
        state=state,
        code_verifier=code_verifier,
        purpose=OAuthPurpose.LOGIN,
    )

    response.set_cookie(
        key="oauth_state",
        value=state,
        httponly=True,
        secure=settings.COOKIE_SECURE,
        samesite="lax",
        max_age=settings.OAUTH_STATE_EXPIRE_MINUTES * 60,
        path="/auth/google/callback",
    )

    return GoogleLoginResponse(authorization_url=authorization_url)


@router.get("/google/callback", response_model=TokenResponse)
def google_login_callback(
    db: DBSession,
    response: Response,
    code: Annotated[str | None, Query()] = None,
    state: Annotated[str | None, Query()] = None,
    oauth_state: Annotated[str | None, Cookie()] = None,
    error: Annotated[str | None, Query()] = None,
) -> TokenResponse:

    if error:
        raise GoogleOAuthExchangeError()

    if not state or not oauth_state:
        raise InvalidOAuthStateError()

    if not code:
        raise GoogleOAuthExchangeError()

    tokens = login_with_google(
        db=db,
        code=code,
        state=state,
        browser_state=oauth_state,
    )

    response.delete_cookie(
        key="oauth_state",
        path="/auth/google/callback",
        secure=settings.COOKIE_SECURE,
        httponly=True,
        samesite="lax",
    )

    response.headers["Cache-Control"] = "no-store"
    response.headers["Pragma"] = "no-cache"

    return tokens
