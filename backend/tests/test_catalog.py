def auth_headers(client, email):
    response = client.post(
        "/api/auth/login",
        json={"email": email, "password": "Demo123!"},
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_seeded_catalog_records_are_available(client):
    headers = auth_headers(client, "inventory@stockpilot.local")

    categories = client.get("/api/categories", headers=headers)
    suppliers = client.get("/api/suppliers", headers=headers)
    warehouses = client.get("/api/warehouses", headers=headers)
    products = client.get("/api/products", headers=headers)

    assert categories.status_code == 200
    assert suppliers.status_code == 200
    assert warehouses.status_code == 200
    assert products.status_code == 200
    assert len(categories.json()) == 8
    assert len(suppliers.json()) == 12
    assert len(warehouses.json()) == 3
    assert len(products.json()) == 50


def test_inventory_manager_can_create_product(client):
    headers = auth_headers(client, "inventory@stockpilot.local")
    category_id = client.get("/api/categories", headers=headers).json()[0]["id"]
    supplier_id = client.get("/api/suppliers", headers=headers).json()[0]["id"]

    response = client.post(
        "/api/products",
        headers=headers,
        json={
            "sku": "lap-demo-999",
            "barcode": "999000999000",
            "name": "Demo Rugged Laptop",
            "description": "Rugged laptop for warehouse supervisors.",
            "category_id": category_id,
            "unit_of_measure": "Each",
            "cost_price": "11800.00",
            "selling_price": "14999.00",
            "reorder_level": 4,
            "preferred_supplier_id": supplier_id,
            "active": True,
        },
    )

    assert response.status_code == 201
    body = response.json()
    assert body["sku"] == "LAP-DEMO-999"
    assert body["category"]["id"] == category_id
    assert body["preferred_supplier"]["id"] == supplier_id


def test_duplicate_sku_is_rejected(client):
    headers = auth_headers(client, "inventory@stockpilot.local")
    category_id = client.get("/api/categories", headers=headers).json()[0]["id"]

    response = client.post(
        "/api/products",
        headers=headers,
        json={
            "sku": "LAP-HP-840",
            "barcode": "999000999001",
            "name": "Duplicate SKU Laptop",
            "description": "Should not be accepted.",
            "category_id": category_id,
            "unit_of_measure": "Each",
            "cost_price": "1000.00",
            "selling_price": "1200.00",
            "reorder_level": 2,
            "preferred_supplier_id": None,
            "active": True,
        },
    )

    assert response.status_code == 409
    assert response.json()["detail"] == "SKU already exists."


def test_auditor_cannot_create_product(client):
    headers = auth_headers(client, "auditor@stockpilot.local")
    category_id = client.get("/api/categories", headers=headers).json()[0]["id"]

    response = client.post(
        "/api/products",
        headers=headers,
        json={
            "sku": "AUDIT-LOCKED",
            "barcode": "999000999002",
            "name": "Auditor Created Product",
            "description": "Auditors must remain read-only.",
            "category_id": category_id,
            "unit_of_measure": "Each",
            "cost_price": "1000.00",
            "selling_price": "1200.00",
            "reorder_level": 2,
            "preferred_supplier_id": None,
            "active": True,
        },
    )

    assert response.status_code == 403


def test_procurement_officer_can_create_supplier(client):
    response = client.post(
        "/api/suppliers",
        headers=auth_headers(client, "procurement@stockpilot.local"),
        json={
            "supplier_code": "sup-9000",
            "name": "Portfolio Demo Supplier",
            "contact_person": "Grace Moloi",
            "email": "grace@portfoliodemo.example",
            "phone": "+266 5900 9000",
            "address": "Demo Supplier Park, Maseru",
            "tax_reference": "TAX-SUP-9000",
            "payment_terms": "Net 30",
            "active": True,
        },
    )

    assert response.status_code == 201
    assert response.json()["supplier_code"] == "SUP-9000"


def test_warehouse_code_uniqueness_is_enforced(client):
    response = client.post(
        "/api/warehouses",
        headers=auth_headers(client, "admin@stockpilot.local"),
        json={
            "code": "CENTRAL",
            "name": "Duplicate Central Warehouse",
            "location": "Maseru",
            "description": "Should be rejected.",
            "active": True,
        },
    )

    assert response.status_code == 409
    assert response.json()["detail"] == "Warehouse code already exists."
