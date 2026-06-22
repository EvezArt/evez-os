# ---------------------------------------------------------------------------
# vpc.tf — VPC, subnets, Cloud NAT, VPC peering, firewall rules
# ---------------------------------------------------------------------------

# ---------- Primary VPC ----------

resource "google_compute_network" "evez_primary" {
  name                            = "evez-mesh-vpc"
  auto_create_subnetworks         = false
  routing_mode                    = "GLOBAL"
  mtu                             = 1460
  enable_ula_internal_ipv6        = false

  delete_default_routes_on_create = true
}

resource "google_compute_subnetwork" "primary" {
  name          = "evez-subnet-us-west1"
  network       = google_compute_network.evez_primary.id
  region        = var.region
  ip_cidr_range = var.subnet_primary_cidr

  secondary_ip_range {
    range_name    = "evez-pods"
    ip_cidr_range = "10.128.8.0/22"
  }

  secondary_ip_range {
    range_name    = "evez-services"
    ip_cidr_range = "10.128.12.0/24"
  }

  private_ip_google_access = true
  log_config {
    aggregation_interval = "INTERVAL_5_SEC"
    flow_sampling        = 0.5
    metadata             = "INCLUDE_ALL_METADATA"
  }
}

resource "google_compute_subnetwork" "secondary" {
  name          = "evez-subnet-us-central1"
  network       = google_compute_network.evez_primary.id
  region        = var.region_secondary
  ip_cidr_range = var.subnet_secondary_cidr

  secondary_ip_range {
    range_name    = "evez-pods-secondary"
    ip_cidr_range = "10.129.0.0/22"
  }

  private_ip_google_access = true
}

# ---------- Secondary VPC (peering target) ----------

resource "google_compute_network" "evez_secondary" {
  name                    = "evez-mesh-vpc-secondary"
  auto_create_subnetworks = false
  routing_mode            = "GLOBAL"

  delete_default_routes_on_create = true
}

resource "google_compute_subnetwork" "secondary_vpc_subnet" {
  name          = "evez-secondary-subnet"
  network       = google_compute_network.evez_secondary.id
  region        = var.region_secondary
  ip_cidr_range = var.vpc_secondary_cidr

  private_ip_google_access = true
}

# ---------- VPC Peering ----------

resource "google_compute_network_peering" "primary_to_secondary" {
  name         = "evez-primary-to-secondary"
  network      = google_compute_network.evez_primary.id
  peer_network = google_compute_network.evez_secondary.id

  export_custom_routes = true
  import_custom_routes = true
}

resource "google_compute_network_peering" "secondary_to_primary" {
  name         = "evez-secondary-to-primary"
  network      = google_compute_network.evez_secondary.id
  peer_network = google_compute_network.evez_primary.id

  export_custom_routes = true
  import_custom_routes = true
}

# ---------- Cloud Router + NAT ----------

resource "google_compute_router" "evez_router" {
  name    = "evez-cloud-router"
  network = google_compute_network.evez_primary.id
  region  = var.region

  bgp {
    asn = 64514
  }
}

resource "google_compute_router_nat" "evez_nat" {
  name                               = "evez-cloud-nat"
  router                             = google_compute_router.evez_router.name
  region                             = var.region
  nat_ip_allocate_option             = "AUTO_ONLY"
  source_subnetwork_ip_ranges_to_nat = "LIST_OF_SUBNETWORKS"

  subnetwork {
    name                    = google_compute_subnetwork.primary.name
    source_ip_ranges_to_nat = ["ALL_IP_RANGES"]
  }

  log_config {
    enable = true
    filter = "ERRORS_ONLY"
  }
}

resource "google_compute_router" "evez_router_secondary" {
  name    = "evez-cloud-router-secondary"
  network = google_compute_network.evez_primary.id
  region  = var.region_secondary

  bgp {
    asn = 64515
  }
}

