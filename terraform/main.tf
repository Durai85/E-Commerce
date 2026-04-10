# ── terraform/main.tf ─────────────────────────────────────────────────────────
# Infrastructure-as-Code for the E-Commerce DevOps project.
#
# What this file provisions:
#   1. AWS Security Group  – firewall rules for the EC2 instance
#   2. AWS EC2 Instance    – Ubuntu server that runs Minikube/K3s
#
# Prerequisites:
#   - AWS CLI configured (`aws configure`) or credentials in env vars
#   - An existing EC2 Key Pair (set var.key_pair_name)
#   - Terraform >= 1.5 installed
#
# Usage:
#   terraform init
#   terraform plan -var="key_pair_name=my-key"
#   terraform apply -var="key_pair_name=my-key"
# ─────────────────────────────────────────────────────────────────────────────


# ── Terraform Settings ────────────────────────────────────────────────────────
terraform {
  required_version = ">= 1.5.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"   # Permissive patch/minor upgrades; locks major version
    }
  }

  # ── Remote State (optional but recommended for teams) ────────────────────
  # Uncomment and configure to store tfstate in S3 instead of locally.
  # backend "s3" {
  #   bucket         = "my-terraform-state-bucket"
  #   key            = "ecommerce-devops/terraform.tfstate"
  #   region         = "us-east-1"
  #   encrypt        = true
  #   dynamodb_table = "terraform-lock"
  # }
}


# ── Provider Configuration ────────────────────────────────────────────────────
# Terraform uses the AWS provider to interact with the AWS API.
provider "aws" {
  region = var.aws_region

  # Tag every resource created by this provider with project metadata.
  # This enables cost tracking and resource grouping in the AWS Console.
  default_tags {
    tags = {
      Project     = var.project_name
      Environment = var.environment
      ManagedBy   = "Terraform"
    }
  }
}


# ── Security Group ────────────────────────────────────────────────────────────
# A Security Group acts as a virtual firewall for the EC2 instance.
# It controls which ports accept inbound (ingress) traffic and which
# outbound (egress) connections are allowed.
resource "aws_security_group" "k8s_host_sg" {
  name        = "${var.project_name}-k8s-host-sg"
  description = "Security group for the Minikube/K3s host EC2 instance"

  # ── Inbound Rules (ingress) ───────────────────────────────────────────────

  # SSH (port 22): required to connect and manage the server.
  # In a production environment restrict cidr_blocks to your office/VPN IP.
  ingress {
    description = "SSH access"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]   # Restrict to your IP in production!
  }

  # HTTP (port 80): for exposing Kubernetes services via a NodePort or ingress.
  ingress {
    description = "HTTP traffic"
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # HTTPS (port 443): for TLS-terminated traffic (cert-manager / Let's Encrypt).
  ingress {
    description = "HTTPS traffic"
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # ── Outbound Rules (egress) ───────────────────────────────────────────────
  # Allow all outbound traffic so the server can pull Docker images,
  # install packages, and communicate with the Kubernetes API.
  egress {
    description = "Allow all outbound traffic"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"             # -1 means all protocols
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "${var.project_name}-sg"
  }
}


# ── EC2 Instance ──────────────────────────────────────────────────────────────
# This Ubuntu server will have Minikube (or K3s) installed on it via the
# user_data bootstrap script below.
resource "aws_instance" "k8s_host" {
  ami           = var.ami_id
  instance_type = var.instance_type   # t3.medium: 2 vCPU, 4 GiB RAM

  key_name               = var.key_pair_name
  vpc_security_group_ids = [aws_security_group.k8s_host_sg.id]

  # Give the instance a public IP so you can SSH to it directly.
  # For a private-subnet setup, use a bastion or AWS Systems Manager.
  associate_public_ip_address = true

  # ── Root Volume ───────────────────────────────────────────────────────────
  # 30 GiB is the minimum comfortable size for Docker images + K8s overhead.
  root_block_device {
    volume_type           = "gp3"   # gp3 is cheaper and faster than gp2
    volume_size           = 30      # GiB
    delete_on_termination = true    # Clean up EBS volume when instance terminates
    encrypted             = true    # Encrypt at rest (security best practice)
  }

  # ── User Data Bootstrap Script ────────────────────────────────────────────
  # This shell script runs once as root when the instance first boots.
  # It installs Docker and K3s (a lightweight Kubernetes distribution).
  # K3s is easier to set up than Minikube on a headless server.
  user_data = <<-EOF
    #!/bin/bash
    set -euo pipefail

    # ── System Update ────────────────────────────────────────────────────────
    apt-get update -y
    apt-get upgrade -y

    # ── Install Docker ───────────────────────────────────────────────────────
    # Docker is used by K3s as the container runtime.
    apt-get install -y docker.io curl git
    systemctl enable docker
    systemctl start docker

    # ── Install K3s (lightweight Kubernetes) ─────────────────────────────────
    # K3s sets up a single-node cluster automatically.
    # INSTALL_K3S_EXEC flags disable the local load balancer (we use NodePort).
    curl -sfL https://get.k3s.io | INSTALL_K3S_EXEC="--docker" sh -

    # ── Export kubeconfig for the ubuntu user ─────────────────────────────
    mkdir -p /home/ubuntu/.kube
    cp /etc/rancher/k3s/k3s.yaml /home/ubuntu/.kube/config
    chown ubuntu:ubuntu /home/ubuntu/.kube/config
    echo 'export KUBECONFIG=/home/ubuntu/.kube/config' >> /home/ubuntu/.bashrc

    echo "Bootstrap complete — K3s cluster is ready."
  EOF

  tags = {
    Name = "${var.project_name}-k8s-host"
  }
}


# ── Outputs ───────────────────────────────────────────────────────────────────
# Outputs are printed after `terraform apply` and can be consumed by other
# Terraform modules or CI/CD pipelines.

output "instance_public_ip" {
  description = "Public IP of the K3s host — use this to SSH: ssh ubuntu@<ip>"
  value       = aws_instance.k8s_host.public_ip
}

output "instance_id" {
  description = "EC2 Instance ID (useful for AWS CLI commands)"
  value       = aws_instance.k8s_host.id
}

output "ssh_command" {
  description = "Ready-to-use SSH command"
  value       = "ssh -i ~/.ssh/${var.key_pair_name}.pem ubuntu@${aws_instance.k8s_host.public_ip}"
}
