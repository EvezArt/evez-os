# ---------------------------------------------------------------------------
# main.tf — Provider config, backend, data sources
# ---------------------------------------------------------------------------

terraform {
  required_version = ">= 1.7"

  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.40"
    }
    vultr = {
      source  = "vultr/vultr"
      version = "~> 2.20"
    }
  }

  # Backend configured dynamically via -backend-config in CI/CD.
  # For local dev:
  #   terraform init -backend-config="bucket=evez-mesh-terraform-state"
  # For CI/CD:
  #   terraform init -backend-config="bucket=${GCP_PROJECT_ID}-terraform-state" -backend-config="prefix=terraform/state"
  backend "gcs" {
    bucket = "evez-mesh-terraform-state"
    prefix = "terraform/state"
  }
}

# ---------- Google Provider ----------
# CI/CD: Set GOOGLE_APPLICATION_CREDENTIALS env var to service account key JSON path
# Local:  Use `gcloud auth application-default login`

provider "google" {
  project = var.project_id
  region  = var.region
  zone    = var.zone_primary

  default_labels = var.labels
}

provider "google-beta" {
  project = var.project_id
  region  = var.region
  zone    = var.zone_primary
}

# ---------- Vultr Provider ----------

provider "vultr" {
  api_key = var.vultr_api_key
}

# ---------- Data Sources ----------

data "google_client_config" "current" {}

data "google_compute_zones" "available_primary" {
  region = var.region
}

data "google_compute_zones" "available_secondary" {
  region = var.region_secondary
}

data "google_project" "project" {
  project_id = var.project_id
}
