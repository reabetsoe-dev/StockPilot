from sqlalchemy import Boolean, Column, Integer, String, Text
from sqlalchemy.orm import relationship

from app.core.database import Base
from app.models.base import TimestampMixin


class Department(TimestampMixin, Base):
    __tablename__ = "departments"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(120), unique=True, index=True)
    description = Column(Text, nullable=True)
    active = Column(Boolean, default=True, nullable=False)

    users = relationship("User", back_populates="department")
