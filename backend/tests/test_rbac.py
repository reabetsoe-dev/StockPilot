def auth_headers(client, email):
    response = client.post(
        "/api/auth/login",
        json={"email": email, "password": "Demo123!"},
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_administrator_can_create_user(client):
    response = client.post(
        "/api/users",
        headers=auth_headers(client, "admin@stockpilot.local"),
        json={
            "full_name": "New Buyer",
            "email": "new.buyer@stockpilot.local",
            "password": "Demo123!",
            "role": "PROCUREMENT_OFFICER",
            "department_id": 1,
            "active": True,
        },
    )

    assert response.status_code == 201
    assert response.json()["email"] == "new.buyer@stockpilot.local"


def test_auditor_cannot_create_user(client):
    response = client.post(
        "/api/users",
        headers=auth_headers(client, "auditor@stockpilot.local"),
        json={
            "full_name": "Unauthorized User",
            "email": "unauthorized@stockpilot.local",
            "password": "Demo123!",
            "role": "WAREHOUSE_OFFICER",
            "department_id": 1,
            "active": True,
        },
    )

    assert response.status_code == 403


def test_departments_are_protected(client):
    response = client.get("/api/departments")

    assert response.status_code == 401
