# ── order_service/app.py ─────────────────────────────────────────────────────
# The Order Service is a Flask microservice that accepts customer orders.
# It calls the Product Service over HTTP to validate that the product exists
# before confirming the order — demonstrating inter-service communication.
#
# DevOps note: PRODUCT_SERVICE_URL is injected as an environment variable.
# • In Docker Compose: set to http://product_service:5001
# • In Kubernetes:     set to http://product-service (ClusterIP DNS)
# • Locally:           defaults to http://localhost:5001
#
# Port: 5002
# ─────────────────────────────────────────────────────────────────────────────

import os
import requests
from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# ── Configuration via Environment Variable ────────────────────────────────────
# Reading config from the environment is a 12-Factor App principle.
# It decouples the service from any specific deployment topology.
PRODUCT_SERVICE_URL = os.environ.get("PRODUCT_SERVICE_URL", "http://localhost:5001")

# ── In-Memory Order Store ─────────────────────────────────────────────────────
_orders = []
_next_order_id = 1


# ── Health Endpoint ───────────────────────────────────────────────────────────
# Kubernetes liveness and readiness probes call this route.
@app.route("/health")
def health():
    return jsonify({"status": "healthy", "service": "order-service"}), 200


# ── Place Order ───────────────────────────────────────────────────────────────
@app.route("/order", methods=["POST"])
def place_order():
    """
    Accept a JSON body with a 'product_id' field.
    1. Validate the request body.
    2. Call the Product Service to confirm the product exists.
    3. If found, create and store the order; return 201 Created.
    """
    global _next_order_id

    body = request.get_json(silent=True)
    if not body or "product_id" not in body:
        return jsonify({"error": "Request body must contain 'product_id'"}), 400

    product_id = str(body["product_id"])

    # ── Inter-Service Call ────────────────────────────────────────────────────
    # This is the key microservice pattern: the Order Service does NOT
    # duplicate the product catalogue.  It delegates to the authoritative
    # source — the Product Service — via its internal DNS name.
    try:
        product_url = f"{PRODUCT_SERVICE_URL}/products/{product_id}"
        resp = requests.get(product_url, timeout=5)
    except requests.exceptions.ConnectionError:
        return jsonify({"error": "Product Service is unreachable"}), 503
    except requests.exceptions.Timeout:
        return jsonify({"error": "Product Service timed out"}), 504

    if resp.status_code == 404:
        return jsonify({"error": f"Product '{product_id}' does not exist"}), 404

    if resp.status_code != 200:
        return jsonify({"error": "Unexpected response from Product Service"}), 502

    product = resp.json()

    # ── Create the Order ──────────────────────────────────────────────────────
    order = {
        "order_id":     _next_order_id,
        "product_id":   product_id,
        "product_name": product.get("name"),
        "unit_price":   product.get("price"),
        "status":       "confirmed",
    }
    _orders.append(order)
    _next_order_id += 1

    return jsonify(order), 201


# ── Entry Point ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5002, debug=False)
