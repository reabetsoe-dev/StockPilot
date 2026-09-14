from fastapi import APIRouter, Depends, Query
from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.procurement import PurchaseOrder, PurchaseRequest
from app.models.product import Product
from app.models.supplier import Supplier
from app.models.user import User
from app.models.warehouse import Warehouse
from app.schemas.search import SearchResult

router = APIRouter(prefix="/search", tags=["Search"])


@router.get("", response_model=list[SearchResult])
def search(
    q: str = Query(min_length=2, max_length=80),
    _: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[SearchResult]:
    needle = f"%{q.strip()}%"
    results: list[SearchResult] = []

    products = db.scalars(
        select(Product)
        .where(or_(Product.name.ilike(needle), Product.sku.ilike(needle), Product.barcode.ilike(needle)))
        .order_by(Product.name)
        .limit(6)
    ).all()
    results.extend(
        SearchResult(
            type="Product",
            label=f"{product.sku} - {product.name}",
            description="Inventory item",
            url=f"/inventory/{product.id}",
        )
        for product in products
    )

    suppliers = db.scalars(
        select(Supplier)
        .where(or_(Supplier.name.ilike(needle), Supplier.supplier_code.ilike(needle), Supplier.contact_person.ilike(needle)))
        .order_by(Supplier.name)
        .limit(4)
    ).all()
    results.extend(
        SearchResult(
            type="Supplier",
            label=f"{supplier.supplier_code} - {supplier.name}",
            description=supplier.contact_person,
            url="/suppliers",
        )
        for supplier in suppliers
    )

    warehouses = db.scalars(
        select(Warehouse)
        .where(or_(Warehouse.name.ilike(needle), Warehouse.code.ilike(needle), Warehouse.location.ilike(needle)))
        .order_by(Warehouse.name)
        .limit(3)
    ).all()
    results.extend(
        SearchResult(
            type="Warehouse",
            label=f"{warehouse.code} - {warehouse.name}",
            description=warehouse.location,
            url="/warehouses",
        )
        for warehouse in warehouses
    )

    purchase_requests = db.scalars(
        select(PurchaseRequest)
        .where(or_(PurchaseRequest.reference_number.ilike(needle), PurchaseRequest.purpose.ilike(needle)))
        .order_by(PurchaseRequest.created_at.desc())
        .limit(4)
    ).all()
    results.extend(
        SearchResult(
            type="Purchase Request",
            label=request.reference_number,
            description=request.purpose,
            url="/purchase-requests",
        )
        for request in purchase_requests
    )

    purchase_orders = db.scalars(
        select(PurchaseOrder)
        .where(or_(PurchaseOrder.po_number.ilike(needle), PurchaseOrder.notes.ilike(needle)))
        .order_by(PurchaseOrder.created_at.desc())
        .limit(4)
    ).all()
    results.extend(
        SearchResult(
            type="Purchase Order",
            label=order.po_number,
            description=f"{order.status.value} order",
            url="/purchase-orders",
        )
        for order in purchase_orders
    )

    return results[:20]
