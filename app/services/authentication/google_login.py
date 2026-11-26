import secrets

from psycopg.errors import UniqueViolation
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.enums import OAuthPurpose
from app.core.exceptions import ConflictError, GoogleAccountLinkRequiredError
from app.integrations.google.identity import verify_google_identity
from app.integrations.google.oauth import exchange_authorization_code
from app.models.google_identity import GoogleIdentity
from app.models.user import User
from app.schemas.auth import TokenResponse
from app.schemas.google import GoogleUserInfo
from app.services.authentication.tokens import issue_tokens
from app.services.google_accounts.oauth_state import consume_oauth_state


def find_or_create_google_user(
    db: Session,
    google_user: GoogleUserInfo,
) -> User:

    google_identity = db.scalar(
        select(GoogleIdentity).where(
            GoogleIdentity.google_user_id == google_user.google_user_id
        )
    )

    if google_identity is not None:
        return google_identity.user

    existing_user = db.scalar(select(User).where(User.email == google_user.email))

    if existing_user is not None:
        raise GoogleAccountLinkRequiredError()

    user = User(
        username=f"google_{secrets.token_hex(12)}",
        email=google_user.email,
        password_hash=None,
    )

    db.add(user)
    db.flush()

    google_identity = GoogleIdentity(
        user_id=user.id,
        google_user_id=google_user.google_user_id,
        google_email=google_user.email,
    )

    db.add(google_identity)
    db.flush()

    return user


def login_with_google(
    db: Session,
    code: str,
    state: str,
    browser_state: str,
) -> TokenResponse:

    _, code_verifier = consume_oauth_state(
        db=db,
        state=state,
        browser_state=browser_state,
        expected_purpose=OAuthPurpose.LOGIN,
    )

    credentials = exchange_authorization_code(
        code=code,
        state=state,
        code_verifier=code_verifier,
        purpose=OAuthPurpose.LOGIN,
    )

    google_user = verify_google_identity(credentials)

    try:
        user = find_or_create_google_user(
            db=db,
            google_user=google_user,
        )

        tokens = issue_tokens(
            db=db,
            user_id=user.id,
        )

        db.commit()

    except IntegrityError as exc:
        db.rollback()

        if isinstance(exc.orig, UniqueViolation):
            raise ConflictError(
                "Account creation conflict. Please try signing in again."
            ) from exc

        raise

    except Exception:
        db.rollback()
        raise

    return tokens
