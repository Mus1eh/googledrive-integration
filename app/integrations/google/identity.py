from google.auth.exceptions import GoogleAuthError
from google.auth.transport.requests import Request
from google.oauth2 import id_token
from google.oauth2.credentials import Credentials
from pydantic import ValidationError

from app.core.config import settings
from app.core.exceptions import InvalidGoogleIdentityError
from app.schemas.google import GoogleUserInfo


def verify_google_identity(
    credentials: Credentials,
) -> GoogleUserInfo:

    if not credentials.id_token:
        raise InvalidGoogleIdentityError()

    try:
        claims = id_token.verify_oauth2_token(
            credentials.id_token,
            Request(),
            settings.GOOGLE_CLIENT_ID,
        )

        if (
            not claims.get("sub")
            or not claims.get("email")
            or claims.get("email_verified") is not True
        ):
            raise InvalidGoogleIdentityError()

        return GoogleUserInfo(
            google_user_id=claims["sub"],
            email=claims["email"],
            email_verified=claims["email_verified"],
        )

    except (ValueError, GoogleAuthError, ValidationError) as exc:
        raise InvalidGoogleIdentityError() from exc
