"""
Tests for the Order Service
=============================
Key Concept — Mocking:
  The Order Service depends on the Product Service being available.
  In unit tests, we don't want to run the actual Product Service.
  Instead, we use unittest.mock.patch() to *replace* the HTTP call
  with a fake ("mock") that returns whatever we tell it to.

  This keeps tests:
  - Fast (no real network calls)
  - Isolated (no dependency on another service running)
  - Deterministic (same result every time)
"""

import pytest
from unittest.mock import patch, MagicMock
from app import app, orders, order_counter


@pytest.fixture
def client():
    """Provides a fresh test client and resets order state between tests."""
    app.config["TESTING"] = True
    # Reset the in-memory order store before each test
    orders.clear()
    import app as app_module
    app_module.order_counter = 0
    with app.test_client() as client:
        yield client


# ── POST /orders — success ─────────────────────────────────────────

@patch("app.http_client.get")  # Replace requests.get in app.py
def test_create_order_success(mock_get, client):
    """
    Simulate the Product Service returning a valid product.
    The order should be created with status 201.
    """
    # Configure the mock to behave like a successful HTTP response
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "id": 1, "name": "Laptop", "price": 1200.00
    }
    mock_get.return_value = mock_response

    # Send the order request
    response = client.post("/orders", json={
        "product_id": 1,
        "quantity": 2
    })

    assert response.status_code == 201
    data = response.get_json()
    assert data["order_id"] == 1
    assert data["quantity"] == 2
    assert data["total_price"] == 2400.00
    assert data["status"] == "confirmed"


# ── POST /orders — product not found ──────────────────────────────

@patch("app.http_client.get")
def test_create_order_product_not_found(mock_get, client):
    """
    Simulate the Product Service returning 404.
    Our Order Service should also return 404.
    """
    mock_response = MagicMock()
    mock_response.status_code = 404
    mock_get.return_value = mock_response

    response = client.post("/orders", json={
        "product_id": 999,
        "quantity": 1
    })

    assert response.status_code == 404
    data = response.get_json()
    assert "error" in data


# ── POST /orders — missing fields ─────────────────────────────────

def test_create_order_missing_fields(client):
    """Should return 400 if product_id or quantity is missing."""
    response = client.post("/orders", json={"product_id": 1})
    assert response.status_code == 400


# ── POST /orders — Product Service down ───────────────────────────

@patch("app.http_client.get")
def test_create_order_service_unavailable(mock_get, client):
    """
    Simulate the Product Service being completely unreachable.
    Our service should return 503 Service Unavailable.
    """
    import requests
    mock_get.side_effect = requests.exceptions.ConnectionError()

    response = client.post("/orders", json={
        "product_id": 1,
        "quantity": 1
    })

    assert response.status_code == 503


# ── GET /health ────────────────────────────────────────────────────

def test_health_check(client):
    """Health endpoint should return 200."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "healthy"
