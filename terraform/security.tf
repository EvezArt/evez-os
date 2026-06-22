# ---------------------------------------------------------------------------
# security.tf — IAM, service accounts, OS Login, VPC Service Controls
# ---------------------------------------------------------------------------

# ---------- Service Account for monitoring ----------

resource "google_service_account" "evez_monitor" {
  account_id   = "evez-monitor-sa"
  display_name = "EVEZ Monitoring Service Account"
  description  = "Used by monitoring and logging components"
}

# ---------- Service Account IAM Bindings ----------

resource "google_project_iam_binding" "evez_node_roles" {
  for_each = toset([
    "roles/logging.logWriter",
    "roles/logging.viewer",
    "roles/monitoring.metricWriter",
    "roles/monitoring.viewer",
    "roles/stackdriver.resourceMetadata.writer",
    "roles/storage.objectViewer",
    "roles/pubsub.publisher",
    "roles/compute.networkViewer",
  ])

  role = each.value

  members = [
    "serviceAccount:${google_service_account.evez_node.email}",
  ]
}

resource "google_project_iam_binding" "evez_monitor_roles" {
  for_each = toset([
    "roles/monitoring.admin",
    "roles/logging.viewer",
    "roles/pubsub.subscriber",
  ])

  role = each.value

  members = [
    "serviceAccount:${google_service_account.evez_monitor.email}",
  ]
}

# ---------- OS Login IAM ----------

resource "google_project_iam_binding" "os_login" {
  role = "roles/compute.osLogin"

  members = [
    "serviceAccount:${google_service_account.evez_node.email}",
    "user:${var.alert_email}",
  ]
}

resource "google_project_iam_binding" "os_admin_login" {
  role = "roles/compute.osAdminLogin"

  members = [
    "user:${var.alert_email}",
  ]
}

# ---------- Organization Policy: Require OS Login ----------

resource "google_compute_project_metadata_item" "os_login_enabled" {
  key   = "enable-oslogin"
  value = "TRUE"
}

# ---------- VPC Service Controls ----------

resource "google_access_context_manager_access_policy" "evez_policy" {
  parent = "organizations/${data.google_project.project.number}"
  title  = "EVEZ Mesh Access Policy"
}

resource "google_access_context_manager_service_perimeter" "evez_perimeter" {
  parent         = google_access_context_manager_access_policy.evez_policy.name
  name           = "evez_mesh_perimeter"
  perimeter_type = "PERIMETER_TYPE_REGULAR"
  title          = "EVEZ Mesh Service Perimeter"

  spec {
    restricted_services {
      service = "storage.googleapis.com"
    }
    restricted_services {
      service = "pubsub.googleapis.com"
    }
    restricted_services {
      service = "logging.googleapis.com"
    }
    restricted_services {
      service = "monitoring.googleapis.com"
    }

    ingress_policies {
      ingress_from {
        identity_type = "ANY_SERVICE_ACCOUNT"
        sources {
          access_level = google_access_context_manager_access_level.evez_trusted.name
        }
      }
      ingress_to {
        resources = ["*"]
      }
    }

    egress_policies {
      egress_to {
        resources = ["*"]
      }
      egress_from {
        identity_type = "ANY_SERVICE_ACCOUNT"
      }
    }
  }

  # Bridge to allow perimeter resources to talk to each other
  use_explicit_dry_run_spec = false
}

resource "google_access_context_manager_access_level" "evez_trusted" {
  parent = google_access_context_manager_access_policy.evez_policy.name
  name   = "evez_trusted_level"
  title  = "EVEZ Trusted Network"

  basic {
    conditions {
      ip_subnetworks = [
        var.subnet_primary_cidr,
        var.subnet_secondary_cidr,
        "${var.vultr_primary_ip}/32",
      ]
    }
    combining_function = "AND"
  }
}

# ---------- Firewall: deny all egress by default (explicit allow via NAT only) ----------

resource "google_compute_firewall" "deny_egress_default" {
  name      = "evez-deny-egress-default"
  network   = google_compute_network.evez_primary.name
  priority  = 65534
  direction = "EGRESS"

  deny {
    protocol = "all"
  }

  destination_ranges = ["0.0.0.0/0"]

  target_tags = ["evez-node"]
}

# ---------- IAM audit logging ----------

resource "google_project_audit_config" "evez_audit" {
  project = var.project_id

  service = "allServices"

  audit_log_config {
    log_type = "ADMIN_READ"
  }
  audit_log_config {
    log_type = "DATA_READ"
  }
  audit_log_config {
    log_type = "DATA_WRITE"
  }
}
