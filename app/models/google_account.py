from datetime import UTC, datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
    DateTime,
    ForeignKey,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.drive_file import DriveFile
    from app.models.user import User


class GoogleAccount(Base):
    __tablename__ = "google_accounts"

    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "google_user_id",
            name="uq_user_google_account",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    google_user_id: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    google_email: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    access_token: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    refresh_token: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    token_expiry: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        nullable=False,
    )

    user: Mapped["User"] = relationship(
        back_populates="google_accounts",
    )

    drive_files: Mapped[list["DriveFile"]] = relationship(
        back_populates="google_account",
        cascade="all, delete-orphan",
    )

    scopes: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
        nullable=False,
    )
