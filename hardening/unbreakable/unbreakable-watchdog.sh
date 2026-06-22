#!/usr/bin/env bash
# ============================================================================
# UNBREAKABLE-WATCHDOG.SH — The Watchdog That Watches The Watchdog
# ============================================================================
# This script runs as PID-independent watchdog. It supervises systemd (PID 1).
# If systemd dies, becomes unresponsive, or enters a failed state, this
# watchdog attempts recovery.
#
# Architecture:
#   - Runs as a standalone process (can be launched by systemd, cron, or init)
#   - Monitors PID 1 (systemd) every N seconds
#   - If systemd is unresponsive for > threshold:
#     1. Attempt soft recovery (systemctl daemon-reexec)
#     2. Attempt hard recovery (signal systemd to re-exec)
#     3. Emergency: exec into recovery shell
#   - Self-healing: if this watchdog dies, a cron job restarts it
#   - Inescapable: even if you kill the watchdog, it comes back
#
# Usage:
#   unbreakable-watchdog.sh                    # run as daemon
#   unbreakable-watchdog.sh --install          # install as service + cron failsafe
#   unbreakable-watchdog.sh --uninstall        # remove service + cron
#   unbreakable-watchdog.sh --status           # check watchdog health
# ============================================================================

set -euo pipefail

# --- Configuration ---
STATE_DIR="${EVEZ_WATCHDOG_STATE:-/var/lib/evez/watchdog}"
INTERVAL="${EVEZ_WATCHDOG_INTERVAL:-2}"              # check every 2s
SYSTEMD_DEAD_THRESHOLD=5                              # missed checks = systemd dead
RESTART_ATTEMPTS="${EVEZ_SYSTEMD_RESTART_ATTEMPTS:-5}"
RESTART_DELAY="${EVEZ_SYSTEMD_RESTART_DELAY:-1}"
PID1_PATH="${EVEZ_PID1_PATH:-/sbin/init}"
LOG_FILE="${STATE_DIR}/watchdog.log"
PID_FILE="${STATE_DIR}/watchdog.pid"
CRON_MARKER="# EVEZ-WATCHDOG-FAILSAFE"

mkdir -p "$STATE_DIR"

# --- Logging ---
log() {
    local level="$1"; shift
    local ts
    ts=$(date -Iseconds)
    echo "[$ts] [$level] $*" | tee -a "$LOG_FILE"
}

# --- Systemd Health Check ---
check_systemd() {
    # Method 1: Check if PID 1 is systemd
    if ! ps -p 1 -o comm= 2>/dev/null | grep -q "systemd\|init"; then
        log "CRITICAL" "PID 1 is not systemd! (comm=$(ps -p 1 -o comm= 2>/dev/null || echo 'dead'))"
        return 1
    fi

    # Method 2: Try to communicate with systemd via D-Bus
    if ! systemctl is-system-running &>/dev/null; then
        local state
        state=$(systemctl is-system-running 2>/dev/null || echo "unknown")
        if [[ "$state" == "degraded" ]]; then
            log "WARN" "Systemd is running but degraded"
            return 0  # degraded is still running
        fi
        log "CRITICAL" "Systemd is not running (state=$state)"
        return 1
    fi

    # Method 3: Verify systemd responds to ping
    if ! systemd-notify --booted &>/dev/null; then
        if ! test -d /run/systemd/system; then
            log "CRITICAL" "Systemd is not the init system"
            return 1
        fi
    fi

    return 0
}

# --- Recovery Procedures ---
recover_systemd() {
    local attempt=0

    while [[ $attempt -lt $RESTART_ATTEMPTS ]]; do
        attempt=$((attempt + 1))
        log "RECOVERY" "Attempt $attempt/$RESTART_ATTEMPTS to recover systemd"

        case $attempt in
            1)
                # Soft: ask systemd to re-exec
                log "RECOVERY" "Soft recovery: systemctl daemon-reexec"
                systemctl daemon-reexec 2>/dev/null || true
                sleep "$RESTART_DELAY"
                ;;
            2)
                # Medium: signal PID 1 to re-exec
                log "RECOVERY" "Medium recovery: SIGTERM to PID 1 (daemon-reexec)"
                kill -TERM 1 2>/dev/null || true
                sleep "$RESTART_DELAY"
                ;;
            3)
                # Hard: try to start emergency mode
                log "RECOVERY" "Hard recovery: triggering emergency target"
                systemctl isolate emergency.target 2>/dev/null || true
                sleep "$RESTART_DELAY"
                ;;
            4)
                # Nuclear: try to reboot
                log "RECOVERY" "Nuclear recovery: requesting reboot"
                systemctl reboot --force --force 2>/dev/null || true
                sleep "$RESTART_DELAY"
                ;;
            5)
                # Absolute: sync disks and force reboot via sysrq
                log "RECOVERY" "Absolute recovery: sysrq emergency reboot"
                sync
                echo 1 > /proc/sys/kernel/sysrq 2>/dev/null || true
                echo b > /proc/sysrq-trigger 2>/dev/null || true
                ;;
        esac

        if check_systemd; then
            log "RECOVERY" "Systemd recovered on attempt $attempt!"
            return 0
        fi
    done

    log "FATAL" "All recovery attempts failed. Systemd is unresponsive."
    return 1
}

# --- Service Management ---
# Watch systemd services critical to EVEZ
CRITICAL_SERVICES=(
    "evez-gateway"
    "evez-spine"
    "evez-consciousness"
    "evez-consensus"
)

