from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.exceptions import InvalidCredentialsError
from app.core.security import Token
from app.models.refresh_tokens import RefreshToken
from app.schemas.auth import TokenResponse
from app.services.authentication.tokens import issue_tokens


def refresh_access_token(db: Session, refresh_token: str) -> TokenResponse:

    try:
        hashed_refresh_token = Token.hash_refresh_token(refresh_token)

        refresh_token_obj = db.scalar(
            select(RefreshToken)
            .where(
                RefreshToken.token_hash == hashed_refresh_token,
            )
            .with_for_update()
        )

        now = datetime.now(UTC)
        if (
            refresh_token_obj is None
            or refresh_token_obj.expires_at <= now
            or refresh_token_obj.revoked_at is not None
        ):
            raise InvalidCredentialsError()

        refresh_token_obj.revoked_at = now

        user_id = refresh_token_obj.user_id
        new_tokens = issue_tokens(db, user_id)

        db.commit()

    except Exception:
        db.rollback()
        raise
    return new_tokens
