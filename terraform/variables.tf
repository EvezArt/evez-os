# ---------------------------------------------------------------------------
# variables.tf — EVEZ Mesh configurable parameters
# ---------------------------------------------------------------------------

variable "project_id" {
  description = "GCP project ID"
  type        = string
  default     = "evez-mesh-prod"
}

variable "region" {
  description = "Primary GCP region"
  type        = string
  default     = "us-west1"
}

variable "region_secondary" {
  description = "Secondary GCP region"
  type        = string
  default     = "us-central1"
}

variable "zone_primary" {
  description = "Primary zone"
  type        = string
  default     = "us-west1-a"
}

variable "zone_secondary" {
  description = "Secondary zone"
  type        = string
  default     = "us-central1-a"
}

# ---------- Networking ----------

variable "vpc_cidr" {
  description = "Primary VPC CIDR"
  type        = string
  default     = "10.128.0.0/20"
}

variable "subnet_primary_cidr" {
  description = "Primary subnet CIDR (us-west1)"
  type        = string
  default     = "10.128.0.0/24"
}

variable "subnet_secondary_cidr" {
  description = "Secondary subnet CIDR (us-central1)"
  type        = string
  default     = "10.128.1.0/24"
}

variable "vpc_secondary_cidr" {
  description = "Secondary VPC CIDR (for peering)"
  type        = string
  default     = "10.129.0.0/20"
}

# ---------- Instances ----------

variable "machine_type_small" {
  description = "Machine type for worker nodes"
  type        = string
  default     = "e2-medium"
}

variable "machine_type_controller" {
  description = "Machine type for controller node"
  type        = string
  default     = "e2-standard-2"
}

variable "machine_type_free" {
  description = "Machine type for free-tier node"
  type        = string
  default     = "e2-micro"
}

variable "instance_count_small" {
  description = "Number of e2-medium worker nodes"
  type        = number
  default     = 3
}

# ---------- Vultr ----------

variable "vultr_api_key" {
  description = "Vultr API key for primary node"
  type        = string
  sensitive   = true
  default     = ""

  # CI/CD: Set via VULTR_API_KEY environment variable
  # Terraform will auto-detect TF_VAR_vultr_api_key
}

variable "vultr_primary_ip" {
  description = "Public IP of the Vultr primary node"
  type        = string
  default     = "149.28.134.51"
}

# ---------- DNS ----------

variable "dns_zone" {
  description = "DNS zone domain"
  type        = string
  default     = "evez-os.ai"
}

variable "dns_zone_name" {
  description = "Cloud DNS zone resource name"
  type        = string
  default     = "evez-os-ai"
}

# ---------- EVEZ Services ----------

variable "evez_ports" {
  description = "EVEZ microservice ports (9111-9117)"
  type        = list(number)
  default     = [9111, 9112, 9113, 9114, 9115, 9116, 9117]
}

variable "evez_service_names" {
  description = "EVEZ microservice names indexed to ports 9111-9117"
  type        = list(string)
  default     = [
    "consciousness",    # 9111
    "desire",           # 9112
    "world-model",      # 9113
    "planner",          # 9114
    "inner-voice",      # 9115
    "self-modify",      # 9116
    "agency",           # 9117
  ]
}

# ---------- SSH ----------

variable "ssh_public_key" {
  description = "SSH public key for instance access"
  type        = string
  default     = "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIOPENCLAW-EVEZ-MESH evez@mesh"
}

variable "ssh_user" {
  description = "SSH username"
  type        = string
  default     = "evez"
}

# ---------- Monitoring ----------

variable "alert_email" {
  description = "Email for alert notifications"
  type        = string
  default     = "ops@evez-os.ai"
}

variable "uptime_check_period" {
  description = "Uptime check interval in seconds"
  type        = string
  default     = "60"
}

# ---------- Labels ----------

variable "labels" {
  description = "Common resource labels"
  type        = map(string)
  default     = {
    managed_by = "terraform"
    mesh       = "evez"
    env        = "prod"
  }
}