resource "google_compute_router_nat" "evez_nat_secondary" {
  name                               = "evez-cloud-nat-secondary"
  router                             = google_compute_router.evez_router_secondary.name
  region                             = var.region_secondary
  nat_ip_allocate_option             = "AUTO_ONLY"
  source_subnetwork_ip_ranges_to_nat = "LIST_OF_SUBNETWORKS"

  subnetwork {
    name                    = google_compute_subnetwork.secondary.name
    source_ip_ranges_to_nat = ["ALL_IP_RANGES"]
  }
}

# ---------- Firewall Rules ----------

# SSH from internal VPC only
resource "google_compute_firewall" "ssh_internal" {
  name    = "evez-allow-ssh-internal"
  network = google_compute_network.evez_primary.name

  allow {
    protocol = "tcp"
    ports    = ["22"]
  }

  source_ranges = [
    var.subnet_primary_cidr,
    var.subnet_secondary_cidr,
    var.vpc_secondary_cidr,
  ]

  target_tags = ["evez-node"]
}

# OpenClaw API internal (port 8443)
resource "google_compute_firewall" "openclaw_api_internal" {
  name    = "evez-allow-openclaw-api-internal"
  network = google_compute_network.evez_primary.name

  allow {
    protocol = "tcp"
    ports    = ["8443"]
  }

  source_ranges = [
    var.subnet_primary_cidr,
    var.subnet_secondary_cidr,
    var.vpc_secondary_cidr,
  ]

  target_tags = ["evez-node"]
}

# EVEZ microservice ports (9111-9117) internal
resource "google_compute_firewall" "evez_services_internal" {
  name    = "evez-allow-services-internal"
  network = google_compute_network.evez_primary.name

  dynamic "allow" {
    for_each = var.evez_ports
    content {
      protocol = "tcp"
      ports    = [tostring(allow.value)]
    }
  }

  source_ranges = [
    var.subnet_primary_cidr,
    var.subnet_secondary_cidr,
    var.vpc_secondary_cidr,
  ]

  target_tags = ["evez-node"]
}

# EVEZ services from Vultr primary node
resource "google_compute_firewall" "evez_services_vultr" {
  name    = "evez-allow-services-vultr"
  network = google_compute_network.evez_primary.name

  dynamic "allow" {
    for_each = var.evez_ports
    content {
      protocol = "tcp"
      ports    = [tostring(allow.value)]
    }
  }

  source_ranges = ["${var.vultr_primary_ip}/32"]

  target_tags = ["evez-node"]
}

# Health checks from Google probing ranges
resource "google_compute_firewall" "health_checks" {
  name    = "evez-allow-health-checks"
  network = google_compute_network.evez_primary.name

  allow {
    protocol = "tcp"
    ports    = ["9111", "9112", "9113", "9114", "9115", "9116", "9117"]
  }

  source_ranges = [
    "35.191.0.0/16",
    "130.211.0.0/22",
    "209.85.152.0/22",
    "209.85.204.0/22",
  ]

  target_tags = ["evez-node"]
}

# IAP tunnel access (35.235.240.0/20)
resource "google_compute_firewall" "iap_tunnel" {
  name    = "evez-allow-iap-tunnel"
  network = google_compute_network.evez_primary.name

  allow {
    protocol = "tcp"
    ports    = ["22"]
  }

  source_ranges = ["35.235.240.0/20"]

  target_tags = ["evez-node"]
}

# ICMP internal
resource "google_compute_firewall" "icmp_internal" {
  name    = "evez-allow-icmp-internal"
  network = google_compute_network.evez_primary.name

  allow {
    protocol = "icmp"
  }

  source_ranges = [
    var.subnet_primary_cidr,
    var.subnet_secondary_cidr,
    var.vpc_secondary_cidr,
  ]

  target_tags = ["evez-node"]
}

# Deny all other ingress (lowest priority)
resource "google_compute_firewall" "deny_all" {
  name       = "evez-deny-all-ingress"
  network    = google_compute_network.evez_primary.name
  priority   = 65534
  direction  = "INGRESS"

  deny {
    protocol = "all"
  }

  source_ranges = ["0.0.0.0/0"]

  target_tags = ["evez-node"]
}
