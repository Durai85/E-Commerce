# E-Commerce Microservices — DevOps IA3

A mini e-commerce backend built with two Python/Flask microservices and a full DevOps automation pipeline.

## Architecture

```
┌──────────────┐     HTTP GET      ┌──────────────────┐
│ Order Service │ ───────────────► │ Product Service   │
│  (port 5002)  │  /products/<id>  │   (port 5001)     │
└──────────────┘                   └──────────────────┘
```

## Services

| Service | Port | Endpoints |
|---------|------|-----------|
| Product Service | 5001 | `GET /products`, `GET /products/<id>`, `GET /health` |
| Order Service | 5002 | `POST /orders`, `GET /orders`, `GET /health` |

## Quick Start (Docker Compose)

```bash
docker-compose up -d --build
curl http://localhost:5001/products
curl -X POST http://localhost:5002/orders \
  -H "Content-Type: application/json" \
  -d '{"product_id": 1, "quantity": 2}'
```

## DevOps Pipeline

- **CI/CD**: GitHub Actions → test → Docker build → DockerHub push
- **IaC**: Terraform (AWS EC2 + VPC + Minikube)
- **Orchestration**: Kubernetes Deployments + Services
