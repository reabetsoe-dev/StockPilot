from sqlalchemy import Boolean, Column, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.orm import relationship

from app.core.database import Base
from app.models.base import TimestampMixin


class Product(TimestampMixin, Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    sku = Column(String(80), unique=True, index=True, nullable=False)
    barcode = Column(String(80), unique=True, index=True, nullable=True)
    name = Column(String(180), nullable=False, index=True)
    description = Column(Text, nullable=True)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False, index=True)
    unit_of_measure = Column(String(40), nullable=False, default="Each")
    cost_price = Column(Numeric(12, 2), nullable=False, default=0)
    selling_price = Column(Numeric(12, 2), nullable=False, default=0)
    reorder_level = Column(Integer, nullable=False, default=0)
    preferred_supplier_id = Column(Integer, ForeignKey("suppliers.id"), nullable=True, index=True)
    active = Column(Boolean, default=True, nullable=False)

    category = relationship("Category", back_populates="products")
    preferred_supplier = relationship("Supplier", back_populates="products")
