#!/usr/bin/env bash
# ── build-frontend.sh ─────────────────────────────────────────────────────────
# Injects Render environment variables into the static frontend at build time.
# Replaces the localhost placeholder URLs with the actual deployed service URLs.
# ─────────────────────────────────────────────────────────────────────────────
set -e

echo "Injecting service URLs into frontend..."

sed -i "s|http://localhost:5011|${PRODUCT_SERVICE_URL}|g" frontend/index.html
sed -i "s|http://localhost:5012|${ORDER_SERVICE_URL}|g"   frontend/index.html
sed -i "s|http://localhost:5013|${USER_SERVICE_URL}|g"    frontend/index.html

echo "Done. URLs injected:"
echo "  Product : ${PRODUCT_SERVICE_URL}"
echo "  Order   : ${ORDER_SERVICE_URL}"
echo "  User    : ${USER_SERVICE_URL}"
