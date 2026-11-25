from datetime import UTC, datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
    BigInteger,
    Boolean,
    DateTime,
    ForeignKey,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.google_account import GoogleAccount


class DriveFile(Base):
    __tablename__ = "drive_files"

    __table_args__ = (
        UniqueConstraint(
            "google_account_id",
            "google_file_id",
            name="uq_google_account_file",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    google_account_id: Mapped[int] = mapped_column(
        ForeignKey("google_accounts.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    google_file_id: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    mime_type: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    size: Mapped[int | None] = mapped_column(
        BigInteger,
        nullable=True,
    )

    created_time: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    modified_time: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    parent_id: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
        index=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        nullable=False,
    )

    google_account: Mapped["GoogleAccount"] = relationship(
        back_populates="drive_files",
    )

    trashed: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    last_synced_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
