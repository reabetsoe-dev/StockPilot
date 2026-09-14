from decimal import Decimal


def auth_headers(client, email):
    response = client.post(
        "/api/auth/login",
        json={"email": email, "password": "Demo123!"},
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def lookup_seed_data(client, headers):
    categories = client.get("/api/categories", headers=headers).json()
    suppliers = client.get("/api/suppliers", headers=headers).json()
    warehouses = client.get("/api/warehouses", headers=headers).json()
    return {
        "category_id": categories[0]["id"],
        "supplier_id": suppliers[0]["id"],
        "central_id": next(warehouse["id"] for warehouse in warehouses if warehouse["code"] == "CENTRAL"),
        "north_id": next(warehouse["id"] for warehouse in warehouses if warehouse["code"] == "NORTH"),
    }


def create_product(client, headers, sku, category_id, supplier_id):
    response = client.post(
        "/api/products",
        headers=headers,
        json={
            "sku": sku,
            "barcode": f"BAR-{sku}",
            "name": f"{sku} Product",
            "description": "Integration test product.",
            "category_id": category_id,
            "unit_of_measure": "Each",
            "cost_price": "100.00",
            "selling_price": "140.00",
            "reorder_level": 5,
            "preferred_supplier_id": supplier_id,
            "active": True,
        },
    )
    assert response.status_code == 201
    return response.json()


def test_purchase_request_can_be_submitted_and_approved(client):
    requester_headers = auth_headers(client, "requester@stockpilot.local")
    inventory_headers = auth_headers(client, "inventory@stockpilot.local")
    seed = lookup_seed_data(client, inventory_headers)
    product_id = client.get("/api/products", headers=inventory_headers, params={"search": "USB Keyboard"}).json()[0]["id"]

    created = client.post(
        "/api/purchase-requests",
        headers=requester_headers,
        json={
            "purpose": "Need keyboards for new department workstations.",
            "priority": "HIGH",
            "items": [
                {
                    "product_id": product_id,
                    "description": "USB Keyboard",
                    "quantity": 5,
                    "estimated_unit_price": "210.00",
                }
            ],
        },
    )

    assert created.status_code == 201
    request_id = created.json()["id"]
    assert created.json()["status"] == "DRAFT"

    submitted = client.post(f"/api/purchase-requests/{request_id}/submit", headers=requester_headers)
    approved = client.post(f"/api/purchase-requests/{request_id}/approve", headers=inventory_headers)

    assert submitted.status_code == 200
    assert submitted.json()["status"] == "SUBMITTED"
    assert approved.status_code == 200
    assert approved.json()["status"] == "APPROVED"
    assert seed["category_id"]


def test_purchase_order_totals_are_calculated_on_backend(client):
    procurement_headers = auth_headers(client, "procurement@stockpilot.local")
    inventory_headers = auth_headers(client, "inventory@stockpilot.local")
    seed = lookup_seed_data(client, inventory_headers)
    product = create_product(client, inventory_headers, "PO-CALC-001", seed["category_id"], seed["supplier_id"])

    response = client.post(
        "/api/purchase-orders",
        headers=procurement_headers,
        json={
            "supplier_id": seed["supplier_id"],
            "items": [
                {
                    "product_id": product["id"],
                    "description": "Backend calculated line",
                    "quantity_ordered": 3,
                    "unit_price": "100.00",
                }
            ],
        },
    )

    assert response.status_code == 201
    body = response.json()
    assert Decimal(str(body["subtotal"])) == Decimal("300.00")
    assert Decimal(str(body["tax"])) == Decimal("45.00")
    assert Decimal(str(body["total"])) == Decimal("345.00")
    assert Decimal(str(body["items"][0]["line_total"])) == Decimal("300.00")


def test_goods_receipt_partial_and_complete_updates_inventory(client):
    inventory_headers = auth_headers(client, "inventory@stockpilot.local")
    procurement_headers = auth_headers(client, "procurement@stockpilot.local")
    warehouse_headers = auth_headers(client, "warehouse@stockpilot.local")
    seed = lookup_seed_data(client, inventory_headers)
    product = create_product(client, inventory_headers, "GRN-LAP-001", seed["category_id"], seed["supplier_id"])

    adjustment = client.post(
        "/api/stock-adjustments",
        headers=inventory_headers,
        json={
            "product_id": product["id"],
            "warehouse_id": seed["central_id"],
            "adjustment_type": "INCREASE",
            "quantity": 10,
            "reason": "Initial integration stock.",
        },
    )
    assert adjustment.status_code == 201

    order = client.post(
        "/api/purchase-orders",
        headers=procurement_headers,
        json={
            "supplier_id": seed["supplier_id"],
            "items": [
                {
                    "product_id": product["id"],
                    "description": product["name"],
                    "quantity_ordered": 20,
                    "unit_price": "100.00",
                }
            ],
        },
    ).json()
    issued = client.post(f"/api/purchase-orders/{order['id']}/issue", headers=procurement_headers).json()
    order_item_id = issued["items"][0]["id"]

    first_receipt = client.post(
        "/api/goods-receipts",
        headers=warehouse_headers,
        json={
            "purchase_order_id": order["id"],
            "warehouse_id": seed["central_id"],
            "items": [{"purchase_order_item_id": order_item_id, "quantity_received": 12}],
        },
    )
    assert first_receipt.status_code == 201
    partially_received = client.get(f"/api/purchase-orders/{order['id']}", headers=procurement_headers).json()
    detail_after_first = client.get(f"/api/inventory/{product['id']}", headers=inventory_headers).json()
    assert partially_received["status"] == "PARTIALLY_RECEIVED"
    assert partially_received["items"][0]["quantity_received"] == 12
    assert detail_after_first["total_on_hand"] == 22

    second_receipt = client.post(
        "/api/goods-receipts",
        headers=warehouse_headers,
        json={
            "purchase_order_id": order["id"],
            "warehouse_id": seed["central_id"],
            "items": [{"purchase_order_item_id": order_item_id, "quantity_received": 8}],
        },
    )
    assert second_receipt.status_code == 201
    received = client.get(f"/api/purchase-orders/{order['id']}", headers=procurement_headers).json()
    detail_after_second = client.get(f"/api/inventory/{product['id']}", headers=inventory_headers).json()
    assert received["status"] == "RECEIVED"
    assert received["items"][0]["quantity_received"] == 20
    assert detail_after_second["total_on_hand"] == 30


def test_negative_stock_issue_is_rejected_without_movement(client):
    inventory_headers = auth_headers(client, "inventory@stockpilot.local")
    requester_headers = auth_headers(client, "requester@stockpilot.local")
    warehouse_headers = auth_headers(client, "warehouse@stockpilot.local")
    seed = lookup_seed_data(client, inventory_headers)
    product = create_product(client, inventory_headers, "NO-STOCK-ISSUE", seed["category_id"], seed["supplier_id"])

    request = client.post(
        "/api/stock-requests",
        headers=requester_headers,
        json={
            "source_warehouse_id": seed["central_id"],
            "purpose": "Request product that has no stock.",
            "items": [{"product_id": product["id"], "quantity_requested": 8}],
        },
    ).json()
    approved = client.post(f"/api/stock-requests/{request['id']}/approve", headers=inventory_headers)
    issued = client.post(f"/api/stock-requests/{request['id']}/issue", headers=warehouse_headers)
    movements = client.get("/api/stock-movements", headers=inventory_headers, params={"search": "NO-STOCK-ISSUE"}).json()

    assert approved.status_code == 200
    assert issued.status_code == 400
    assert issued.json()["detail"] == "Insufficient stock for one or more requested items."
    assert movements == []


def test_stock_transfer_creates_out_and_in_movements(client):
    warehouse_headers = auth_headers(client, "warehouse@stockpilot.local")
    inventory_headers = auth_headers(client, "inventory@stockpilot.local")
    seed = lookup_seed_data(client, inventory_headers)
    product = client.get("/api/products", headers=inventory_headers, params={"search": "A4 Printing Paper Ream"}).json()[0]
    before = client.get(f"/api/inventory/{product['id']}", headers=inventory_headers).json()
    before_central = next(balance for balance in before["balances"] if balance["warehouse"]["code"] == "CENTRAL")
    before_north = next(balance for balance in before["balances"] if balance["warehouse"]["code"] == "NORTH")

    transfer = client.post(
        "/api/transfers",
        headers=warehouse_headers,
        json={
            "source_warehouse_id": seed["central_id"],
            "destination_warehouse_id": seed["north_id"],
            "items": [{"product_id": product["id"], "quantity": 20}],
        },
    ).json()

    dispatched = client.post(f"/api/transfers/{transfer['id']}/dispatch", headers=warehouse_headers)
    received = client.post(f"/api/transfers/{transfer['id']}/receive", headers=warehouse_headers)
    after = client.get(f"/api/inventory/{product['id']}", headers=inventory_headers).json()
    after_central = next(balance for balance in after["balances"] if balance["warehouse"]["code"] == "CENTRAL")
    after_north = next(balance for balance in after["balances"] if balance["warehouse"]["code"] == "NORTH")
    movements = client.get("/api/stock-movements", headers=inventory_headers, params={"search": received.json()["transfer_number"]}).json()

    assert dispatched.status_code == 200
    assert received.status_code == 200
    assert received.json()["status"] == "COMPLETED"
    assert after_central["quantity_on_hand"] == before_central["quantity_on_hand"] - 20
    assert after_north["quantity_on_hand"] == before_north["quantity_on_hand"] + 20
    assert {"TRANSFER_OUT", "TRANSFER_IN"}.issubset({movement["movement_type"] for movement in movements})


def test_notifications_and_audit_logs_are_available(client):
    inventory_headers = auth_headers(client, "inventory@stockpilot.local")
    auditor_headers = auth_headers(client, "auditor@stockpilot.local")

    notifications = client.get("/api/notifications", headers=inventory_headers)
    audit_logs = client.get("/api/audit-logs", headers=auditor_headers)
    analytics = client.get("/api/analytics/dashboard", headers=auditor_headers)
    search = client.get("/api/search", headers=inventory_headers, params={"q": "LAP-HP"})

    assert notifications.status_code == 200
    assert len(notifications.json()) > 0
    assert audit_logs.status_code == 200
    assert len(audit_logs.json()) > 0
    assert analytics.status_code == 200
    assert Decimal(str(analytics.json()["inventory_value"])) > 0
    assert search.status_code == 200
    assert any(result["type"] == "Product" for result in search.json())
