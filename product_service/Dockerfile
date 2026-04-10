# ── product_service/Dockerfile ───────────────────────────────────────────────
# Multi-stage-ready, production-grade Dockerfile for the Product Service.
#
# Design decisions:
#   - python:3.9-slim  → minimal attack surface vs the full python image
#   - WORKDIR /app     → keeps the container filesystem organised
#   - Copy requirements first → Docker layer-cache means 'pip install' only
#                                re-runs when requirements.txt changes, not on
#                                every code edit (speeds up CI builds).
#   - Non-root user    → security best practice; avoids privilege escalation
# ─────────────────────────────────────────────────────────────────────────────

# ── Base Image ────────────────────────────────────────────────────────────────
FROM python:3.9-slim

# ── Metadata ──────────────────────────────────────────────────────────────────
LABEL maintainer="devops-team" \
      service="product-service" \
      version="1.0"

# ── Working Directory ─────────────────────────────────────────────────────────
# All subsequent COPY, RUN, CMD instructions operate relative to /app.
WORKDIR /app

# ── Install Dependencies (cached layer) ──────────────────────────────────────
# Copy only the dependency manifest first so Docker can cache this layer.
# The layer is invalidated only when requirements.txt changes.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ── Copy Application Source ───────────────────────────────────────────────────
COPY . .

# ── Security: Run as Non-Root User ───────────────────────────────────────────
RUN adduser --disabled-password --gecos "" appuser
USER appuser

# ── Network ───────────────────────────────────────────────────────────────────
# Documents the port the application listens on.
# The Kubernetes manifest maps this to a Service port.
EXPOSE 5001

# ── Start Command ─────────────────────────────────────────────────────────────
# Use the module directly instead of the Flask dev server in production.
CMD ["python", "app.py"]
