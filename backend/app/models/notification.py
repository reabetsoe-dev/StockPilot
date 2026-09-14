from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.core.database import Base
from app.models.base import TimestampMixin


class Notification(TimestampMixin, Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    title = Column(String(160), nullable=False)
    message = Column(Text, nullable=False)
    entity_type = Column(String(80), nullable=True, index=True)
    entity_id = Column(String(80), nullable=True)
    action_url = Column(String(255), nullable=True)
    read = Column(Boolean, default=False, nullable=False, index=True)

    user = relationship("User")
