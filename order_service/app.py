"""
Order Service — The Checkout Counter
=====================================
This microservice handles placing orders. Before confirming any order,
it makes an HTTP request to the Product Service to verify the product
actually exists. This is the core of microservice communication.

Key Concepts:
- Inter-Service Communication: Microservices talk to each other over
  HTTP, just like a browser talks to a website. We use Python's
  `requests` library to make these calls.
- Environment Variables (os.environ): Configuration that can change
  between environments (local, staging, production) is stored in
  env vars, NOT hardcoded. This lets Kubernetes or Docker inject
  the correct URL at runtime.
- requests.get(): Sends an HTTP GET request and returns a Response
  object with .status_code, .json(), etc.
"""

import os
import requests as http_client  # renamed to avoid confusion with Flask's request
from flask import Flask, jsonify, request

# ── Create Flask app ───────────────────────────────────────────────
app = Flask(__name__)

# ── Configuration ──────────────────────────────────────────────────
# In Docker/Kubernetes, this env var will point to the Product Service
# container. Locally, it defaults to localhost:5001.
PRODUCT_SERVICE_URL = os.environ.get("PRODUCT_SERVICE_URL", "http://localhost:5001")

# ── In-Memory Order Storage ───────────────────────────────────────
# In a real app this would be a database. We use a simple list here.
orders = []
order_counter = 0  # auto-incrementing ID


@app.route("/orders", methods=["POST"])
def create_order():
    """
    POST /orders
    Body: { "product_id": 1, "quantity": 2 }

    Workflow:
    1. Parse the JSON body.
    2. Call the Product Service to check if the product exists.
    3. If it exists → create the order and return 201 Created.
    4. If it doesn't → return 404 with an error message.
    5. If the Product Service is unreachable → return 503.
    """
    global order_counter
    data = request.get_json()

    # ── Validate input ─────────────────────────────────────────
    if not data or "product_id" not in data or "quantity" not in data:
        return jsonify({"error": "Missing product_id or quantity"}), 400

    product_id = data["product_id"]
    quantity = data["quantity"]

    # ── Call Product Service (inter-service communication) ─────
    try:
        response = http_client.get(
            f"{PRODUCT_SERVICE_URL}/products/{product_id}",
            timeout=5  # seconds — don't hang forever if the service is down
        )
    except http_client.exceptions.ConnectionError:
        return jsonify({"error": "Product Service is unavailable"}), 503

    if response.status_code == 404:
        return jsonify({"error": f"Product {product_id} not found"}), 404

    # ── Product exists — create the order ──────────────────────
    product = response.json()
    order_counter += 1
    order = {
        "order_id": order_counter,
        "product": product,
        "quantity": quantity,
        "total_price": product["price"] * quantity,
        "status": "confirmed",
    }
    orders.append(order)

    return jsonify(order), 201


@app.route("/orders", methods=["GET"])
def get_all_orders():
    """
    GET /orders
    Returns all orders that have been placed.
    """
    return jsonify(orders), 200


@app.route("/health", methods=["GET"])
def health_check():
    """
    GET /health
    Kubernetes liveness probe endpoint.
    """
    return jsonify({"status": "healthy", "service": "order-service"}), 200


# ── Entry Point ────────────────────────────────────────────────────
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5002, debug=True)
