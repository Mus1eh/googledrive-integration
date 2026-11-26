from datetime import UTC, datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.core.limits import MAX_EMAIL_LENGTH

if TYPE_CHECKING:
    from app.models.user import User


class GoogleIdentity(Base):
    __tablename__ = "google_identities"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    google_user_id: Mapped[str] = mapped_column(
        String(255), nullable=False, unique=True
    )

    google_email: Mapped[str] = mapped_column(String(MAX_EMAIL_LENGTH), nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False
    )

    user: Mapped["User"] = relationship(back_populates="google_identities")
