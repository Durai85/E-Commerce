# ── Variables ──────────────────────────────────────────────────────
# Variables make your Terraform config reusable. Instead of hardcoding
# values, you define them here and can override them per environment.

variable "aws_region" {
  description = "AWS region to deploy into"
  type        = string
  default     = "us-east-1"
}

variable "instance_type" {
  description = "EC2 instance type (t2.medium+ recommended for Minikube)"
  type        = string
  default     = "t2.medium"
}

variable "key_pair_name" {
  description = "Name of the SSH key pair (must already exist in AWS)"
  type        = string
  default     = "ecommerce-key"
}

variable "ami_id" {
  description = "AMI ID for Ubuntu 22.04 (region-specific)"
  type        = string
  default     = "ami-0c7217cdde317cfec"  # Ubuntu 22.04 LTS in us-east-1
}
