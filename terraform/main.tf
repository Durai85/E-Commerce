# ── Terraform — Infrastructure as Code ─────────────────────────────
# Instead of manually clicking through the AWS Console to create a
# server, we *describe* the infrastructure we want in code.
# Running `terraform apply` makes Terraform create it all for us.
#
# Key Concepts:
# - Provider: tells Terraform which cloud to talk to (AWS here).
# - Resource: a thing Terraform creates (VPC, subnet, EC2 instance).
# - user_data: a startup script that runs once when the EC2 boots.
# - Security Group: a virtual firewall — we MUST open the right
#   ports or nothing can reach our server.

terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
  required_version = ">= 1.0"
}

# ── AWS Provider ───────────────────────────────────────────────────
provider "aws" {
  region = var.aws_region
}

# ── VPC (Virtual Private Cloud) ───────────────────────────────────
# A VPC is your own isolated network inside AWS.
resource "aws_vpc" "main" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_hostnames = true
  enable_dns_support   = true

  tags = {
    Name = "ecommerce-vpc"
  }
}

# ── Public Subnet ─────────────────────────────────────────────────
# A subnet is a range of IPs within your VPC. "Public" means
# instances here can get a public IP and be reached from the internet.
resource "aws_subnet" "public" {
  vpc_id                  = aws_vpc.main.id
  cidr_block              = "10.0.1.0/24"
  map_public_ip_on_launch = true
  availability_zone       = "${var.aws_region}a"

  tags = {
    Name = "ecommerce-public-subnet"
  }
}

# ── Internet Gateway ──────────────────────────────────────────────
# Connects your VPC to the public internet.
resource "aws_internet_gateway" "igw" {
  vpc_id = aws_vpc.main.id

  tags = {
    Name = "ecommerce-igw"
  }
}

# ── Route Table ────────────────────────────────────────────────────
# Tells traffic where to go. 0.0.0.0/0 = "all internet traffic"
# goes through the Internet Gateway.
resource "aws_route_table" "public" {
  vpc_id = aws_vpc.main.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.igw.id
  }

  tags = {
    Name = "ecommerce-public-rt"
  }
}

resource "aws_route_table_association" "public" {
  subnet_id      = aws_subnet.public.id
  route_table_id = aws_route_table.public.id
}

# ── Security Group (Firewall Rules) ───────────────────────────────
resource "aws_security_group" "k8s_sg" {
  name        = "ecommerce-k8s-sg"
  description = "Allow SSH, HTTP, K8s API, and NodePort traffic"
  vpc_id      = aws_vpc.main.id

  # SSH access
  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # HTTP
  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # Kubernetes API server
  ingress {
    from_port   = 6443
    to_port     = 6443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # Kubernetes NodePort range — this is how we access our services
  ingress {
    from_port   = 30000
    to_port     = 32767
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # Allow all outbound traffic
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "ecommerce-k8s-sg"
  }
}

# ── EC2 Instance ──────────────────────────────────────────────────
# This is the virtual server where Kubernetes will run.
resource "aws_instance" "k8s_server" {
  ami                    = var.ami_id
  instance_type          = var.instance_type
  key_name               = var.key_pair_name
  subnet_id              = aws_subnet.public.id
  vpc_security_group_ids = [aws_security_group.k8s_sg.id]

  # user_data = a bash script that runs when the instance first boots.
  # We use it to install Docker and Minikube automatically.
  user_data = <<-EOF
              #!/bin/bash
              set -e

              # Update system packages
              apt-get update -y
              apt-get upgrade -y

              # Install Docker
              apt-get install -y docker.io curl
              systemctl enable docker
              systemctl start docker
              usermod -aG docker ubuntu

              # Install kubectl
              curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
              install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl

              # Install Minikube
              curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64
              install minikube-linux-amd64 /usr/local/bin/minikube

              # Start Minikube as the ubuntu user
              su - ubuntu -c "minikube start --driver=docker"
              EOF

  root_block_device {
    volume_size = 20
    volume_type = "gp3"
  }

  tags = {
    Name = "ecommerce-k8s-server"
  }
}
