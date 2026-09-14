from typing import Any

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.category import Category
from app.models.product import Product
from app.models.supplier import Supplier
from app.models.user import User
from app.models.warehouse import Warehouse
from app.schemas.category import CategoryCreate, CategoryUpdate
from app.schemas.product import ProductCreate, ProductUpdate
from app.schemas.supplier import SupplierCreate, SupplierUpdate
from app.schemas.warehouse import WarehouseCreate, WarehouseUpdate
from app.services.audit_service import record_audit_log


def clean_code(value: str) -> str:
    return value.strip().upper()


def clean_text(value: str | None) -> str | None:
    if value is None:
        return None
    stripped = value.strip()
    return stripped or None


def ensure_unique(
    db: Session,
    model: type,
    column: Any,
    value: str | None,
    detail: str,
    current_id: int | None = None,
) -> None:
    if value is None:
        return
    stmt = select(model).where(column == value)
    if current_id is not None:
        stmt = stmt.where(model.id != current_id)
    if db.scalar(stmt) is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=detail)


def get_category(db: Session, category_id: int) -> Category:
    category = db.get(Category, category_id)
    if category is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found.")
    return category


def get_supplier(db: Session, supplier_id: int | None) -> Supplier | None:
    if supplier_id is None:
        return None
    supplier = db.get(Supplier, supplier_id)
    if supplier is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Supplier not found.")
    return supplier


def create_category(db: Session, payload: CategoryCreate, actor: User) -> Category:
    name = payload.name.strip()
    ensure_unique(db, Category, Category.name, name, "Category already exists.")
    category = Category(name=name, description=clean_text(payload.description), active=payload.active)
    db.add(category)
    db.flush()
    record_audit_log(db, actor, "CATEGORY_CREATED", "Category", category.id, f"{actor.full_name} created category {category.name}.")
    db.commit()
    db.refresh(category)
    return category


def update_category(db: Session, category: Category, payload: CategoryUpdate, actor: User) -> Category:
    data = payload.model_dump(exclude_unset=True)
    if "name" in data and data["name"] is not None:
        name = data["name"].strip()
        ensure_unique(db, Category, Category.name, name, "Category already exists.", category.id)
        category.name = name
    if "description" in data:
        category.description = clean_text(data["description"])
    if "active" in data and data["active"] is not None:
        category.active = data["active"]
    record_audit_log(db, actor, "CATEGORY_UPDATED", "Category", category.id, f"{actor.full_name} updated category {category.name}.")
    db.commit()
    db.refresh(category)
    return category


def create_supplier(db: Session, payload: SupplierCreate, actor: User) -> Supplier:
    supplier_code = clean_code(payload.supplier_code)
    ensure_unique(db, Supplier, Supplier.supplier_code, supplier_code, "Supplier code already exists.")
    supplier = Supplier(
        supplier_code=supplier_code,
        name=payload.name.strip(),
        contact_person=payload.contact_person.strip(),
        email=clean_text(payload.email),
        phone=clean_text(payload.phone),
        address=clean_text(payload.address),
        tax_reference=clean_text(payload.tax_reference),
        payment_terms=clean_text(payload.payment_terms),
        active=payload.active,
    )
    db.add(supplier)
    db.flush()
    record_audit_log(db, actor, "SUPPLIER_CREATED", "Supplier", supplier.id, f"{actor.full_name} created supplier {supplier.name}.")
    db.commit()
    db.refresh(supplier)
    return supplier


def update_supplier(db: Session, supplier: Supplier, payload: SupplierUpdate, actor: User) -> Supplier:
    data = payload.model_dump(exclude_unset=True)
    if "supplier_code" in data and data["supplier_code"] is not None:
        supplier_code = clean_code(data["supplier_code"])
        ensure_unique(db, Supplier, Supplier.supplier_code, supplier_code, "Supplier code already exists.", supplier.id)
        supplier.supplier_code = supplier_code
    for field in ["name", "contact_person", "email", "phone", "address", "tax_reference", "payment_terms"]:
        if field in data:
            value = clean_text(data[field])
            if field in {"name", "contact_person"} and value is None:
                continue
            setattr(supplier, field, value)
    if "active" in data and data["active"] is not None:
        supplier.active = data["active"]
    record_audit_log(db, actor, "SUPPLIER_UPDATED", "Supplier", supplier.id, f"{actor.full_name} updated supplier {supplier.name}.")
    db.commit()
    db.refresh(supplier)
    return supplier