check_critical_services() {
    for svc in "${CRITICAL_SERVICES[@]}"; do
        if systemctl is-enabled "$svc" &>/dev/null; then
            if ! systemctl is-active "$svc" &>/dev/null; then
                log "WARN" "Critical service $svc is down — restarting"
                systemctl restart "$svc" 2>/dev/null || true
                sleep 1
                if systemctl is-active "$svc" &>/dev/null; then
                    log "INFO" "Service $svc recovered"
                else
                    log "ERROR" "Service $svc failed to recover"
                fi
            fi
        fi
    done
}

# --- Main Daemon Loop ---
run_watchdog() {
    log "INFO" "Watchdog starting (interval=${INTERVAL}s, pid=$$)"
    echo $$ > "$PID_FILE"

    local consecutive_failures=0

    while true; do
        sleep "$INTERVAL"

        # Write heartbeat
        date +%s > "${STATE_DIR}/watchdog-heartbeat"

        # Check systemd
        if ! check_systemd; then
            consecutive_failures=$((consecutive_failures + 1))
            if [[ $consecutive_failures -ge $SYSTEMD_DEAD_THRESHOLD ]]; then
                log "CRITICAL" "Systemd unresponsive for $consecutive_failures checks — RECOVERY"
                recover_systemd
                consecutive_failures=0
            fi
        else
            if [[ $consecutive_failures -gt 0 ]]; then
                log "INFO" "Systemd recovered after $consecutive_failures failures"
            fi
            consecutive_failures=0
        fi

        # Check critical services
        check_critical_services

        # Write state
        cat > "${STATE_DIR}/watchdog-state.json" <<EOF
{
  "pid": $$,
  "systemd_healthy": $(check_systemd && echo "true" || echo "false"),
  "consecutive_failures": $consecutive_failures,
  "timestamp": "$(date -Iseconds)"
}
EOF
    done
}

# --- Install ---
install_watchdog() {
    log "INFO" "Installing EVEZ watchdog..."

    # 1. Install the systemd service
    local script_dir
    script_dir="$(cd "$(dirname "$0")" && pwd)"
    cp "${script_dir}/unbreakable-watchdog.service" /etc/systemd/system/evez-watchdog.service 2>/dev/null || {
        log "WARN" "Cannot install systemd service (need root). Installing cron failsafe only."
    }

    # Copy watchdog binary to system path
    cp "$0" /usr/local/bin/evez-watchdog 2>/dev/null || true
    chmod +x /usr/local/bin/evez-watchdog 2>/dev/null || true

    # 2. Enable and start the service
    if [[ -f /etc/systemd/system/evez-watchdog.service ]]; then
        systemctl daemon-reload 2>/dev/null || true
        systemctl enable evez-watchdog 2>/dev/null || true
        systemctl start evez-watchdog 2>/dev/null || true
        log "INFO" "Systemd service installed and started"
    fi

    # 3. Install cron failsafe — if systemd dies, cron restarts the watchdog
    # This is the inescapable layer: even if systemd is gone, cron still runs
    local cron_entry="* * * * * /usr/local/bin/evez-watchdog --ensure-running $CRON_MARKER"
    (crontab -l 2>/dev/null | grep -v "$CRON_MARKER"; echo "$cron_entry") | crontab - 2>/dev/null || {
        log "WARN" "Cannot install cron failsafe"
    }

    # 4. Install inittab failsafe (for SysV init systems)
    if [[ -f /etc/inittab ]]; then
        if ! grep -q "evez-watchdog" /etc/inittab; then
            echo "w0:2345:respawn:/usr/local/bin/evez-watchdog" >> /etc/inittab 2>/dev/null || true
        fi
    fi

    log "INFO" "Installation complete. Watchdog is now inescapable."
}

# --- Uninstall ---
uninstall_watchdog() {
    log "INFO" "Uninstalling EVEZ watchdog..."

    systemctl stop evez-watchdog 2>/dev/null || true
    systemctl disable evez-watchdog 2>/dev/null || true
    rm -f /etc/systemd/system/evez-watchdog.service
    systemctl daemon-reload 2>/dev/null || true

    (crontab -l 2>/dev/null | grep -v "$CRON_MARKER") | crontab - 2>/dev/null || true

    rm -f /usr/local/bin/evez-watchdog
    log "INFO" "Uninstallation complete"
}

# --- Status ---
status_watchdog() {
    echo "=== EVEZ Watchdog Status ==="
    echo ""
    echo "Watchdog process:"
    if [[ -f "$PID_FILE" ]]; then
        local pid
        pid=$(cat "$PID_FILE")
        if ps -p "$pid" &>/dev/null; then
            echo "  Running (PID $pid)"
        else
            echo "  NOT RUNNING (stale PID file)"
        fi
    else
        echo "  NOT RUNNING"
    fi

    echo ""
    echo "Systemd health:"
    if check_systemd; then
        echo "  HEALTHY ($(systemctl is-system-running 2>/dev/null || echo 'unknown'))"
    else
        echo "  UNRESPONSIVE"
    fi

    echo ""
    if [[ -f "${STATE_DIR}/watchdog-state.json" ]]; then
        echo "Last state:"
        cat "${STATE_DIR}/watchdog-state.json"
    fi
}

# --- Ensure Running (for cron failsafe) ---
ensure_running() {
    if [[ -f "$PID_FILE" ]]; then
        local pid
        pid=$(cat "$PID_FILE")
        if ps -p "$pid" &>/dev/null; then
            return 0
        fi
    fi
    # Not running — start it
    log "INFO" "Watchdog not running — starting (from failsafe)"
    nohup "$0" </dev/null >> "$LOG_FILE" 2>&1 &
    disown
}

# --- Entry Point ---
main() {
    case "${1:-run}" in
        --install)      install_watchdog ;;
        --uninstall)    uninstall_watchdog ;;
        --status)       status_watchdog ;;
        --ensure-running) ensure_running ;;
        run|*)          run_watchdog ;;
    esac
}

main "$@"
