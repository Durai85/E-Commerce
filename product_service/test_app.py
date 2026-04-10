# ── product_service/test_app.py ───────────────────────────────────────────────
# Unit tests for the Product Service.
# Run with: pytest test_app.py -v
#
# DevOps note: these tests are executed in CI Job 1 ("test").
# Job 2 ("build-and-push") only runs if these tests pass, ensuring
# broken code is never containerised and pushed to DockerHub.
# ─────────────────────────────────────────────────────────────────────────────

import pytest
from app import app


# ── Fixture ───────────────────────────────────────────────────────────────────
# pytest fixtures are reusable setup/teardown helpers.
# This one creates a Flask test client so we can make HTTP calls without
# actually starting a server — fast and deterministic.
@pytest.fixture
def client():
    app.config["TESTING"] = True          # Propagate exceptions to the test
    with app.test_client() as client:
        yield client


# ── Health Check ──────────────────────────────────────────────────────────────
def test_health_returns_200(client):
    """Kubernetes probes depend on this returning HTTP 200."""
    response = client.get("/health")
    assert response.status_code == 200


def test_health_returns_healthy_status(client):
    """Response body must contain the 'healthy' status field."""
    response = client.get("/health")
    data = response.get_json()
    assert data["status"] == "healthy"


# ── Product Catalogue ─────────────────────────────────────────────────────────
def test_get_all_products_returns_200(client):
    response = client.get("/products")
    assert response.status_code == 200


def test_get_all_products_returns_list(client):
    response = client.get("/products")
    data = response.get_json()
    assert isinstance(data, list)
    assert len(data) == 3            # We seeded 3 products in PRODUCTS dict


def test_get_single_product_returns_200(client):
    response = client.get("/products/1")
    assert response.status_code == 200


def test_get_single_product_has_correct_fields(client):
    response = client.get("/products/1")
    data = response.get_json()
    assert data["id"] == "1"
    assert "name" in data
    assert "price" in data
    assert "stock" in data


def test_get_nonexistent_product_returns_404(client):
    """Order service relies on this 404 to detect invalid product IDs."""
    response = client.get("/products/9999")
    assert response.status_code == 404
