from psycopg.errors import UniqueViolation
from sqlalchemy import exists, or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.exceptions import UserAlreadyExistsError
from app.core.security import Hash
from app.models.user import User
from app.schemas.user import UserCreate


def register_user(db: Session, data: UserCreate) -> User:
    user_exists = db.scalar(
        select(
            exists().where(
                or_(
                    User.username == data.username,
                    User.email == data.email,
                )
            )
        )
    )

    if user_exists:
        raise UserAlreadyExistsError()

    hashed_password = Hash.crypt_password(data.password)

    new_user = User(
        username=data.username,
        email=data.email,
        password_hash=hashed_password,
    )

    try:
        db.add(new_user)
        db.commit()

    except IntegrityError as exc:
        db.rollback()

        if isinstance(exc.orig, UniqueViolation):
            raise UserAlreadyExistsError() from exc

        raise

    db.refresh(new_user)
    return new_user
