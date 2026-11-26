from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow

from app.core.config import settings

GOOGLE_SCOPES = [
    "openid",
    "https://www.googleapis.com/auth/userinfo.email",
    "https://www.googleapis.com/auth/drive",
]

GOOGLE_CLIENT_CONFIG = {
    "web": {
        "client_id": settings.GOOGLE_CLIENT_ID,
        "client_secret": settings.GOOGLE_CLIENT_SECRET,
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "redirect_uris": [settings.GOOGLE_REDIRECT_URI],
    }
}


def create_oauth_flow(state: str, code_verifier: str) -> Flow:
    return Flow.from_client_config(
        client_config=GOOGLE_CLIENT_CONFIG,
        scopes=GOOGLE_SCOPES,
        redirect_uri=settings.GOOGLE_REDIRECT_URI,
        state=state,
        code_verifier=code_verifier,
        autogenerate_code_verifier=False,
    )


def generate_authorization_url(state: str, code_verifier: str) -> str:
    flow = create_oauth_flow(state, code_verifier)

    authorization_url, _ = flow.authorization_url(
        access_type="offline",
        prompt="consent select_account",
        include_granted_scopes="true",
    )

    return authorization_url


def exchange_authorization_code(
    code: str, state: str, code_verifier: str
) -> Credentials:
    flow = create_oauth_flow(state, code_verifier)

    flow.fetch_token(code=code)

    return flow.credentials
