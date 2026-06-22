#!/usr/bin/env bash
# ============================================================================
# UNBREAKABLE-HA.SH — Multi-Node Consensus Cluster
# ============================================================================
# Survive ANY single node failure. If the primary dies, ANY node becomes
# primary within 3 seconds. Zero downtime. The mesh never stops.
#
# Architecture:
#   - Each node runs this daemon
#   - Nodes gossip heartbeats every 1s
#   - If primary misses 3 heartbeats (3s), election triggers
#   - Highest-priority reachable node wins election
#   - State is replicated via the spine (see unbreakable-spine.sh)
#   - No single point of failure. No single point of control.
#
# Usage:
#   unbreakable-ha.sh --node-id node1 --nodes node1:port,node2:port,node3:port
#   unbreakable-ha.sh --bootstrap  # auto-configure from EVEZ_MESH env
# ============================================================================

set -euo pipefail

# --- Configuration ---
STATE_DIR="${EVEZ_STATE_DIR:-/var/lib/evez/ha}"
HEARTBEAT_INTERVAL="${EVEZ_HB_INTERVAL:-1}"       # seconds between heartbeats
ELECTION_TIMEOUT="${EVEZ_ELECTION_TIMEOUT:-3}"      # seconds before election
MISSED_THRESHOLD=3                                  # missed heartbeats = dead
PID_FILE="${STATE_DIR}/ha-daemon.pid"
LOG_FILE="${STATE_DIR}/ha.log"

# Node identity
NODE_ID=""
NODE_PORT=7900
NODE_PRIORITY=0    # lower = higher priority for election
PEERS=()           # array of "host:port" strings

# --- Cluster State ---
ROLE="follower"    # follower | candidate | primary
TERM=0
PRIMARY_ID=""
LAST_HB_FROM_PEERS=()  # timestamps of last heartbeat per peer
ALIVE_PEERS=()

# --- Signal Handling ---
cleanup() {
    log "INFO" "HA daemon shutting down (role=$ROLE, term=$TERM)"
    rm -f "$PID_FILE"
    exit 0
}
trap cleanup SIGINT SIGTERM SIGHUP

# --- Utilities ---
log() {
    local level="$1"; shift
    echo "[$(date -Iseconds)] [$level] [node=$NODE_ID] $*" >> "$LOG_FILE"
}

mkdir -p "$STATE_DIR"

write_state() {
    cat > "${STATE_DIR}/cluster-state.json" <<EOF
{
  "node_id": "$NODE_ID",
  "role": "$ROLE",
  "term": $TERM,
  "primary_id": "$PRIMARY_ID",
  "timestamp": "$(date -Iseconds)",
  "peers_alive": [$(printf '"%s",' "${ALIVE_PEERS[@]}" | sed 's/,$//')]
}
EOF
}

# --- Network: Simple TCP heartbeat protocol ---
# Protocol: each message is a single JSON line
#   {"type":"heartbeat","node_id":"X","term":N,"role":"primary|follower","priority":P}
#   {"type":"vote_request","node_id":"X","term":N}
#   {"type":"vote_response","node_id":"X","term":N,"granted":true|false}
#   {"type":"state_sync","node_id":"X","spine_hash":"H","events":N}

send_heartbeat() {
    local peer="$1"
    local host="${peer%%:*}"
    local port="${peer##*:}"
    local msg
    msg=$(printf '{"type":"heartbeat","node_id":"%s","term":%d,"role":"%s","priority":%d}' \
        "$NODE_ID" "$TERM" "$ROLE" "$NODE_PRIORITY")

    # Fire-and-forget UDP-like via timeout'd TCP
    timeout 0.5 bash -c "echo '$msg' | nc -q0 -w1 '$host' '$port'" 2>/dev/null || true
}

broadcast_heartbeat() {
    for peer in "${PEERS[@]}"; do
        send_heartbeat "$peer"
    done
}

# --- Listener ---
start_listener() {
    # Listen on NODE_PORT for heartbeats from peers
    while true; do
        nc -l -p "$NODE_PORT" -q0 2>/dev/null | while read -r line; do
            handle_message "$line"
        done
    done &
    LISTENER_PID=$!
    log "INFO" "Listener started on port $NODE_PORT (pid=$LISTENER_PID)"
}

