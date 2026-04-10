# ── order_service/test_app.py ─────────────────────────────────────────────────
# Unit tests for the Order Service.
# Run with: pytest test_app.py -v
#
# Key technique: unittest.mock.patch is used to replace the real HTTP call to
# the Product Service with a controlled fake (mock).  This means the tests:
#   ✓ run without a live Product Service
#   ✓ are deterministic and fast
#   ✓ cover multiple scenarios (success, 404, connection error)
# ─────────────────────────────────────────────────────────────────────────────

import pytest
from unittest.mock import patch, MagicMock
import requests as real_requests

from app import app


# ── Fixture ───────────────────────────────────────────────────────────────────
@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


# ── Health Check ──────────────────────────────────────────────────────────────
def test_health_returns_200(client):
    """Kubernetes probes depend on this returning HTTP 200."""
    response = client.get("/health")
    assert response.status_code == 200


def test_health_returns_healthy_status(client):
    response = client.get("/health")
    data = response.get_json()
    assert data["status"] == "healthy"


# ── Place Order — Happy Path ───────────────────────────────────────────────────
def test_place_order_success(client):
    """
    Mock a successful 200 response from the Product Service.
    The order should be created and returned with status 'confirmed'.
    """
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        "id": "1", "name": "Laptop Pro 15", "price": 1299.99, "stock": 45
    }

    with patch("app.requests.get", return_value=mock_resp):
        response = client.post("/order", json={"product_id": "1"})

    assert response.status_code == 201
    data = response.get_json()
    assert data["status"] == "confirmed"
    assert data["product_id"] == "1"
    assert data["product_name"] == "Laptop Pro 15"


# ── Place Order — Validation Errors ──────────────────────────────────────────
def test_place_order_missing_body_returns_400(client):
    """Missing product_id must be rejected with 400 Bad Request."""
    response = client.post("/order", json={})
    assert response.status_code == 400


def test_place_order_no_json_returns_400(client):
    response = client.post("/order", data="not-json", content_type="text/plain")
    assert response.status_code == 400


# ── Place Order — Product Not Found ──────────────────────────────────────────
def test_place_order_product_not_found_returns_404(client):
    """If the Product Service returns 404, the Order Service must return 404."""
    mock_resp = MagicMock()
    mock_resp.status_code = 404

    with patch("app.requests.get", return_value=mock_resp):
        response = client.post("/order", json={"product_id": "9999"})

    assert response.status_code == 404


# ── Place Order — Product Service Unreachable ─────────────────────────────────
def test_place_order_product_service_down_returns_503(client):
    """A ConnectionError from requests must surface as 503 Service Unavailable."""
    with patch("app.requests.get", side_effect=real_requests.exceptions.ConnectionError):
        response = client.post("/order", json={"product_id": "1"})

    assert response.status_code == 503
