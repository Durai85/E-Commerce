# ── product_service/app.py ───────────────────────────────────────────────────
# The Product Service is a standalone Flask microservice.
# Responsibility: serve a catalogue of products from an in-memory dictionary.
#
# DevOps note: keeping business logic trivially simple means the CI pipeline
# can validate infrastructure correctness without any risk of logic bugs
# interfering with the evaluation.
#
# Port: 5001  (set in the Dockerfile CMD and Kubernetes manifest)
# ─────────────────────────────────────────────────────────────────────────────

from flask import Flask, jsonify

app = Flask(__name__)

# ── Mock Database ─────────────────────────────────────────────────────────────
# In production this would be replaced by a real DB (PostgreSQL, DynamoDB …).
# Using a plain dict keeps the service 100 % self-contained for demo purposes.
PRODUCTS = {
    "1": {"id": "1", "name": "Laptop Pro 15",   "price": 1299.99, "stock": 45},
    "2": {"id": "2", "name": "Wireless Mouse",   "price":   29.99, "stock": 200},
    "3": {"id": "3", "name": "Mechanical Keyboard", "price": 89.99, "stock": 120},
}


# ── Health Endpoint ───────────────────────────────────────────────────────────
# Both the Kubernetes livenessProbe and readinessProbe hit this route.
# A 200 response means the container is alive and ready to serve traffic.
@app.route("/health")
def health():
    return jsonify({"status": "healthy", "service": "product-service"}), 200


# ── List All Products ─────────────────────────────────────────────────────────
@app.route("/products")
def get_products():
    """Return the full product catalogue as a JSON array."""
    return jsonify(list(PRODUCTS.values())), 200


# ── Get Single Product ────────────────────────────────────────────────────────
@app.route("/products/<product_id>")
def get_product(product_id):
    """Return a single product by its ID, or 404 if it does not exist."""
    product = PRODUCTS.get(product_id)
    if not product:
        return jsonify({"error": f"Product '{product_id}' not found"}), 404
    return jsonify(product), 200


# ── Entry Point ───────────────────────────────────────────────────────────────
# host='0.0.0.0' is required inside a Docker container so the port is reachable
# from outside the container network namespace.
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=False)
