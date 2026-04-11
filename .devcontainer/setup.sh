#!/bin/bash
set -e

echo ""
echo "================================================"
echo "  E-Commerce K8s Demo — Auto Setup"
echo "================================================"
echo ""

# ── Step 1: Install k3d ──────────────────────────────────────────��────────────
echo "[1/6] Installing k3d..."
curl -s https://raw.githubusercontent.com/k3d-io/k3d/main/install.sh | bash
echo "      k3d installed."

# ── Step 2: Create k3d cluster with fixed NodePort mappings ──────────────────
echo "[2/6] Creating Kubernetes cluster..."
k3d cluster create ecommerce \
  -p "30001:30001@server:0" \
  -p "30002:30002@server:0" \
  -p "30003:30003@server:0" \
  -p "30080:30080@server:0" \
  --k3s-arg "--disable=traefik@server:*" \
  --wait

echo "      Cluster ready."
kubectl wait --for=condition=ready node --all --timeout=60s

# ── Step 3: Update frontend config.js with Codespace URLs ────────────────────
echo "[3/6] Configuring frontend URLs..."
if [ -n "$CODESPACE_NAME" ]; then
  echo "      Detected GitHub Codespace: $CODESPACE_NAME"
  cat > frontend/config.js << EOF
const API_URLS = {
    products: "https://${CODESPACE_NAME}-30001.app.github.dev",
    orders:   "https://${CODESPACE_NAME}-30002.app.github.dev",
    users:    "https://${CODESPACE_NAME}-30003.app.github.dev"
};
export default API_URLS;
EOF
  echo "      config.js updated with Codespace URLs."
else
  echo "      Not in Codespaces — using default config.js."
fi

# ── Step 4: Build frontend image and import into cluster ─────────────────────
echo "[4/6] Building and loading frontend image..."
docker build -t durai85/frontend:latest ./frontend
k3d image import durai85/frontend:latest -c ecommerce
echo "      Frontend image loaded into cluster."

# ── Step 5: Deploy all Kubernetes manifests ───────────────────────────────────
echo "[5/6] Deploying services to Kubernetes..."
kubectl apply -f kubernetes/product-manifests.yaml
kubectl apply -f kubernetes/order-manifests.yaml
kubectl apply -f kubernetes/user-manifests.yaml
kubectl apply -f kubernetes/frontend-manifests.yaml
kubectl apply -f kubernetes/nodeport-services.yaml
echo "      Manifests applied."

# ── Step 6: Wait for all deployments to be ready ─────────────────────────────
echo "[6/6] Waiting for pods to be ready..."
kubectl rollout status deployment/product-service --timeout=120s
kubectl rollout status deployment/order-service   --timeout=120s
kubectl rollout status deployment/user-service    --timeout=120s
kubectl rollout status deployment/frontend        --timeout=120s

# ── Done ──────────────────────────────────────────────────────────────────────
echo ""
echo "================================================"
echo "  Deployment Complete!"
echo "================================================"
echo ""
if [ -n "$CODESPACE_NAME" ]; then
  echo "  Frontend  → https://${CODESPACE_NAME}-30080.app.github.dev"
  echo "  Products  → https://${CODESPACE_NAME}-30001.app.github.dev/products"
  echo "  Orders    → https://${CODESPACE_NAME}-30002.app.github.dev/order"
  echo "  Users     → https://${CODESPACE_NAME}-30003.app.github.dev/users"
else
  echo "  Frontend  → http://localhost:30080"
  echo "  Products  → http://localhost:30001/products"
  echo "  Orders    → http://localhost:30002/order"
  echo "  Users     → http://localhost:30003/users"
fi
echo ""
kubectl get pods
