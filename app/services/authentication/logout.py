from datetime import UTC, datetime

from sqlalchemy import update
from sqlalchemy.orm import Session

from app.core.security import Token
from app.models.refresh_tokens import RefreshToken


def logout_user(db: Session, refresh_token: str) -> None:
    try:
        hashed_refresh_token = Token.hash_refresh_token(refresh_token)

        db.execute(
            update(RefreshToken)
            .where(
                RefreshToken.token_hash == hashed_refresh_token,
                RefreshToken.revoked_at.is_(None),
            )
            .values(revoked_at=datetime.now(UTC))
        )

        db.commit()

    except Exception:
        db.rollback()
        raise


def logout_all_devices(db: Session, user_id: int) -> None:
    try:
        db.execute(
            update(RefreshToken)
            .where(
                RefreshToken.user_id == user_id,
                RefreshToken.revoked_at.is_(None),
            )
            .values(revoked_at=datetime.now(UTC))
        )
        db.commit()

    except Exception:
        db.rollback()
        raise
