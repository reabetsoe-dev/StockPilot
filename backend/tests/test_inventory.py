from decimal import Decimal


def auth_headers(client, email):
    response = client.post(
        "/api/auth/login",
        json={"email": email, "password": "Demo123!"},
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_inventory_index_calculates_stock_status_and_value(client):
    response = client.get(
        "/api/inventory",
        headers=auth_headers(client, "inventory@stockpilot.local"),
        params={"search": "LAP-HP-840"},
    )

    assert response.status_code == 200
    body = response.json()
    assert len(body) == 1
    laptop = body[0]
    assert laptop["sku"] == "LAP-HP-840"
    assert laptop["total_on_hand"] == 9
    assert laptop["total_reserved"] == 1
    assert laptop["available_quantity"] == 8
    assert laptop["stock_status"] == "NORMAL"
    assert Decimal(str(laptop["inventory_value"])) == Decimal("130500.00")


def test_product_inventory_detail_shows_balances_and_movements(client):
    headers = auth_headers(client, "warehouse@stockpilot.local")
    inventory = client.get("/api/inventory", headers=headers, params={"search": "LAP-HP-840"}).json()
    product_id = inventory[0]["product_id"]

    response = client.get(f"/api/inventory/{product_id}", headers=headers)

    assert response.status_code == 200
    body = response.json()
    assert body["product"]["sku"] == "LAP-HP-840"
    assert body["total_on_hand"] == 9
    assert len(body["balances"]) == 3
    assert sum(balance["quantity_on_hand"] for balance in body["balances"]) == 9
    assert {"OPENING_BALANCE", "GOODS_RECEIPT"}.issubset(
        {movement["movement_type"] for movement in body["recent_movements"]}
    )
    assert sum(movement["quantity"] for movement in body["recent_movements"]) == 9


def test_stock_movements_can_be_filtered(client):
    response = client.get(
        "/api/stock-movements",
        headers=auth_headers(client, "auditor@stockpilot.local"),
        params={"movement_type": "OPENING_BALANCE", "search": "CENTRAL", "limit": 5},
    )

    assert response.status_code == 200
    body = response.json()
    assert len(body) == 5
    assert {movement["movement_type"] for movement in body} == {"OPENING_BALANCE"}
    assert {movement["warehouse_code"] for movement in body} == {"CENTRAL"}


def test_out_of_stock_filter_returns_seeded_records(client):
    response = client.get(
        "/api/inventory",
        headers=auth_headers(client, "inventory@stockpilot.local"),
        params={"stock_status": "OUT_OF_STOCK"},
    )

    assert response.status_code == 200
    skus = {item["sku"] for item in response.json()}
    assert "NET-RACK-12U" in skus
    assert "TBL-MEET-8" in skus


def test_department_requester_cannot_view_inventory_ledger(client):
    response = client.get(
        "/api/inventory",
        headers=auth_headers(client, "requester@stockpilot.local"),
    )

    assert response.status_code == 403
