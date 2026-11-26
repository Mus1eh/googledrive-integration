from fastapi import APIRouter, Response

from app.core.config import settings
from app.core.enums import OAuthPurpose
from app.dependencies.authentication import CurrentUser, DBSession
from app.integrations.google.oauth import generate_authorization_url
from app.schemas.google import GoogleConnectResponse
from app.services.google_accounts.oauth_state import create_oauth_state

router = APIRouter(prefix="/google", tags=["Google OAuth"])


@router.post("/connect", response_model=GoogleConnectResponse)
def connect_google(
    current_user: CurrentUser,
    db: DBSession,
    response: Response,
) -> GoogleConnectResponse:

    state, code_verifier = create_oauth_state(
        db=db, purpose=OAuthPurpose.CONNECT, user_id=current_user.id
    )

    authorization_url = generate_authorization_url(
        state, code_verifier, purpose=OAuthPurpose.CONNECT
    )

    response.set_cookie(
        key="oauth_state",
        value=state,
        httponly=True,
        secure=settings.COOKIE_SECURE,
        samesite="lax",
        max_age=settings.OAUTH_STATE_EXPIRE_MINUTES * 60,
        path="/google/callback",
    )

    return GoogleConnectResponse(authorization_url=authorization_url)
