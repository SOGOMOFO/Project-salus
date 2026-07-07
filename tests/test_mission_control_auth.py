from fastapi.testclient import TestClient

from backend.main import app


client = TestClient(app)


def test_auth_status_api():
    response = client.get("/api/mission-control/auth/status")
    assert response.status_code == 200

    data = response.json()
    assert data["status"] == "ok"
    assert "auth_enabled" in data
    assert "recommended_action" in data


def test_login_page_loads():
    response = client.get("/mission-control/login")
    assert response.status_code == 200
    assert "Project Salus" in response.text
    assert "Local dashboard access gate" in response.text


def test_dashboard_redirects_without_auth():
    response = client.get("/mission-control/v1", follow_redirects=False)
    assert response.status_code == 303
    assert response.headers["location"] == "/mission-control/login"


def test_login_rejects_bad_password():
    response = client.post(
        "/mission-control/login",
        data={"password": "wrong-password"},
    )

    assert response.status_code == 401
    assert "Access denied" in response.text


def test_login_accepts_default_local_password():
    response = client.post(
        "/mission-control/login",
        data={"password": "salus-local"},
        follow_redirects=False,
    )

    assert response.status_code == 303
    assert response.headers["location"] == "/mission-control/v1"
    assert "salus_access" in response.cookies


def test_dashboard_loads_with_cookie():
    login = client.post(
        "/mission-control/login",
        data={"password": "salus-local"},
        follow_redirects=False,
    )

    cookies = login.cookies

    response = client.get("/mission-control/v1", cookies=cookies)
    assert response.status_code == 200
    assert "Mission Control" in response.text or "Project Salus" in response.text


def test_dashboard_loads_with_header_token():
    response = client.get(
        "/mission-control/v1",
        headers={"x-salus-token": "salus-local-token"},
    )

    assert response.status_code == 200
    assert "Mission Control" in response.text or "Project Salus" in response.text


def test_logout_clears_cookie():
    response = client.post("/mission-control/logout", follow_redirects=False)

    assert response.status_code == 303
    assert response.headers["location"] == "/mission-control/login"