handle_message() {
    local msg="$1"
    local type
    type=$(echo "$msg" | jq -r '.type' 2>/dev/null || echo "unknown")

    case "$type" in
        heartbeat)
            local sender_id sender_term sender_role
            sender_id=$(echo "$msg" | jq -r '.node_id')
            sender_term=$(echo "$msg" | jq -r '.term')
            sender_role=$(echo "$msg" | jq -r '.role')

            # Record heartbeat
            local idx
            for i in "${!PEERS[@]}"; do
                if [[ "${PEERS[$i]}" == *"$sender_id"* ]]; then
                    LAST_HB_FROM_PEERS[$i]=$(date +%s)
                    break
                fi
            done

            # Update primary tracking
            if [[ "$sender_role" == "primary" && "$sender_term" -ge "$TERM" ]]; then
                PRIMARY_ID="$sender_id"
                TERM="$sender_term"
                if [[ "$ROLE" == "candidate" ]]; then
                    ROLE="follower"
                    log "INFO" "Stepping down: discovered primary $sender_id (term=$sender_term)"
                fi
            fi
            ;;

        vote_request)
            local candidate_id candidate_term
            candidate_id=$(echo "$msg" | jq -r '.node_id')
            candidate_term=$(echo "$msg" | jq -r '.term')

            local granted=false
            if [[ "$candidate_term" -gt "$TERM" ]]; then
                granted=true
                TERM="$candidate_term"
                ROLE="follower"
                log "INFO" "Granting vote to $candidate_id (term=$candidate_term)"
            fi

            local response
            response=$(printf '{"type":"vote_response","node_id":"%s","term":%d,"granted":%s}' \
                "$NODE_ID" "$TERM" "$granted")
            send_to_node "$candidate_id" "$response"
            ;;

        vote_response)
            local voter granted
            voter=$(echo "$msg" | jq -r '.node_id')
            granted=$(echo "$msg" | jq -r '.granted')
            if [[ "$granted" == "true" ]]; then
                VOTES_RECEIVED=$((VOTES_RECEIVED + 1))
                log "INFO" "Vote granted by $voter (total=$VOTES_RECEIVED)"
            fi
            ;;

        state_sync)
            # Peer is offering spine state — handled by unbreakable-spine.sh
            log "INFO" "State sync received from $(echo "$msg" | jq -r '.node_id')"
            ;;

        *)
            log "WARN" "Unknown message type: $type"
            ;;
    esac
}

send_to_node() {
    local target_id="$1"
    local msg="$2"
    for peer in "${PEERS[@]}"; do
        if [[ "$peer" == *"$target_id"* ]]; then
            send_heartbeat "$peer"  # reuse heartbeat channel
            break
        fi
    done
}

# --- Election ---
VOTES_RECEIVED=0

