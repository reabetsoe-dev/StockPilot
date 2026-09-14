import enum

from sqlalchemy import Column, Date, Enum, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.orm import relationship

from app.core.database import Base
from app.models.base import TimestampMixin


class PurchaseRequestStatus(str, enum.Enum):
    DRAFT = "DRAFT"
    SUBMITTED = "SUBMITTED"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    CONVERTED_TO_PO = "CONVERTED_TO_PO"
    CANCELLED = "CANCELLED"


class PurchaseRequestPriority(str, enum.Enum):
    LOW = "LOW"
    NORMAL = "NORMAL"
    HIGH = "HIGH"
    URGENT = "URGENT"


class PurchaseOrderStatus(str, enum.Enum):
    DRAFT = "DRAFT"
    ISSUED = "ISSUED"
    PARTIALLY_RECEIVED = "PARTIALLY_RECEIVED"
    RECEIVED = "RECEIVED"
    CANCELLED = "CANCELLED"


def enum_column(enum_type: type[enum.Enum], **kwargs):
    return Column(
        Enum(
            enum_type,
            values_callable=lambda values: [value.value for value in values],
            native_enum=False,
        ),
        **kwargs,
    )


class PurchaseRequest(TimestampMixin, Base):
    __tablename__ = "purchase_requests"

    id = Column(Integer, primary_key=True, index=True)
    reference_number = Column(String(40), unique=True, index=True, nullable=False)
    requested_by = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=False, index=True)
    purpose = Column(Text, nullable=False)
    priority = enum_column(PurchaseRequestPriority, nullable=False, default=PurchaseRequestPriority.NORMAL)
    status = enum_column(PurchaseRequestStatus, nullable=False, default=PurchaseRequestStatus.DRAFT, index=True)

    requested_by_user = relationship("User")
    department = relationship("Department")
    items = relationship("PurchaseRequestItem", back_populates="purchase_request", cascade="all, delete-orphan")
    purchase_orders = relationship("PurchaseOrder", back_populates="purchase_request")


class PurchaseRequestItem(Base):
    __tablename__ = "purchase_request_items"

    id = Column(Integer, primary_key=True, index=True)
    purchase_request_id = Column(Integer, ForeignKey("purchase_requests.id"), nullable=False, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=True, index=True)
    description = Column(Text, nullable=False)
    quantity = Column(Integer, nullable=False)
    estimated_unit_price = Column(Numeric(12, 2), nullable=False, default=0)

    purchase_request = relationship("PurchaseRequest", back_populates="items")
    product = relationship("Product")


class PurchaseOrder(TimestampMixin, Base):
    __tablename__ = "purchase_orders"

    id = Column(Integer, primary_key=True, index=True)
    po_number = Column(String(40), unique=True, index=True, nullable=False)
    supplier_id = Column(Integer, ForeignKey("suppliers.id"), nullable=False, index=True)
    purchase_request_id = Column(Integer, ForeignKey("purchase_requests.id"), nullable=True, index=True)
    order_date = Column(Date, nullable=False)
    expected_delivery_date = Column(Date, nullable=True)
    status = enum_column(PurchaseOrderStatus, nullable=False, default=PurchaseOrderStatus.DRAFT, index=True)
    subtotal = Column(Numeric(12, 2), nullable=False, default=0)
    tax = Column(Numeric(12, 2), nullable=False, default=0)
    total = Column(Numeric(12, 2), nullable=False, default=0)
    notes = Column(Text, nullable=True)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)

    supplier = relationship("Supplier")
    purchase_request = relationship("PurchaseRequest", back_populates="purchase_orders")
    created_by_user = relationship("User")
    items = relationship("PurchaseOrderItem", back_populates="purchase_order", cascade="all, delete-orphan")
    goods_receipts = relationship("GoodsReceipt", back_populates="purchase_order")


class PurchaseOrderItem(Base):
    __tablename__ = "purchase_order_items"

    id = Column(Integer, primary_key=True, index=True)
    purchase_order_id = Column(Integer, ForeignKey("purchase_orders.id"), nullable=False, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False, index=True)
    description = Column(Text, nullable=False)
    quantity_ordered = Column(Integer, nullable=False)
    quantity_received = Column(Integer, nullable=False, default=0)
    unit_price = Column(Numeric(12, 2), nullable=False)
    line_total = Column(Numeric(12, 2), nullable=False)

    purchase_order = relationship("PurchaseOrder", back_populates="items")
    product = relationship("Product")
    receipt_items = relationship("GoodsReceiptItem", back_populates="purchase_order_item")


class GoodsReceipt(TimestampMixin, Base):
    __tablename__ = "goods_receipts"

    id = Column(Integer, primary_key=True, index=True)
    receipt_number = Column(String(40), unique=True, index=True, nullable=False)
    purchase_order_id = Column(Integer, ForeignKey("purchase_orders.id"), nullable=False, index=True)
    warehouse_id = Column(Integer, ForeignKey("warehouses.id"), nullable=False, index=True)
    received_by = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    received_date = Column(Date, nullable=False)
    notes = Column(Text, nullable=True)

    purchase_order = relationship("PurchaseOrder", back_populates="goods_receipts")
    warehouse = relationship("Warehouse")
    received_by_user = relationship("User")
    items = relationship("GoodsReceiptItem", back_populates="goods_receipt", cascade="all, delete-orphan")


class GoodsReceiptItem(Base):
    __tablename__ = "goods_receipt_items"

    id = Column(Integer, primary_key=True, index=True)
    goods_receipt_id = Column(Integer, ForeignKey("goods_receipts.id"), nullable=False, index=True)
    purchase_order_item_id = Column(Integer, ForeignKey("purchase_order_items.id"), nullable=False, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False, index=True)
    quantity_received = Column(Integer, nullable=False)
    quantity_rejected = Column(Integer, nullable=False, default=0)
    notes = Column(Text, nullable=True)

    goods_receipt = relationship("GoodsReceipt", back_populates="items")
    purchase_order_item = relationship("PurchaseOrderItem", back_populates="receipt_items")
    product = relationship("Product")
