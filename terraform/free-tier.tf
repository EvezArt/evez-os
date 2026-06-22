# ---------------------------------------------------------------------------
# free-tier.tf — Always-free tier resources (1 e2-micro, GCS, Pub/Sub, Scheduler)
# ---------------------------------------------------------------------------

# ---------- Free-Tier Instance (e2-micro in us-west1) ----------

resource "google_compute_instance" "free_tier" {
  name         = "evez-free-tier"
  machine_type = var.machine_type_free
  zone         = var.zone_primary

  tags = ["evez-node", "evez-free-tier"]

  labels = merge(var.labels, {
    role = "free-tier"
    tier = "free"
  })

  boot_disk {
    initialize_params {
      image = "debian-cloud/debian-12"
      size   = 30   # free tier allows up to 30 GB standard PD
      type   = "pd-standard"
    }
  }

  network_interface {
    subnetwork = google_compute_subnetwork.primary.id
    stack_type = "IPV4_ONLY"

    # No external IP — use Cloud NAT for egress; or enable for direct access
    access_config {
      network_tier = "STANDARD"
    }
  }

  service_account {
    email  = google_service_account.evez_node.email
    scopes = ["cloud-platform"]
  }

  metadata = {
    ssh-keys       = "${var.ssh_user}:${var.ssh_public_key} ${var.ssh_user}"
    enable-oslogin = "TRUE"
  }

  metadata_startup_script = <<-SCRIPT
    #!/bin/bash
    set -euo pipefail
    apt-get update && apt-get install -y curl wget git jq
    curl -fsSL https://deb.nodesource.com/setup_22.x | bash -
    apt-get install -y nodejs
    npm install -g openclaw@latest
    openclaw init --non-interactive
    echo "EVEZ free-tier node ready" > /tmp/evez-ready
  SCRIPT

  depends_on = [
    google_compute_subnetwork.primary,
    google_service_account.evez_node,
  ]
}

# ---------- Free Cloud Storage Bucket (5 GB US, multi-regional) ----------

resource "google_storage_bucket" "evez_artifacts" {
  name          = "${var.project_id}-artifacts"
  location      = "US"
  force_destroy = false

  uniform_bucket_level_access = true

  versioning {
    enabled = true
  }

  lifecycle_rule {
    condition {
      age = 365
    }
    action {
      type = "SetStorageClass"
      storage_class = "COLDLINE"
    }
  }

  cors {
    origin          = ["https://evez-os.ai"]
    method          = ["GET", "HEAD"]
    response_header = ["Content-Type", "Access-Control-Allow-Origin"]
    max_age_seconds = 3600
  }

  labels = var.labels
}

resource "google_storage_bucket_iam_binding" "evez_artifacts_viewer" {
  bucket = google_storage_bucket.evez_artifacts.name
  role   = "roles/storage.objectViewer"

  members = [
    "serviceAccount:${google_service_account.evez_node.email}",
  ]
}

# ---------- Pub/Sub Topic ----------

resource "google_pubsub_topic" "evez_events" {
  name = "evez-mesh-events"

  message_retention_duration = "86400s"  # 1 day (free tier friendly)

  labels = var.labels
}

resource "google_pubsub_subscription" "evez_events_sub" {
  name  = "evez-mesh-events-sub"
  topic = google_pubsub_topic.evez_events.name

  ack_deadline_seconds = 30

  message_retention_duration = "604800s"  # 7 days

  retry_policy {
    minimum_backoff = "10s"
    maximum_backoff = "600s"
  }
}

# ---------- Cloud Scheduler Jobs ----------

resource "google_cloud_scheduler_job" "health_ping" {
  name             = "evez-health-ping"
  region           = var.region
  description      = "Ping EVEZ health endpoint every 5 minutes"
  schedule         = "*/5 * * * *"
  time_zone        = "America/New_York"
  attempt_deadline = "300s"

  pubsub_target {
    topic_name = google_pubsub_topic.evez_events.id
    data       = base64encode(jsonencode({
      type    = "health_ping"
      source  = "scheduler"
      targets = ["9111", "9112", "9113", "9114", "9115", "9116", "9117"]
    }))
  }
}

resource "google_cloud_scheduler_job" "memory_gc" {
  name             = "evez-memory-gc"
  region           = var.region
  description      = "Trigger memory garbage collection hourly"
  schedule         = "0 * * * *"
  time_zone        = "America/New_York"
  attempt_deadline = "300s"

  pubsub_target {
    topic_name = google_pubsub_topic.evez_events.id
    data       = base64encode(jsonencode({
      type   = "memory_gc"
      source = "scheduler"
    }))
  }
}

resource "google_cloud_scheduler_job" "sync_check" {
  name             = "evez-sync-check"
  region           = var.region
  description      = "Check mesh synchronization every 15 minutes"
  schedule         = "*/15 * * * *"
  time_zone        = "America/New_York"
  attempt_deadline = "300s"

  pubsub_target {
    topic_name = google_pubsub_topic.evez_events.id
    data       = base64encode(jsonencode({
      type   = "sync_check"
      source = "scheduler"
    }))
  }
}
