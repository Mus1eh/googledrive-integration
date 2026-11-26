from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from oauthlib.oauth2 import OAuth2Error
from requests.exceptions import RequestException

from app.core.config import settings
from app.core.enums import OAuthPurpose
from app.core.exceptions import GoogleOAuthExchangeError

GOOGLE_LOGIN_SCOPES = [
    "openid",
    "https://www.googleapis.com/auth/userinfo.email",
]

GOOGLE_DRIVE_SCOPES = [
    *GOOGLE_LOGIN_SCOPES,
    "https://www.googleapis.com/auth/drive",
]

GOOGLE_CLIENT_CONFIG = {
    "web": {
        "client_id": settings.GOOGLE_CLIENT_ID,
        "client_secret": settings.GOOGLE_CLIENT_SECRET,
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "redirect_uris": [
            settings.GOOGLE_LOGIN_REDIRECT_URI,
            settings.GOOGLE_CONNECT_REDIRECT_URI,
        ],
    }
}


def create_oauth_flow(state: str, code_verifier: str, purpose: OAuthPurpose) -> Flow:

    if purpose == OAuthPurpose.LOGIN:
        scopes = GOOGLE_LOGIN_SCOPES
        redirect_uri = settings.GOOGLE_LOGIN_REDIRECT_URI
    elif purpose == OAuthPurpose.CONNECT:
        scopes = GOOGLE_DRIVE_SCOPES
        redirect_uri = settings.GOOGLE_CONNECT_REDIRECT_URI
    else:
        raise ValueError(f"Invalid OAuth purpose: {purpose}")

    return Flow.from_client_config(
        client_config=GOOGLE_CLIENT_CONFIG,
        scopes=scopes,
        redirect_uri=redirect_uri,
        state=state,
        code_verifier=code_verifier,
        autogenerate_code_verifier=False,
    )


def generate_authorization_url(
    state: str, code_verifier: str, purpose: OAuthPurpose
) -> str:
    flow = create_oauth_flow(state=state, code_verifier=code_verifier, purpose=purpose)

    if purpose == OAuthPurpose.LOGIN:
        authorization_url, _ = flow.authorization_url(
            access_type="online",
            prompt="select_account",
        )
    else:
        authorization_url, _ = flow.authorization_url(
            access_type="offline",
            prompt="consent select_account",
            include_granted_scopes="true",
        )

    return authorization_url


def exchange_authorization_code(
    code: str,
    state: str,
    code_verifier: str,
    purpose: OAuthPurpose,
) -> Credentials:

    flow = create_oauth_flow(
        state=state,
        code_verifier=code_verifier,
        purpose=purpose,
    )

    try:
        flow.fetch_token(code=code, timeout=15)
    except (OAuth2Error, RequestException, Warning) as exc:
        raise GoogleOAuthExchangeError() from exc

    return flow.credentials
