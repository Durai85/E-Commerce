# ── user_service/test_app.py ──────────────────────────────────────────────────
# Unit tests for the User Service.
# Run with: pytest test_app.py -v
# ─────────────────────────────────────────────────────────────────────────────

import pytest
from app import app, USERS, _next_user_id


# ── Fixture ───────────────────────────────────────────────────────────────────
@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


# ── Health Check ──────────────────────────────────────────────────────────────
def test_health_returns_200(client):
    """Kubernetes probes depend on this returning HTTP 200."""
    response = client.get("/health")
    assert response.status_code == 200


def test_health_returns_healthy_status(client):
    response = client.get("/health")
    data = response.get_json()
    assert data["status"] == "healthy"
    assert data["service"] == "user-service"


# ── List Users ────────────────────────────────────────────────────────────────
def test_get_users_returns_200(client):
    response = client.get("/users")
    assert response.status_code == 200


def test_get_users_returns_list(client):
    response = client.get("/users")
    data = response.get_json()
    assert isinstance(data, list)
    assert len(data) >= 3   # At least the three seeded users


# ── Get Single User ───────────────────────────────────────────────────────────
def test_get_user_returns_correct_user(client):
    response = client.get("/users/u1")
    assert response.status_code == 200
    data = response.get_json()
    assert data["id"] == "u1"
    assert data["email"] == "alice@example.com"


def test_get_user_not_found_returns_404(client):
    response = client.get("/users/u9999")
    assert response.status_code == 404


# ── Register New User — Happy Path ────────────────────────────────────────────
def test_create_user_success(client):
    """A valid registration must return 201 with the new user object."""
    payload = {"name": "Dave Test", "email": "dave.test.unique@example.com"}
    response = client.post("/users", json=payload)
    assert response.status_code == 201
    data = response.get_json()
    assert data["name"] == "Dave Test"
    assert data["email"] == "dave.test.unique@example.com"
    assert data["role"] == "customer"   # default role


# ── Register New User — Validation Errors ─────────────────────────────────────
def test_create_user_missing_name_returns_400(client):
    response = client.post("/users", json={"email": "missing@example.com"})
    assert response.status_code == 400


def test_create_user_missing_email_returns_400(client):
    response = client.post("/users", json={"name": "No Email"})
    assert response.status_code == 400


def test_create_user_no_body_returns_400(client):
    response = client.post("/users", data="not-json", content_type="text/plain")
    assert response.status_code == 400


# ── Register New User — Duplicate Email ──────────────────────────────────────
def test_create_user_duplicate_email_returns_409(client):
    """Attempting to register with an already-used email must return 409."""
    response = client.post("/users", json={"name": "Duplicate", "email": "alice@example.com"})
    assert response.status_code == 409
