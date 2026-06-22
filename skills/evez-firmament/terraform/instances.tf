# ---------------------------------------------------------------------------
# instances.tf — 4 GCP instances with OpenClaw startup scripts
# ---------------------------------------------------------------------------

# ---------- Service Account ----------

resource "google_service_account" "evez_node" {
  account_id   = "evez-node-sa"
  display_name = "EVEZ Mesh Node Service Account"
  description  = "Used by all EVEZ mesh compute instances"
}

# ---------- SSH Key in metadata ----------

resource "google_compute_project_metadata_item" "ssh_key" {
  key   = "ssh-keys"
  value = "${var.ssh_user}:${var.ssh_public_key} ${var.ssh_user}"
}

# ---------- Startup Script (shared) ----------

locals {
  openclaw_startup_script = <<-SCRIPT
    #!/bin/bash
    set -euo pipefail

    # --- System prep ---
    apt-get update && apt-get upgrade -y
    apt-get install -y curl wget git jq unzip net-tools

    # --- Install Node.js 22 ---
    curl -fsSL https://deb.nodesource.com/setup_22.x | bash -
    apt-get install -y nodejs

    # --- Install OpenClaw ---
    npm install -g openclaw@latest

    # --- Initialize OpenClaw ---
    openclaw init --non-interactive

    # --- Enable EVEZ service ports ---
    for port in 9111 9112 9113 9114 9115 9116 9117; do
      iptables -A INPUT -p tcp --dport $port -j ACCEPT
    done

    # --- Start OpenClaw gateway ---
    systemctl enable openclaw-gateway || true
    openclaw gateway start --detach || true

    # --- Report ready ---
    echo "EVEZ OpenClaw node ready at $(hostname -I | awk '{print $1}')" > /tmp/evez-ready
  SCRIPT
}

# ---------- Controller Node (e2-standard-2) ----------

resource "google_compute_instance" "controller" {
  name         = "evez-controller"
  machine_type = var.machine_type_controller
  zone         = var.zone_primary

  tags = ["evez-node", "evez-controller"]

  labels = merge(var.labels, {
    role = "controller"
  })

  boot_disk {
    initialize_params {
      image = "debian-cloud/debian-12"
      size   = 50
      type   = "pd-balanced"
    }
  }

  network_interface {
    subnetwork = google_compute_subnetwork.primary.id
    stack_type = "IPV4_ONLY"

    access_config {
      network_tier = "PREMIUM"
    }
  }

  service_account {
    email  = google_service_account.evez_node.email
    scopes = ["cloud-platform"]
  }

  metadata = {
    ssh-keys        = "${var.ssh_user}:${var.ssh_public_key} ${var.ssh_user}"
    enable-oslogin  = "TRUE"
    startup-script  = local.openclaw_startup_script
  }

  metadata_startup_script = local.openclaw_startup_script

  depends_on = [
    google_compute_subnetwork.primary,
    google_service_account.evez_node,
  ]
}

# ---------- Worker Nodes (e2-medium × 3) ----------

resource "google_compute_instance" "worker" {
  count        = var.instance_count_small
  name         = "evez-worker-${count.index}"
  machine_type = var.machine_type_small
  zone         = count.index < 2 ? var.zone_primary : var.zone_secondary

  tags = ["evez-node", "evez-worker"]

  labels = merge(var.labels, {
    role = "worker"
    idx  = tostring(count.index)
  })

  boot_disk {
    initialize_params {
      image = "debian-cloud/debian-12"
      size   = 30
      type   = "pd-balanced"
    }
  }

  network_interface {
    subnetwork = count.index < 2 ? google_compute_subnetwork.primary.id : google_compute_subnetwork.secondary.id
    stack_type = "IPV4_ONLY"

    access_config {
      network_tier = "PREMIUM"
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

  metadata_startup_script = local.openclaw_startup_script

  depends_on = [
    google_compute_subnetwork.primary,
    google_compute_subnetwork.secondary,
    google_service_account.evez_node,
  ]
}
