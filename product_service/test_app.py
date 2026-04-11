"""
Tests for the Product Service
==============================
We use pytest + Flask's built-in test client.

Key Concept — Test Client:
  Flask provides app.test_client() which simulates HTTP requests
  *without* starting a real server. This makes tests fast and isolated.
"""

import pytest
from app import app


@pytest.fixture
def client():
    """
    A pytest 'fixture' — a reusable piece of setup code.
    Every test function that lists 'client' as a parameter will
    automatically receive a fresh test client.
    """
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


# ── GET /products ──────────────────────────────────────────────────

def test_get_all_products(client):
    """Should return a JSON list of all 5 products with status 200."""
    response = client.get("/products")
    assert response.status_code == 200

    data = response.get_json()
    assert isinstance(data, list)
    assert len(data) == 5
    assert data[0]["name"] == "Laptop"


# ── GET /products/<id> — valid ─────────────────────────────────────

def test_get_single_product(client):
    """Should return the correct product when a valid ID is given."""
    response = client.get("/products/1")
    assert response.status_code == 200

    data = response.get_json()
    assert data["id"] == 1
    assert data["name"] == "Laptop"
    assert data["price"] == 1200.00


# ── GET /products/<id> — not found ────────────────────────────────

def test_product_not_found(client):
    """Should return 404 and an error message for a non-existent ID."""
    response = client.get("/products/999")
    assert response.status_code == 404

    data = response.get_json()
    assert "error" in data


# ── GET /health ────────────────────────────────────────────────────

def test_health_check(client):
    """Health endpoint should return 200 and service name."""
    response = client.get("/health")
    assert response.status_code == 200

    data = response.get_json()
    assert data["status"] == "healthy"
