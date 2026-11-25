from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.core.exceptions import InvalidCredentialsError
from app.core.security import Hash
from app.models.user import User
from app.schemas.auth import TokenResponse
from app.services.authentication.tokens import issue_tokens


def login_user(db: Session, identifier: str, password: str) -> TokenResponse:
    user = db.scalar(
        select(User).where(
            or_(
                User.username == identifier,
                User.email == identifier,
            )
        )
    )

    if user is None or not Hash.verify_password(password, user.password_hash):
        raise InvalidCredentialsError()

    try:
        tokens = issue_tokens(db, user.id)
        db.commit()
    except Exception:
        db.rollback()
        raise

    return tokens
