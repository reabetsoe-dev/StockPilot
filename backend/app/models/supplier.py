from sqlalchemy import Boolean, Column, Integer, String, Text
from sqlalchemy.orm import relationship

from app.core.database import Base
from app.models.base import TimestampMixin


class Supplier(TimestampMixin, Base):
    __tablename__ = "suppliers"

    id = Column(Integer, primary_key=True, index=True)
    supplier_code = Column(String(40), unique=True, index=True, nullable=False)
    name = Column(String(180), nullable=False, index=True)
    contact_person = Column(String(140), nullable=False)
    email = Column(String(255), nullable=True)
    phone = Column(String(60), nullable=True)
    address = Column(Text, nullable=True)
    tax_reference = Column(String(80), nullable=True)
    payment_terms = Column(String(120), nullable=True)
    active = Column(Boolean, default=True, nullable=False)

    products = relationship("Product", back_populates="preferred_supplier")
