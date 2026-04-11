"""
Product Service — The Digital Warehouse
========================================
This microservice manages a catalog of products.
It exposes a REST API so other services (like the Order Service)
can look up products by ID.

Key Concepts:
- Flask: A lightweight Python web framework. We create an "app" object
  and use decorators (@app.route) to map URL paths to Python functions.
- JSON: The standard data format for REST APIs. Flask's jsonify()
  converts Python dicts/lists into JSON HTTP responses.
- HTTP Status Codes: 200 = OK, 404 = Not Found.
"""

from flask import Flask, jsonify

# ── Create the Flask application instance ──────────────────────────
# __name__ tells Flask where to find templates/static files (not used
# here, but it's Flask convention).
app = Flask(__name__)

# ── In-Memory Product Catalog ──────────────────────────────────────
# In a real app this would be a database. For our microservice demo,
# a simple Python list of dicts is sufficient.
PRODUCTS = [
    {"id": 1, "name": "Laptop",        "price": 1200.00},
    {"id": 2, "name": "Headphones",    "price":   59.99},
    {"id": 3, "name": "Mechanical Keyboard", "price": 89.99},
    {"id": 4, "name": "USB-C Hub",     "price":   34.99},
    {"id": 5, "name": "Monitor Stand", "price":   45.00},
]

# ── Routes ─────────────────────────────────────────────────────────

@app.route("/products", methods=["GET"])
def get_all_products():
    """
    GET /products
    Returns the entire product catalog as a JSON array.
    """
    return jsonify(PRODUCTS), 200


@app.route("/products/<int:product_id>", methods=["GET"])
def get_product(product_id):
    """
    GET /products/<id>
    Looks up a single product by its integer ID.
    Returns 200 + product JSON if found, or 404 + error message.
    """
    # next() iterates through PRODUCTS and returns the first match.
    # If nothing matches, it returns None (the second argument).
    product = next((p for p in PRODUCTS if p["id"] == product_id), None)

    if product:
        return jsonify(product), 200
    else:
        return jsonify({"error": "Product not found"}), 404


@app.route("/health", methods=["GET"])
def health_check():
    """
    GET /health
    A simple health-check endpoint used by Kubernetes liveness probes
    to confirm the service is running.
    """
    return jsonify({"status": "healthy", "service": "product-service"}), 200


# ── Entry Point ────────────────────────────────────────────────────
# host="0.0.0.0" makes the server accessible from outside the
# container (by default Flask only listens on 127.0.0.1).
# port=5001 is our chosen port for the Product Service.
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)
