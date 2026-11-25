import hashlib
import secrets
from datetime import UTC, datetime, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.encryption import Encryption
from app.core.exceptions import BadRequestError
from app.models.oauth_state import OAuthState


class InvalidOAuthStateError(BadRequestError):
    default_detail = "Invalid, expired, or already used OAuth state."


def create_oauth_state(db: Session, user_id: int) -> tuple[str, str]:

    state = secrets.token_urlsafe(32)
    code_verifier = secrets.token_urlsafe(64)

    state_hash = hashlib.sha256(state.encode()).hexdigest()

    encrypted_verifier = Encryption.encrypt(code_verifier)

    expires_at = datetime.now(UTC) + timedelta(
        minutes=settings.OAUTH_STATE_EXPIRE_MINUTES
    )

    oauth_state = OAuthState(
        user_id=user_id,
        state_hash=state_hash,
        code_verifier=encrypted_verifier,
        expires_at=expires_at,
    )

    try:
        db.add(oauth_state)
        db.commit()

    except Exception:
        db.rollback()
        raise

    return state, code_verifier


def consume_state(db: Session, state: str, browser_state: str) -> tuple[int, str]:

    if not state or not browser_state:
        raise InvalidOAuthStateError()

    if not secrets.compare_digest(state.encode(), browser_state.encode()):
        raise InvalidOAuthStateError()

    state_hash = hashlib.sha256(state.encode()).hexdigest()

    try:
        oauth_state = db.scalar(
            select(OAuthState)
            .where(OAuthState.state_hash == state_hash)
            .with_for_update()
        )

        now = datetime.now(UTC)

        if (
            oauth_state is None
            or oauth_state.used_at is not None
            or oauth_state.expires_at <= now
        ):
            raise InvalidOAuthStateError()

        user_id = oauth_state.user_id

        code_verifier = Encryption.decrypt(oauth_state.code_verifier)

        oauth_state.used_at = now

        db.commit()

    except Exception:
        db.rollback()
        raise

    return user_id, code_verifier
