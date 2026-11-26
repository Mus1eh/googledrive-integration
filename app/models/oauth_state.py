from datetime import UTC, datetime
from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, DateTime, Enum, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.core.enums import OAuthPurpose

if TYPE_CHECKING:
    from app.models.user import User


class OAuthState(Base):
    __tablename__ = "oauth_states"
    __table_args__ = (
        CheckConstraint(
            "(purpose = 'login' AND user_id IS NULL) OR "
            "(purpose = 'connect' AND user_id IS NOT NULL)",
            name="ck_oauth_state_purpose_user",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)

    user_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
        nullable=True,
    )

    state_hash: Mapped[str] = mapped_column(
        String(64),
        unique=True,
        nullable=False,
    )

    code_verifier: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    used_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        nullable=False,
    )

    purpose: Mapped[OAuthPurpose] = mapped_column(
        Enum(
            OAuthPurpose,
            name="oauth_purpose",
            values_callable=lambda enum: [member.value for member in enum],
        ),
        nullable=False,
    )

    user: Mapped["User | None"] = relationship(
        back_populates="oauth_states",
    )
