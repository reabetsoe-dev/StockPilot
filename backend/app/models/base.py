from datetime import UTC, datetime

from sqlalchemy import Column, DateTime, func


def utc_now() -> datetime:
    return datetime.now(UTC)


class TimestampMixin:
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=utc_now,
        nullable=False,
    )
