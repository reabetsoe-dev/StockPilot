import enum

from sqlalchemy import Column, DateTime, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.core.database import Base
from app.models.base import TimestampMixin


class StockRequestStatus(str, enum.Enum):
    SUBMITTED = "SUBMITTED"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    ISSUED = "ISSUED"
    CANCELLED = "CANCELLED"


class StockTransferStatus(str, enum.Enum):
    DRAFT = "DRAFT"
    IN_TRANSIT = "IN_TRANSIT"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"


class StockAdjustmentType(str, enum.Enum):
    INCREASE = "INCREASE"
    DECREASE = "DECREASE"


def enum_column(enum_type: type[enum.Enum], **kwargs):
    return Column(
        Enum(
            enum_type,
            values_callable=lambda values: [value.value for value in values],
            native_enum=False,
        ),
        **kwargs,
    )


class StockRequest(TimestampMixin, Base):
    __tablename__ = "stock_requests"

    id = Column(Integer, primary_key=True, index=True)
    reference_number = Column(String(40), unique=True, index=True, nullable=False)
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=False, index=True)
    requested_by = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    source_warehouse_id = Column(Integer, ForeignKey("warehouses.id"), nullable=False, index=True)
    purpose = Column(Text, nullable=False)
    status = enum_column(StockRequestStatus, nullable=False, default=StockRequestStatus.SUBMITTED, index=True)
    issued_by = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    issued_at = Column(DateTime(timezone=True), nullable=True)

    department = relationship("Department")
    requested_by_user = relationship("User", foreign_keys=[requested_by])
    source_warehouse = relationship("Warehouse")
    issued_by_user = relationship("User", foreign_keys=[issued_by])
    items = relationship("StockRequestItem", back_populates="stock_request", cascade="all, delete-orphan")


class StockRequestItem(Base):
    __tablename__ = "stock_request_items"

    id = Column(Integer, primary_key=True, index=True)
    stock_request_id = Column(Integer, ForeignKey("stock_requests.id"), nullable=False, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False, index=True)
    quantity_requested = Column(Integer, nullable=False)
    quantity_issued = Column(Integer, nullable=False, default=0)

    stock_request = relationship("StockRequest", back_populates="items")
    product = relationship("Product")


class StockTransfer(TimestampMixin, Base):
    __tablename__ = "stock_transfers"

    id = Column(Integer, primary_key=True, index=True)
    transfer_number = Column(String(40), unique=True, index=True, nullable=False)
    source_warehouse_id = Column(Integer, ForeignKey("warehouses.id"), nullable=False, index=True)
    destination_warehouse_id = Column(Integer, ForeignKey("warehouses.id"), nullable=False, index=True)
    status = enum_column(StockTransferStatus, nullable=False, default=StockTransferStatus.DRAFT, index=True)
    requested_by = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    completed_by = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)

    source_warehouse = relationship("Warehouse", foreign_keys=[source_warehouse_id])
    destination_warehouse = relationship("Warehouse", foreign_keys=[destination_warehouse_id])
    requested_by_user = relationship("User", foreign_keys=[requested_by])
    completed_by_user = relationship("User", foreign_keys=[completed_by])
    items = relationship("StockTransferItem", back_populates="stock_transfer", cascade="all, delete-orphan")


class StockTransferItem(Base):
    __tablename__ = "stock_transfer_items"

    id = Column(Integer, primary_key=True, index=True)
    stock_transfer_id = Column(Integer, ForeignKey("stock_transfers.id"), nullable=False, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False, index=True)
    quantity = Column(Integer, nullable=False)

    stock_transfer = relationship("StockTransfer", back_populates="items")
    product = relationship("Product")


class StockAdjustment(TimestampMixin, Base):
    __tablename__ = "stock_adjustments"

    id = Column(Integer, primary_key=True, index=True)
    adjustment_number = Column(String(40), unique=True, index=True, nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False, index=True)
    warehouse_id = Column(Integer, ForeignKey("warehouses.id"), nullable=False, index=True)
    adjustment_type = enum_column(StockAdjustmentType, nullable=False)
    quantity = Column(Integer, nullable=False)
    reason = Column(Text, nullable=False)
    notes = Column(Text, nullable=True)
    performed_by = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)

    product = relationship("Product")
    warehouse = relationship("Warehouse")
    performed_by_user = relationship("User")
