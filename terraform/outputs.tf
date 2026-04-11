# ── Outputs ────────────────────────────────────────────────────────
# After `terraform apply`, these values are printed to the terminal.
# The public IP is what you'll SSH into or point your browser at.

output "instance_public_ip" {
  description = "Public IP of the Kubernetes server"
  value       = aws_instance.k8s_server.public_ip
}

output "instance_id" {
  description = "EC2 Instance ID"
  value       = aws_instance.k8s_server.id
}

output "ssh_command" {
  description = "SSH command to connect to the server"
  value       = "ssh -i ~/.ssh/${var.key_pair_name}.pem ubuntu@${aws_instance.k8s_server.public_ip}"
}
