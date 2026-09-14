from sqlalchemy import Boolean, Column, Integer, String, Text
from sqlalchemy.orm import relationship

from app.core.database import Base
from app.models.base import TimestampMixin


class Warehouse(TimestampMixin, Base):
    __tablename__ = "warehouses"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(40), unique=True, index=True, nullable=False)
    name = Column(String(160), nullable=False, index=True)
    location = Column(String(180), nullable=False)
    description = Column(Text, nullable=True)
    active = Column(Boolean, default=True, nullable=False)

    inventory_balances = relationship("InventoryBalance", back_populates="warehouse")
    stock_movements = relationship("StockMovement", back_populates="warehouse")
