from datetime import UTC, datetime, timedelta

from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import Token
from app.models.refresh_tokens import RefreshToken
from app.schemas.auth import TokenResponse


def issue_tokens(db: Session, user_id: int) -> TokenResponse:
    access_token = Token.create_access_token(
        user_id=user_id,
    )

    refresh_token = Token.generate_refresh_token()

    hashed_refresh_token = Token.hash_refresh_token(refresh_token)

    refresh_token_obj = RefreshToken(
        user_id=user_id,
        token_hash=hashed_refresh_token,
        expires_at=datetime.now(UTC)
        + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
    )
    db.add(refresh_token_obj)

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
    )