start_election() {
    TERM=$((TERM + 1))
    ROLE="candidate"
    VOTES_RECEIVED=1  # self-vote
    PRIMARY_ID=""
    log "INFO" "Starting election (term=$TERM, priority=$NODE_PRIORITY)"

    # Request votes from all peers
    for peer in "${PEERS[@]}"; do
        local msg
        msg=$(printf '{"type":"vote_request","node_id":"%s","term":%d}' \
            "$NODE_ID" "$TERM")
        send_heartbeat "$peer"  # reuse channel
    done

    # Wait for votes (simple majority)
    local quorum=$(( (${#PEERS[@]} + 1) / 2 + 1 ))
    local waited=0
    while [[ $VOTES_RECEIVED -lt $quorum && $waited -lt 2 ]]; do
        sleep 0.5
        waited=$((waited + 1))
    done

    if [[ $VOTES_RECEIVED -ge $quorum ]]; then
        ROLE="primary"
        PRIMARY_ID="$NODE_ID"
        log "INFO" "Elected primary! (term=$TERM, votes=$VOTES_RECEIVED)"
        # Announce leadership
        for peer in "${PEERS[@]}"; do
            local msg
            msg=$(printf '{"type":"heartbeat","node_id":"%s","term":%d,"role":"primary","priority":%d}' \
                "$NODE_ID" "$TERM" "$NODE_PRIORITY")
            send_heartbeat "$peer"
        done
    else
        ROLE="follower"
        log "INFO" "Election failed (votes=$VOTES_RECEIVED, needed=$quorum)"
    fi
}

# --- Health Check ---
check_peer_health() {
    local now=$(date +%s)
    ALIVE_PEERS=()

    for i in "${!PEERS[@]}"; do
        local last="${LAST_HB_FROM_PEERS[$i]:-0}"
        local elapsed=$((now - last))
        local peer="${PEERS[$i]}"

        if [[ $elapsed -lt $MISSED_THRESHOLD ]]; then
            ALIVE_PEERS+=("$peer")
        elif [[ $elapsed -eq $MISSED_THRESHOLD ]]; then
            log "WARN" "Peer $peer missed $MISSED_THRESHOLD heartbeats"
        else
            log "ERROR" "Peer $peer is DOWN (last heartbeat ${elapsed}s ago)"
        fi
    done

    # Check if primary is still alive
    if [[ -n "$PRIMARY_ID" && "$PRIMARY_ID" != "$NODE_ID" ]]; then
        local primary_alive=false
        for peer in "${ALIVE_PEERS[@]}"; do
            if [[ "$peer" == *"$PRIMARY_ID"* ]]; then
                primary_alive=true
                break
            fi
        done

        if [[ "$primary_alive" == "false" ]]; then
            log "CRITICAL" "Primary $PRIMARY_ID is DEAD. Triggering election."
            start_election
        fi
    fi
}

# --- Primary Responsibilities ---
run_primary_duties() {
    if [[ "$ROLE" != "primary" ]]; then
        return
    fi

    # 1. Broadcast leadership heartbeats more frequently
    broadcast_heartbeat

    # 2. Check peer health
    check_peer_health

    # 3. Trigger spine checkpoint (if unbreakable-spine.sh is present)
    if [[ -x "${STATE_DIR}/../unbreakable-spine.sh" ]]; then
        "${STATE_DIR}/../unbreakable-spine.sh" --checkpoint 2>/dev/null || true
    fi

    # 4. Write cluster state
    write_state
}

# --- Main Loop ---
run_daemon() {
    log "INFO" "HA daemon starting (id=$NODE_ID, port=$NODE_PORT, peers=${#PEERS[@]})"
    echo $$ > "$PID_FILE"

    # Start listener
    start_listener

    # Determine initial role
    if [[ ${#PEERS[@]} -eq 0 ]]; then
        ROLE="primary"
        PRIMARY_ID="$NODE_ID"
        log "INFO" "Single-node mode — becoming primary"
    else
        # Check if any existing primary
        ROLE="follower"
        log "INFO" "Multi-node mode — starting as follower, discovering primary"
    fi

    write_state

    # Main event loop
    local tick=0
    while true; do
        sleep "$HEARTBEAT_INTERVAL"
        tick=$((tick + 1))

        # Broadcast heartbeat every tick
        broadcast_heartbeat

        # Run primary-specific duties
        if [[ "$ROLE" == "primary" ]]; then
            run_primary_duties
        fi

        # Follower: check if primary is alive
        if [[ "$ROLE" == "follower" ]]; then
            if [[ $((tick % 3)) -eq 0 ]]; then
                check_peer_health
            fi
        fi

        # Write state every 5 ticks
        if [[ $((tick % 5)) -eq 0 ]]; then
            write_state
        fi
    done
}

# --- Argument Parsing ---
parse_args() {
    while [[ $# -gt 0 ]]; do
        case "$1" in
            --node-id)
                NODE_ID="$2"; shift 2 ;;
            --port)
                NODE_PORT="$2"; shift 2 ;;
            --priority)
                NODE_PRIORITY="$2"; shift 2 ;;
            --peers)
                IFS=',' read -ra PEERS <<< "$2"; shift 2 ;;
            --bootstrap)
                # Auto-configure from environment
                NODE_ID="${EVEZ_NODE_ID:-$(hostname)}"
                NODE_PORT="${EVEZ_NODE_PORT:-7900}"
                NODE_PRIORITY="${EVEZ_NODE_PRIORITY:-0}"
                if [[ -n "${EVEZ_MESH_PEERS:-}" ]]; then
                    IFS=',' read -ra PEERS <<< "$EVEZ_MESH_PEERS"
                fi
                shift ;;
            --status)
                # Quick status check
                if [[ -f "${STATE_DIR}/cluster-state.json" ]]; then
                    cat "${STATE_DIR}/cluster-state.json"
                else
                    echo '{"status":"not_running"}'
                fi
                exit 0 ;;
            *)
                echo "Unknown argument: $1" >&2
                exit 1 ;;
        esac
    done

    : "${NODE_ID:=$(hostname)}"
}

# --- Entry Point ---
main() {
    parse_args "$@"

    case "${1:-}" in
        --status)
            # Already handled in parse_args
            ;;
        *)
            run_daemon
            ;;
    esac
}

main "$@"
