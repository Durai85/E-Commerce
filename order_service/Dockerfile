# ── order_service/Dockerfile ─────────────────────────────────────────────────
# Production-grade Dockerfile for the Order Service.
# Identical pattern to the Product Service for consistency.
# ─────────────────────────────────────────────────────────────────────────────

# ── Base Image ────────────────────────────────────────────────────────────────
FROM python:3.9-slim

# ── Metadata ──────────────────────────────────────────────────────────────────
LABEL maintainer="devops-team" \
      service="order-service" \
      version="1.0"

# ── Working Directory ─────────────────────────────────────────────────────────
WORKDIR /app

# ── Install Dependencies (cached layer) ──────────────────────────────────────
# Copying requirements.txt before the application source maximises
# Docker's layer cache: 'pip install' only re-runs when the manifest changes.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ── Copy Application Source ───────────────────────────────────────────────────
COPY . .

# ── Security: Run as Non-Root User ───────────────────────────────────────────
RUN adduser --disabled-password --gecos "" appuser
USER appuser

# ── Network ───────────────────────────────────────────────────────────────────
EXPOSE 5002

# ── Environment Variable Default ─────────────────────────────────────────────
# Can be overridden by docker run -e or a Kubernetes env block.
# In Kubernetes this will be set to the product-service ClusterIP DNS name.
ENV PRODUCT_SERVICE_URL=http://localhost:5001

# ── Start Command ─────────────────────────────────────────────────────────────
CMD ["python", "app.py"]
