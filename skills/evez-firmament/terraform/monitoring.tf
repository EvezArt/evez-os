# ---------------------------------------------------------------------------
# monitoring.tf — Uptime checks, alert policies, log sinks
# ---------------------------------------------------------------------------

# ---------- Uptime Checks (ports 9111-9117) ----------

resource "google_monitoring_uptime_check_config" "evez_service" {
  count           = length(var.evez_ports)
  display_name    = "EVEZ ${var.evez_service_names[count.index]} (port ${var.evez_ports[count.index]})"
  period          = var.uptime_check_period
  timeout         = "10s"

  http_check {
    port         = var.evez_ports[count.index]
    path         = "/health"
    use_ssl      = false
    request_method = "GET"
    headers      = {}
  }

  monitored_resource {
    type = "gce_instance"
    labels = {
      project_id = var.project_id
      instance_id = google_compute_instance.controller.instance_id
      zone        = var.zone_primary
    }
  }

  checker_type = "STATIC_IP_CHECKERS"
}

# ---------- Notification Channel ----------

resource "google_monitoring_notification_channel" "email" {
  display_name = "EVEZ Ops Email"
  type         = "email"
  labels = {
    email_address = var.alert_email
  }
}

# ---------- Alert Policy: Uptime Failures ----------

resource "google_monitoring_alert_policy" "uptime_failure" {
  display_name = "EVEZ Service Down"
  combiner     = "OR"

  conditions {
    display_name = "Uptime check failure"

    condition_threshold {
      filter          = "metric.type=\"monitoring.googleapis.com/uptime_check/check_passed\" AND resource.type=\"uptime_service\""
      duration        = "120s"
      comparison      = "COMPARISON_LT"
      threshold_value = 1

      trigger {
        count = 1
      }

      aggregations {
        alignment_period   = "60s"
        per_series_aligner = "ALIGN_NEXT_OLDER"
      }
    }
  }

  notification_channels = [google_monitoring_notification_channel.email.name]

  user_labels = var.labels

  alert_strategy {
    auto_close = "1800s"

    notification_rate_limit {
      period = "300s"
    }
  }
}

# ---------- Alert Policy: High CPU ----------

resource "google_monitoring_alert_policy" "high_cpu" {
  display_name = "EVEZ High CPU Usage"
  combiner     = "OR"

  conditions {
    display_name = "CPU > 85% for 5 minutes"

    condition_threshold {
      filter     = "metric.type=\"compute.googleapis.com/instance/cpu/utilization\" AND resource.type=\"gce_instance\""
      duration   = "300s"
      comparison = "COMPARISON_GT"
      threshold_value = 0.85

      trigger {
        count = 1
      }

      aggregations {
        alignment_period   = "60s"
        per_series_aligner = "ALIGN_MEAN"
      }
    }
  }

  notification_channels = [google_monitoring_notification_channel.email.name]
  user_labels = var.labels
}

# ---------- Alert Policy: High Disk ----------

resource "google_monitoring_alert_policy" "high_disk" {
  display_name = "EVEZ High Disk Usage"
  combiner     = "OR"

  conditions {
    display_name = "Disk > 90% for 10 minutes"

    condition_threshold {
      filter     = "metric.type=\"agent.googleapis.com/disk/disk_used_percent\" AND resource.type=\"gce_instance\""
      duration   = "600s"
      comparison = "COMPARISON_GT"
      threshold_value = 90

      trigger {
        count = 1
      }

      aggregations {
        alignment_period   = "60s"
        per_series_aligner = "ALIGN_MEAN"
      }
    }
  }

  notification_channels = [google_monitoring_notification_channel.email.name]
  user_labels = var.labels
}

# ---------- Log Sink to Pub/Sub ----------

resource "google_logging_project_sink" "evez_sink" {
  name                   = "evez-mesh-log-sink"
  destination            = google_pubsub_topic.evez_events.id
  filter                 = <<-FILTER
    resource.type="gce_instance"
    resource.labels.zone=~"us-west1-.*|us-central1-.*"
    (severity>=WARNING OR
     jsonPayload.message=~"(?i)(error|fatal|panic|crash)" OR
     jsonPayload.source=~"evez-.*")
  FILTER
  description             = "Sink EVEZ mesh logs to Pub/Sub for processing"

  unique_writer_identity = true
}

resource "google_pubsub_topic_iam_binding" "log_sink_writer" {
  topic = google_pubsub_topic.evez_events.name
  role  = "roles/pubsub.publisher"

  members = [
    google_logging_project_sink.evez_sink.writer_identity,
  ]
}

# ---------- Dashboard ----------

resource "google_monitoring_dashboard" "evez_mesh" {
  dashboard_json = jsonencode({
    displayName = "EVEZ Mesh Overview"
    mosaicLayout = {
      tiles = concat(
        [
          for i, port in var.evez_ports : {
            width  = 4
            height = 4
            widget = {
              title   = "EVEZ ${var.evez_service_names[i]} uptime"
              xyChart = {
                dataSets = [{
                  timeSeriesQuery = {
                    timeSeriesFilter = {
                      filter = "metric.type=\"monitoring.googleapis.com/uptime_check/check_passed\" metric.label.check_id=\"${google_monitoring_uptime_check_config.evez_service[i].name}\""
                    }
                  }
                }]
              }
            }
          }
        ],
        [
          {
            width  = 6
            height = 4
            widget = {
              title   = "EVEZ CPU utilization"
              xyChart = {
                dataSets = [{
                  timeSeriesQuery = {
                    timeSeriesFilter = {
                      filter = "metric.type=\"compute.googleapis.com/instance/cpu/utilization\" resource.type=\"gce_instance\" resource.labels.project_id=\"${var.project_id}\""
                    }
                  }
                }]
              }
            }
          }
        ]
      )
    }
  })
}
