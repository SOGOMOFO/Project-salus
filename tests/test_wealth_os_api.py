from fastapi.testclient import TestClient

from backend.main import app


client = TestClient(app)


def test_wealth_os_framework_loads():
    response = client.get("/wealth-os/framework")
    assert response.status_code == 200

    data = response.json()
    assert data["name"] == "Project Salus Wealth Operating System"
    assert "security_cash" in data["dollar_missions"]
    assert "index_investing" in data["dollar_missions"]


def test_dollar_classifies_to_security_cash_when_emergency_fund_low():
    payload = {
        "amount": 10000,
        "emergency_months": 2,
        "target_emergency_months": 6,
        "highest_debt_apr": 0,
        "timeframe": "long_term",
        "goal": "wealth_building",
        "risk_tolerance": "medium",
    }

    response = client.post("/wealth-os/classify-dollar", json=payload)
    assert response.status_code == 200

    data = response.json()
    assert data["assigned_mission"] == "security_cash"
    assert data["amount"] == 10000


def test_dollar_classifies_to_debt_attack_for_high_interest_debt():
    payload = {
        "amount": 5000,
        "emergency_months": 6,
        "target_emergency_months": 6,
        "highest_debt_apr": 18,
        "timeframe": "long_term",
        "goal": "wealth_building",
        "risk_tolerance": "medium",
    }

    response = client.post("/wealth-os/classify-dollar", json=payload)
    assert response.status_code == 200

    data = response.json()
    assert data["assigned_mission"] == "debt_attack"


def test_cash_allocation_prioritizes_security_and_debt():
    payload = {
        "cash_available": 20000,
        "monthly_expenses": 7000,
        "current_emergency_cash": 10000,
        "target_emergency_months": 3,
        "upcoming_obligations_90_days": 1000,
        "high_interest_debt_balance": 5000,
        "human_capital_need": 1500,
        "business_capital_need": 2500,
        "speculative_cap_percent": 10,
    }

    response = client.post("/wealth-os/allocate-cash", json=payload)
    assert response.status_code == 200

    data = response.json()
    assert data["emergency_gap"] == 11000
    assert data["allocations"]["security_cash"] == 11000
    assert data["allocations"]["operating_cash"] == 1000
    assert data["allocations"]["debt_attack"] == 5000
    assert "Emergency fund below target." in data["risk_flags"]
