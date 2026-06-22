# ---------------------------------------------------------------------------
# dns.tf — Cloud DNS zone for evez-os.ai, A records for all nodes
# ---------------------------------------------------------------------------

resource "google_dns_managed_zone" "evez_zone" {
  name        = var.dns_zone_name
  dns_name    = "${var.dns_zone}."
  description = "EVEZ Mesh DNS zone for ${var.dns_zone}"

  visibility = "public"

  dnssec_config {
    state         = "on"
    non_existence = "nsec3"
    default_kind  = "dnssec-ds"

    kind = "dns#managedZoneDnsSecConfig"

    key_signing_key {
      algorithm = "ecdsa_p256"
      kind     = "dns#dnsKeySpec"
    }

    zone_signing_key {
      algorithm = "ecdsa_p256"
      kind     = "dns#dnsKeySpec"
    }
  }

  labels = var.labels
}

# ---------- Controller A Record ----------

resource "google_dns_record_set" "controller" {
  name         = "controller.${var.dns_zone}."
  type         = "A"
  ttl          = 300
  managed_zone = google_dns_managed_zone.evez_zone.name
  rrdatas      = [google_compute_instance.controller.network_interface[0].access_config[0].nat_ip]
}

# ---------- Worker A Records ----------

resource "google_dns_record_set" "worker" {
  count        = var.instance_count_small
  name         = "worker-${count.index}.${var.dns_zone}."
  type         = "A"
  ttl          = 300
  managed_zone = google_dns_managed_zone.evez_zone.name
  rrdatas      = [google_compute_instance.worker[count.index].network_interface[0].access_config[0].nat_ip]
}

# ---------- Free-Tier A Record ----------

resource "google_dns_record_set" "free_tier" {
  name         = "free.${var.dns_zone}."
  type         = "A"
  ttl          = 300
  managed_zone = google_dns_managed_zone.evez_zone.name
  rrdatas      = [google_compute_instance.free_tier.network_interface[0].access_config[0].nat_ip]
}

# ---------- Vultr Primary A Record ----------

resource "google_dns_record_set" "vultr_primary" {
  name         = "vultr.${var.dns_zone}."
  type         = "A"
  ttl          = 300
  managed_zone = google_dns_managed_zone.evez_zone.name
  rrdatas      = [var.vultr_primary_ip]
}

# ---------- Service CNAME records (all → controller) ----------

resource "google_dns_record_set" "evez_services" {
  count        = length(var.evez_service_names)
  name         = "${var.evez_service_names[count.index]}.${var.dns_zone}."
  type         = "CNAME"
  ttl          = 300
  managed_zone = google_dns_managed_zone.evez_zone.name
  rrdatas      = ["controller.${var.dns_zone}."]
}

# ---------- Wildcard mesh subdomain → controller ----------

resource "google_dns_record_set" "mesh_wildcard" {
  name         = "*.mesh.${var.dns_zone}."
  type         = "CNAME"
  ttl          = 300
  managed_zone = google_dns_managed_zone.evez_zone.name
  rrdatas      = ["controller.${var.dns_zone}."]
}
