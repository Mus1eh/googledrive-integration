import hashlib
import secrets
from datetime import UTC, datetime, timedelta
from typing import Any

import jwt
from pwdlib import PasswordHash

from app.core.config import settings

pwhash = PasswordHash.recommended()


class Hash:
    @staticmethod
    def crypt_password(password: str) -> str:
        return pwhash.hash(password)

    @staticmethod
    def verify_password(
        password: str,
        hashed_password: str,
    ) -> bool:
        return pwhash.verify(password, hashed_password)


class Token:
    @staticmethod
    def create_access_token(
        user_id: int,
        expires_delta: timedelta | None = None,
    ) -> str:
        now = datetime.now(UTC)

        if expires_delta is None:
            expires_delta = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

        payload = {
            "sub": str(user_id),
            "iat": now,
            "exp": now + expires_delta,
            "type": "access",
        }

        return jwt.encode(
            payload,
            settings.JWT_SECRET_KEY,
            algorithm=settings.JWT_ALGORITHM,
        )

    @staticmethod
    def decode_access_token(token: str) -> dict[str, Any]:
        try:
            payload = jwt.decode(
                token,
                settings.JWT_SECRET_KEY,
                algorithms=[settings.JWT_ALGORITHM],
                options={"require": ["sub", "iat", "exp", "type"]},
            )

            if payload["type"] != "access":
                raise ValueError("Invalid token type")

            return payload

        except jwt.ExpiredSignatureError as exc:
            raise ValueError("Token has expired") from exc

        except jwt.InvalidTokenError as exc:
            raise ValueError("Invalid token") from exc

    @staticmethod
    def generate_refresh_token() -> str:
        return secrets.token_urlsafe(32)

    @staticmethod
    def hash_refresh_token(token: str) -> str:
        return hashlib.sha256(token.encode()).hexdigest()
