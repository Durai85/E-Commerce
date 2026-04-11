# Progress Log — DevOps IA3 E-Commerce Microservices

## 2026-04-11
- Initialized monorepo with git, directory structure, and `.gitignore`.
- Built Product Service (Flask) with catalog API and tests.
- Built Order Service (Flask) with inter-service communication and tests.
- Created Dockerfiles for both services and `docker-compose.yml` for local orchestration.
- Created GitHub Actions CI/CD pipeline (`ci-cd.yml`): test → build → push to DockerHub.
- Created Terraform IaC (`main.tf`, `variables.tf`, `outputs.tf`) for AWS EC2 + Minikube.
- Created Kubernetes manifests (Deployments + Services) for both microservices.
