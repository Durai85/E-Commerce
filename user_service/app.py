# ── user_service/app.py ───────────────────────────────────────────────────────
# The User Service is a standalone Flask microservice.
# Responsibility: manage customer and admin user accounts.
#
# DevOps note: this service is intentionally stateless (in-memory store) so
# the demo can be deployed anywhere without a database dependency.
#
# Port: 5003  (set in the Dockerfile CMD and Kubernetes manifest)
# ─────────────────────────────────────────────────────────────────────────────

from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# ── Mock Database ─────────────────────────────────────────────────────────────
# In production this would be a PostgreSQL / DynamoDB table.
# Using a plain dict keeps the service 100 % self-contained for demo purposes.
USERS = {
    "u1": {"id": "u1", "name": "Alice Johnson", "email": "alice@example.com", "role": "admin"},
    "u2": {"id": "u2", "name": "Bob Smith",     "email": "bob@example.com",   "role": "customer"},
    "u3": {"id": "u3", "name": "Carol White",   "email": "carol@example.com", "role": "customer"},
}
_next_user_id = 4   # Counter for new registrations


# ── Health Endpoint ───────────────────────────────────────────────────────────
# Both the Kubernetes livenessProbe and readinessProbe hit this route.
@app.route("/health")
def health():
    return jsonify({"status": "healthy", "service": "user-service"}), 200


# ── List All Users ────────────────────────────────────────────────────────────
@app.route("/users")
def get_users():
    """Return all registered users as a JSON array."""
    return jsonify(list(USERS.values())), 200


# ── Get Single User ───────────────────────────────────────────────────────────
@app.route("/users/<user_id>")
def get_user(user_id):
    """Return a single user by ID, or 404 if not found."""
    user = USERS.get(user_id)
    if not user:
        return jsonify({"error": f"User '{user_id}' not found"}), 404
    return jsonify(user), 200


# ── Register New User ─────────────────────────────────────────────────────────
@app.route("/users", methods=["POST"])
def create_user():
    """
    Accept a JSON body with 'name' and 'email' fields.
    1. Validate the request body.
    2. Check for duplicate email addresses.
    3. Create and store the user; return 201 Created.
    """
    global _next_user_id

    body = request.get_json(silent=True)
    if not body or "name" not in body or "email" not in body:
        return jsonify({"error": "Request body must contain 'name' and 'email'"}), 400

    # ── Duplicate-email guard ─────────────────────────────────────────────────
    email = body["email"].strip().lower()
    if any(u["email"].lower() == email for u in USERS.values()):
        return jsonify({"error": f"Email '{email}' is already registered"}), 409

    user = {
        "id":    f"u{_next_user_id}",
        "name":  body["name"].strip(),
        "email": email,
        "role":  body.get("role", "customer"),
    }
    USERS[user["id"]] = user
    _next_user_id += 1

    return jsonify(user), 201


# ── Entry Point ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5003))
    app.run(host="0.0.0.0", port=port, debug=False)
