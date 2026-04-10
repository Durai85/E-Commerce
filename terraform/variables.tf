# ── terraform/variables.tf ────────────────────────────────────────────────────
# Input variable declarations for the e-commerce infrastructure.
# Values are supplied via:
#   - terraform.tfvars file (local dev, gitignored)
#   - -var flags on the CLI
#   - TF_VAR_<name> environment variables (recommended for CI/CD)
# ─────────────────────────────────────────────────────────────────────────────

# ── AWS Region ────────────────────────────────────────────────────────────────
variable "aws_region" {
  description = "AWS region where all resources will be deployed."
  type        = string
  default     = "us-east-1"
}

# ── EC2 Instance Type ─────────────────────────────────────────────────────────
variable "instance_type" {
  description = "EC2 instance type for the Minikube/K3s host node."
  type        = string
  default     = "t3.medium"   # 2 vCPU, 4 GiB RAM — minimum for Minikube
}

# ── AMI ───────────────────────────────────────────────────────────────────────
variable "ami_id" {
  description = "Ubuntu 22.04 LTS AMI ID (region-specific)."
  type        = string
  # Default: Ubuntu 22.04 LTS in us-east-1 (update if region changes)
  default     = "ami-0c7217cdde317cfec"
}

# ── SSH Key Pair ──────────────────────────────────────────────────────────────
variable "key_pair_name" {
  description = "Name of the AWS EC2 key pair for SSH access. Must already exist in AWS."
  type        = string
  # No default — must be supplied to avoid accidental lockout.
}

# ── Project Tag ───────────────────────────────────────────────────────────────
variable "project_name" {
  description = "Tag applied to all resources for cost allocation and filtering."
  type        = string
  default     = "ecommerce-devops"
}

# ── Environment Tag ───────────────────────────────────────────────────────────
variable "environment" {
  description = "Deployment environment label (dev / staging / prod)."
  type        = string
  default     = "dev"
}