def create_warehouse(db: Session, payload: WarehouseCreate, actor: User) -> Warehouse:
    code = clean_code(payload.code)
    ensure_unique(db, Warehouse, Warehouse.code, code, "Warehouse code already exists.")
    warehouse = Warehouse(
        code=code,
        name=payload.name.strip(),
        location=payload.location.strip(),
        description=clean_text(payload.description),
        active=payload.active,
    )
    db.add(warehouse)
    db.flush()
    record_audit_log(db, actor, "WAREHOUSE_CREATED", "Warehouse", warehouse.id, f"{actor.full_name} created warehouse {warehouse.name}.")
    db.commit()
    db.refresh(warehouse)
    return warehouse


def update_warehouse(db: Session, warehouse: Warehouse, payload: WarehouseUpdate, actor: User) -> Warehouse:
    data = payload.model_dump(exclude_unset=True)
    if "code" in data and data["code"] is not None:
        code = clean_code(data["code"])
        ensure_unique(db, Warehouse, Warehouse.code, code, "Warehouse code already exists.", warehouse.id)
        warehouse.code = code
    for field in ["name", "location", "description"]:
        if field in data:
            value = clean_text(data[field])
            if field in {"name", "location"} and value is None:
                continue
            setattr(warehouse, field, value)
    if "active" in data and data["active"] is not None:
        warehouse.active = data["active"]
    record_audit_log(db, actor, "WAREHOUSE_UPDATED", "Warehouse", warehouse.id, f"{actor.full_name} updated warehouse {warehouse.name}.")
    db.commit()
    db.refresh(warehouse)
    return warehouse


def create_product(db: Session, payload: ProductCreate, actor: User) -> Product:
    sku = clean_code(payload.sku)
    barcode = clean_text(payload.barcode)
    ensure_unique(db, Product, Product.sku, sku, "SKU already exists.")
    ensure_unique(db, Product, Product.barcode, barcode, "Barcode already exists.")
    get_category(db, payload.category_id)
    get_supplier(db, payload.preferred_supplier_id)
    product = Product(
        sku=sku,
        barcode=barcode,
        name=payload.name.strip(),
        description=clean_text(payload.description),
        category_id=payload.category_id,
        unit_of_measure=payload.unit_of_measure.strip(),
        cost_price=payload.cost_price,
        selling_price=payload.selling_price,
        reorder_level=payload.reorder_level,
        preferred_supplier_id=payload.preferred_supplier_id,
        active=payload.active,
    )
    db.add(product)
    db.flush()
    record_audit_log(db, actor, "PRODUCT_CREATED", "Product", product.id, f"{actor.full_name} created product {product.sku}.")
    db.commit()
    db.refresh(product)
    return product


def update_product(db: Session, product: Product, payload: ProductUpdate, actor: User) -> Product:
    data = payload.model_dump(exclude_unset=True)
    if "sku" in data and data["sku"] is not None:
        sku = clean_code(data["sku"])
        ensure_unique(db, Product, Product.sku, sku, "SKU already exists.", product.id)
        product.sku = sku
    if "barcode" in data:
        barcode = clean_text(data["barcode"])
        ensure_unique(db, Product, Product.barcode, barcode, "Barcode already exists.", product.id)
        product.barcode = barcode
    if "category_id" in data and data["category_id"] is not None:
        get_category(db, data["category_id"])
        product.category_id = data["category_id"]
    if "preferred_supplier_id" in data:
        get_supplier(db, data["preferred_supplier_id"])
        product.preferred_supplier_id = data["preferred_supplier_id"]
    for field in ["name", "description", "unit_of_measure", "cost_price", "selling_price", "reorder_level", "active"]:
        if field in data:
            value = data[field]
            if field in {"name", "unit_of_measure"}:
                value = clean_text(value)
                if value is None:
                    continue
            elif field == "description":
                value = clean_text(value)
            if field == "active" and value is None:
                continue
            setattr(product, field, value)
    record_audit_log(db, actor, "PRODUCT_UPDATED", "Product", product.id, f"{actor.full_name} updated product {product.sku}.")
    db.commit()
    db.refresh(product)
    return product
