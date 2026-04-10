# ── user_service/Dockerfile ───────────────────────────────────────────────────
# Production-grade Dockerfile for the User Service.
#
# Design decisions mirror the other services in this repo:
#   - python:3.9-slim  → minimal attack surface
#   - requirements first → Docker layer-cache speeds up CI builds
#   - Non-root user    → security best practice
# ─────────────────────────────────────────────────────────────────────────────

FROM python:3.9-slim

LABEL maintainer="devops-team" \
      service="user-service" \
      version="1.0"

WORKDIR /app

# ── Install Dependencies (cached layer) ──────────────────────────────────────
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ── Copy Application Source ───────────────────────────────────────────────────
COPY . .

# ── Security: Run as Non-Root User ───────────────────────────────────────────
RUN adduser --disabled-password --gecos "" appuser
USER appuser

EXPOSE 5003

CMD ["python", "app.py"]
