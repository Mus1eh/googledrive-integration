from datetime import UTC, datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.google_account import GoogleAccount
    from app.models.oauth_state import OAuthState
    from app.models.refresh_tokens import RefreshToken


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)

    email: Mapped[str] = mapped_column(
        String(100), unique=True, nullable=False, index=True
    )

    password_hash: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False
    )

    google_accounts: Mapped[list["GoogleAccount"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )

    refresh_tokens: Mapped[list["RefreshToken"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    oauth_states: Mapped[list["OAuthState"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )
