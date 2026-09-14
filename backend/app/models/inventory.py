import enum

from sqlalchemy import Column, DateTime, Enum, ForeignKey, Integer, String, Text, UniqueConstraint, func
from sqlalchemy.orm import relationship

from app.core.database import Base
from app.models.base import TimestampMixin


class StockMovementType(str, enum.Enum):
    OPENING_BALANCE = "OPENING_BALANCE"
    GOODS_RECEIPT = "GOODS_RECEIPT"
    STOCK_ISSUE = "STOCK_ISSUE"
    TRANSFER_OUT = "TRANSFER_OUT"
    TRANSFER_IN = "TRANSFER_IN"
    ADJUSTMENT_INCREASE = "ADJUSTMENT_INCREASE"
    ADJUSTMENT_DECREASE = "ADJUSTMENT_DECREASE"
    RETURN = "RETURN"


class InventoryBalance(TimestampMixin, Base):
    __tablename__ = "inventory_balances"
    __table_args__ = (
        UniqueConstraint("warehouse_id", "product_id", name="uq_inventory_balances_warehouse_product"),
    )

    id = Column(Integer, primary_key=True, index=True)
    warehouse_id = Column(Integer, ForeignKey("warehouses.id"), nullable=False, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False, index=True)
    quantity_on_hand = Column(Integer, nullable=False, default=0)
    quantity_reserved = Column(Integer, nullable=False, default=0)

    product = relationship("Product", back_populates="inventory_balances")
    warehouse = relationship("Warehouse", back_populates="inventory_balances")


class StockMovement(Base):
    __tablename__ = "stock_movements"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False, index=True)
    warehouse_id = Column(Integer, ForeignKey("warehouses.id"), nullable=False, index=True)
    movement_type = Column(
        Enum(
            StockMovementType,
            values_callable=lambda movements: [movement.value for movement in movements],
            native_enum=False,
        ),
        nullable=False,
        index=True,
    )
    quantity = Column(Integer, nullable=False)
    reference_type = Column(String(80), nullable=True)
    reference_id = Column(String(80), nullable=True)
    reason = Column(Text, nullable=False)
    performed_by = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    product = relationship("Product", back_populates="stock_movements")
    warehouse = relationship("Warehouse", back_populates="stock_movements")
    performed_by_user = relationship("User")
