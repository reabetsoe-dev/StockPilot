def test_login_returns_jwt_and_user(client):
    response = client.post(
        "/api/auth/login",
        json={"email": "admin@stockpilot.local", "password": "Demo123!"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["token_type"] == "bearer"
    assert body["access_token"]
    assert body["user"]["role"] == "ADMINISTRATOR"


def test_login_rejects_invalid_credentials(client):
    response = client.post(
        "/api/auth/login",
        json={"email": "admin@stockpilot.local", "password": "wrong"},
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid email or password."


def test_me_requires_valid_token(client):
    login = client.post(
        "/api/auth/login",
        json={"email": "warehouse@stockpilot.local", "password": "Demo123!"},
    )
    token = login.json()["access_token"]

    response = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 200
    assert response.json()["email"] == "warehouse@stockpilot.local"


def test_dashboard_summary_returns_phase_one_metrics(client):
    login = client.post(
        "/api/auth/login",
        json={"email": "auditor@stockpilot.local", "password": "Demo123!"},
    )
    token = login.json()["access_token"]

    response = client.get("/api/dashboard/summary", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 200
    body = response.json()
    assert body["organization"] == "StockPilot Distribution Ltd"
    assert body["departments"] == 7
    assert body["demo_accounts"] == 20
    assert len(body["role_counts"]) == 6
