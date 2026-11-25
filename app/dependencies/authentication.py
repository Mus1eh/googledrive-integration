from typing import Annotated

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.exceptions import InvalidCredentialsError
from app.core.security import Token
from app.models.user import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

AcessToken = Annotated[str, Depends(oauth2_scheme)]
DBSession = Annotated[Session, Depends(get_db)]


def get_current_user(
    token: AcessToken,
    db: DBSession,
) -> User:
    try:
        decoded_token = Token.decode_access_token(token)
        user_id = int(decoded_token["sub"])

    except (ValueError, TypeError, KeyError) as exc:
        raise InvalidCredentialsError() from exc

    user = db.get(User, user_id)

    if user is None:
        raise InvalidCredentialsError()

    return user


CurrentUser = Annotated[User, Depends(get_current_user)]
