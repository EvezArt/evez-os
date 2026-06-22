# ---------------------------------------------------------------------------
# outputs.tf — IPs, endpoints, connection strings
# ---------------------------------------------------------------------------

# ---------- Instance IPs ----------

output "controller_public_ip" {
  description = "Public IP of the controller node"
  value       = google_compute_instance.controller.network_interface[0].access_config[0].nat_ip
}

output "controller_internal_ip" {
  description = "Internal IP of the controller node"
  value       = google_compute_instance.controller.network_interface[0].network_ip
}

output "worker_public_ips" {
  description = "Public IPs of worker nodes"
  value       = [for w in google_compute_instance.worker : w.network_interface[0].access_config[0].nat_ip]
}

output "worker_internal_ips" {
  description = "Internal IPs of worker nodes"
  value       = [for w in google_compute_instance.worker : w.network_interface[0].network_ip]
}

output "free_tier_public_ip" {
  description = "Public IP of the free-tier node"
  value       = google_compute_instance.free_tier.network_interface[0].access_config[0].nat_ip
}

output "free_tier_internal_ip" {
  description = "Internal IP of the free-tier node"
  value       = google_compute_instance.free_tier.network_interface[0].network_ip
}

output "vultr_primary_ip" {
  description = "Vultr primary node IP"
  value       = var.vultr_primary_ip
}

# ---------- All Node IPs (flat list) ----------

output "all_node_public_ips" {
  description = "All public IPs across the mesh"
  value = concat(
    [google_compute_instance.controller.network_interface[0].access_config[0].nat_ip],
    [for w in google_compute_instance.worker : w.network_interface[0].access_config[0].nat_ip],
    [google_compute_instance.free_tier.network_interface[0].access_config[0].nat_ip],
    [var.vultr_primary_ip],
  )
}

# ---------- DNS Endpoints ----------

output "dns_zone_name_servers" {
  description = "Cloud DNS nameservers for evez-os.ai"
  value       = google_dns_managed_zone.evez_zone.name_servers
}

output "controller_dns" {
  description = "FQDN of controller"
  value       = "controller.${var.dns_zone}"
}

output "vultr_dns" {
  description = "FQDN of Vultr primary"
  value       = "vultr.${var.dns_zone}"
}

output "service_endpoints" {
  description = "EVEZ service DNS endpoints (port → FQDN:port)"
  value = {
    for i, name in var.evez_service_names :
    "port_${var.evez_ports[i]}" => "${name}.${var.dns_zone}:${var.evez_ports[i]}"
  }
}

# ---------- Network ----------

output "vpc_id" {
  description = "Primary VPC self link"
  value       = google_compute_network.evez_primary.id
}

output "vpc_secondary_id" {
  description = "Secondary VPC self link"
  value       = google_compute_network.evez_secondary.id
}

output "nat_ip_primary" {
  description = "Cloud NAT external IPs (primary region)"
  value       = google_compute_router_nat.evez_nat.nat_ip_allocate_option
}

# ---------- Storage ----------

output "gcs_bucket_name" {
  description = "Artifacts bucket name"
  value       = google_storage_bucket.evez_artifacts.name
}

output "pubsub_topic" {
  description = "Pub/Sub topic for mesh events"
  value       = google_pubsub_topic.evez_events.name
}

# ---------- SSH ----------

output "ssh_command_controller" {
  description = "SSH command for controller"
  value       = "gcloud compute ssh ${google_compute_instance.controller.name} --zone=${var.zone_primary} --project=${var.project_id}"
}

output "ssh_command_iap" {
  description = "IAP tunnel SSH command (no external IP needed)"
  value       = "gcloud compute ssh ${google_compute_instance.controller.name} --zone=${var.zone_primary} --tunnel-through-iap --project=${var.project_id}"
}

# ---------- Monitoring ----------

output "uptime_check_ids" {
  description = "Uptime check IDs indexed by service name"
  value = {
    for i, name in var.evez_service_names :
    name => google_monitoring_uptime_check_config.evez_service[i].name
  }
}

output "alert_policy_names" {
  description = "Active alert policy display names"
  value = [
    google_monitoring_alert_policy.uptime_failure.display_name,
    google_monitoring_alert_policy.high_cpu.display_name,
    google_monitoring_alert_policy.high_disk.display_name,
  ]
}

# ---------- Connection String (summary) ----------

output "mesh_connection_summary" {
  description = "Human-readable mesh connection string"
  value = <<-SUMMARY
    ╔══════════════════════════════════════════════════════╗
    ║              EVEZ MESH — Connection Summary          ║
    ╠══════════════════════════════════════════════════════╣
    ║  Controller:  ${google_compute_instance.controller.network_interface[0].access_config[0].nat_ip} (controller.${var.dns_zone})
    ║  Workers:     ${join(", ", [for w in google_compute_instance.worker : w.network_interface[0].access_config[0].nat_ip])}
    ║  Free-Tier:   ${google_compute_instance.free_tier.network_interface[0].access_config[0].nat_ip} (free.${var.dns_zone})
    ║  Vultr:       ${var.vultr_primary_ip} (vultr.${var.dns_zone})
    ╠══════════════════════════════════════════════════════╣
    ║  Services:    9111/consciousness  9112/desire         ║
    ║               9113/world-model   9114/planner         ║
    ║               9115/inner-voice   9116/self-modify      ║
    ║               9117/agency                              ║
    ╠══════════════════════════════════════════════════════╣
    ║  DNS:         ${join(", ", google_dns_managed_zone.evez_zone.name_servers)}
    ║  Pub/Sub:     ${google_pubsub_topic.evez_events.name}
    ║  GCS:         ${google_storage_bucket.evez_artifacts.name}
    ╚══════════════════════════════════════════════════════╝
  SUMMARY
}
