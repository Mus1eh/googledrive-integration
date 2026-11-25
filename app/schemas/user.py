import re
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

from app.core.limits import (
    MAX_EMAIL_LENGTH,
    MAX_PASSWORD_LENGTH,
    MAX_USERNAME_LENGTH,
    MIN_PASSWORD_LENGTH,
    MIN_USERNAME_LENGTH,
)


class UserCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    username: str = Field(
        min_length=MIN_USERNAME_LENGTH, max_length=MAX_USERNAME_LENGTH
    )
    email: EmailStr = Field(max_length=MAX_EMAIL_LENGTH)
    password: str = Field(
        min_length=MIN_PASSWORD_LENGTH, max_length=MAX_PASSWORD_LENGTH
    )

    @field_validator("username", mode="before")
    @classmethod
    def validate_username(cls, v: Any) -> Any:
        if isinstance(v, str):
            v = v.strip()

            if not re.fullmatch(r"[a-zA-Z0-9_]+", v):
                raise ValueError(
                    "Username can only contain letters, numbers, and underscores."
                )

        return v


class UserMe(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    email: EmailStr
    created_at: datetime
