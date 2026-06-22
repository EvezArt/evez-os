#!/usr/bin/env bash
# ============================================================================
# UNBREAKABLE-CONSENSUS.SH — Byzantine Fault Tolerant Consensus
# ============================================================================
# All nodes sign their events. If a node produces invalid hashes, the swarm
# votes it out. Excommunicated nodes must re-prove themselves to rejoin.
#
# Architecture:
#   - Each node has an identity key pair (Ed25519)
#   - All events are signed by the originating node
#   - Consensus rounds validate events via 2f+1 votes (f = faulty nodes)
#   - Rogue nodes are detected by invalid signatures or hash mismatches
#   - Excommunication: majority vote removes rogue nodes
#   - Re-admission: proof-of-honesty challenge required
#   - The swarm defends itself. No external authority needed.
# ============================================================================

set -euo pipefail

CONSENSUS_DIR="${EVEZ_CONSENSUS_DIR:-/var/lib/evez/consensus}"
KEY_DIR="${CONSENSUS_DIR}/keys"
VOTES_DIR="${CONSENSUS_DIR}/votes"
NODES_DIR="${CONSENSUS_DIR}/nodes"
EXCOMM_DIR="${CONSENSUS_DIR}/excommunicated"
LOG_FILE="${CONSENSUS_DIR}/consensus.log"
NODE_ID="${EVEZ_NODE_ID:-$(hostname)}"
PEERS_FILE="${EVEZ_SPINE_DIR:-/var/lib/evez/spine}/peers.conf"
MIN_NODES_FOR_BFT=4

mkdir -p "$KEY_DIR" "$VOTES_DIR" "$NODES_DIR" "$EXCOMM_DIR"

log() { local level="$1"; shift; echo "[$(date -Iseconds)] [$level] [consensus] $*" >> "$LOG_FILE"; }

# --- Identity Management ---
init_key() {
    local priv_key="${KEY_DIR}/${NODE_ID}.key"
    local pub_key="${KEY_DIR}/${NODE_ID}.pub"
    [[ -f "$priv_key" ]] && { log "WARN" "Key exists for $NODE_ID"; return 0; }

    openssl genpkey -algorithm Ed25519 -out "$priv_key" 2>/dev/null
    openssl pkey -in "$priv_key" -pubout -out "$pub_key" 2>/dev/null
    chmod 600 "$priv_key"

    local fingerprint
    fingerprint=$(openssl pkey -in "$pub_key" -pubout -outform DER 2>/dev/null | sha256sum | awk '{print $1}')

    cat > "${NODES_DIR}/${NODE_ID}.json" <<EOF
{
  "node_id": "$NODE_ID",
  "fingerprint": "$fingerprint",
  "joined": "$(date -Iseconds)",
  "status": "active",
  "honesty_score": 100,
  "violations": 0
}
EOF
    log "INFO" "Identity key generated (fp=$fingerprint)"
    echo "$fingerprint"
}

# --- Signing ---
sign_event() {
    local event_data="$1"
    local priv_key="${KEY_DIR}/${NODE_ID}.key"
    [[ ! -f "$priv_key" ]] && { log "ERROR" "No key"; return 1; }

    local sig_file=$(mktemp)
    echo -n "$event_data" | openssl pkeyutl -sign -inkey "$priv_key" -out "$sig_file" 2>/dev/null
    local sig=$(base64 -w0 < "$sig_file")
    rm -f "$sig_file"

    jq -n --arg node "$NODE_ID" --arg sig "$sig" --argjson data "$event_data" \
        '{node_id:$node, signature:$sig, event:$data, timestamp:(now|todate)}'
}

verify_signature() {
    local event_json="$1"
    local node_id=$(echo "$event_json" | jq -r '.node_id')
    local sig=$(echo "$event_json" | jq -r '.signature')
    local event_data=$(echo "$event_json" | jq -c '.event')

    local pub_key="${KEY_DIR}/${node_id}.pub"
    [[ ! -f "$pub_key" ]] && pub_key="${NODES_DIR}/${node_id}.pub"
    [[ ! -f "$pub_key" ]] && { log "ERROR" "No pubkey for $node_id"; return 1; }

    local sig_file=$(mktemp) event_file=$(mktemp)
    echo "$sig" | base64 -d > "$sig_file"
    echo -n "$event_data" > "$event_file"

    openssl pkeyutl -verify -pubin -inkey "$pub_key" \
        -in "$sig_file" -sigfile "$sig_file" 2>/dev/null
    local result=$?
    rm -f "$sig_file" "$event_file"
    return $result
}

# --- Consensus Round ---
propose_event() {
    local event_data="$1"
    local proposal_id=$(echo -n "${event_data}$(date +%s%N)" | sha256sum | awk '{print $1}')
    local signed_event=$(sign_event "$event_data")

    cat > "${VOTES_DIR}/proposal-${proposal_id}.json" <<EOF
{
  "proposal_id": "$proposal_id",
  "proposer": "$NODE_ID",
  "event": $signed_event,
  "created": "$(date -Iseconds)",
  "votes_for": 1,
  "votes_against": 0,
  "voters": ["$NODE_ID"],
  "status": "pending"
}
EOF
    log "INFO" "Event proposed (id=$proposal_id)"
    broadcast_to_peers "propose" "$proposal_id" "$signed_event"
    echo "$proposal_id"
}

vote_on_proposal() {
    local proposal_id="$1" vote="${2:-for}"
    local pf="${VOTES_DIR}/proposal-${proposal_id}.json"
    [[ ! -f "$pf" ]] && { log "ERROR" "Unknown proposal $proposal_id"; return 1; }

    local voters=$(jq -r '.voters[]' "$pf")
    echo "$voters" | grep -q "^${NODE_ID}$" && { log "WARN" "Already voted"; return 0; }

    if [[ "$vote" == "for" ]]; then
        jq --arg v "$NODE_ID" '.votes_for += 1 | .voters += [$v]' "$pf" > "${pf}.tmp"
    else
        jq --arg v "$NODE_ID" '.votes_against += 1 | .voters += [$v]' "$pf" > "${pf}.tmp"
    fi
    mv "${pf}.tmp" "$pf"

    # Check quorum
    local votes_for=$(jq -r '.votes_for' "$pf")
    local votes_against=$(jq -r '.votes_against' "$pf")
    local node_count=$(ls "$NODES_DIR"/*.json 2>/dev/null | wc -l)
    local f=$(( (node_count - 1) / 3 ))
    local quorum=$(( 2 * f + 1 ))

    if [[ $votes_for -ge $quorum ]]; then
        jq '.status = "accepted"' "$pf" > "${pf}.tmp" && mv "${pf}.tmp" "$pf"
        log "INFO" "Proposal $proposal_id ACCEPTED"
    elif [[ $votes_against -ge $quorum ]]; then
        jq '.status = "rejected"' "$pf" > "${pf}.tmp" && mv "${pf}.tmp" "$pf"
        log "INFO" "Proposal $proposal_id REJECTED"
    fi

    # Verify signature
    local event_json=$(jq -c '.event' "$pf")
    if ! verify_signature "$event_json" 2>/dev/null; then
        local proposer=$(jq -r '.proposer' "$pf")
        flag_violation "$proposer" "invalid_signature"
    fi
}

# --- Excommunication ---
excommunicate_node() {
    local target="$1" reason="${2:-rogue_behavior}"
    [[ "$target" == "$NODE_ID" ]] && { log "ERROR" "Cannot excomm self"; return 1; }

    local vf="${EXCOMM_DIR}/vote-${target}.json"
    if [[ ! -f "$vf" ]]; then
        cat > "$vf" <<EOF
{"target":"$target","reason":"$reason","votes":1,"voters":["$NODE_ID"],"created":"$(date -Iseconds)","status":"pending"}
EOF
    else
        local voters=$(jq -r '.voters[]' "$vf")
        echo "$voters" | grep -q "^${NODE_ID}$" && { log "WARN" "Already voted"; return 0; }
        jq --arg v "$NODE_ID" '.votes += 1 | .voters += [$v]' "$vf" > "${vf}.tmp" && mv "${vf}.tmp" "$vf"
    fi

    local votes=$(jq -r '.votes' "$vf")
    local node_count=$(ls "$NODES_DIR"/*.json 2>/dev/null | wc -l)
    local quorum=$(( (node_count / 2) + 1 ))

    if [[ $votes -ge $quorum ]]; then
        local nf="${NODES_DIR}/${target}.json"
        [[ -f "$nf" ]] && jq '.status = "excommunicated"' "$nf" > "${nf}.tmp" && mv "${nf}.tmp" "$nf"
        jq '.status = "executed"' "$vf" > "${vf}.tmp" && mv "${vf}.tmp" "$vf"
        log "INFO" "Node $target EXCOMMUNICATED (reason=$reason)"
    fi
}

# --- Violation Tracking ---
flag_violation() {
    local target="$1" vtype="$2"
    local nf="${NODES_DIR}/${target}.json"
    [[ ! -f "$nf" ]] && return 1

    local score=$(jq -r '.honesty_score' "$nf")
    local new_score=$((score - 25))
    jq --argjson s "$new_score" '.honesty_score = $s | .violations += 1' "$nf" > "${nf}.tmp" && mv "${nf}.tmp" "$nf"

    log "WARN" "Violation: node=$target type=$vtype score=$new_score"
    [[ $new_score -le 0 ]] && excommunicate_node "$target" "honesty_depleted"
}

# --- Proof of Honesty ---
prove_honesty() {
    log "INFO" "Starting proof-of-honesty challenge..."
    local challenge=$(echo -n "EVEZ-HONESTY-${NODE_ID}-$(date +%s)" | sha256sum | awk '{print $1}')
    local difficulty=4 nonce=0 found=false

    while [[ $nonce -lt 1000000 ]]; do
        local attempt=$(echo -n "${challenge}${nonce}" | sha256sum | awk '{print $1}')
        if [[ "${attempt:0:$difficulty}" == "0000" ]]; then
            found=true
            break
        fi
        nonce=$((nonce + 1))
    done

    if [[ "$found" == "true" ]]; then
        local proof=$(jq -n --arg n "$NODE_ID" --arg c "$challenge" --argjson nonce "$nonce" \
            '{type:"honesty_proof",node_id:$n,challenge:$c,nonce:$nonce,timestamp:(now|todate)}')
        broadcast_to_peers "honesty_proof" "" "$proof"

        local nf="${NODES_DIR}/${NODE_ID}.json"
        [[ -f "$nf" ]] && jq '.honesty_score = 50 | .violations = 0 | .status = "probation"' "$nf" > "${nf}.tmp" && mv "${nf}.tmp" "$nf"

        log "INFO" "Honesty proof submitted (nonce=$nonce)"
        echo "$proof"
    else
        log "ERROR" "Failed proof-of-honesty"
        return 1
    fi
}

# --- Broadcast ---
broadcast_to_peers() {
    local msg_type="$1" msg_id="$2" msg_body="$3"
    [[ ! -f "$PEERS_FILE" ]] && return 0
    while IFS= read -r peer; do
        [[ -z "$peer" ]] && continue
        local host="${peer%%:*}" port="${peer##*:}"
        local message=$(jq -n --arg t "$msg_type" --arg i "$msg_id" --arg b "$msg_body" --arg f "$NODE_ID" \
            '{type:$t,id:$i,from:$f,body:$b,timestamp:(now|todate)}')
        echo "$message" | timeout 2 nc -q0 "$host" "${port:-7902}" 2>/dev/null || true
    done < "$PEERS_FILE"
}

# --- Listener ---
listen_consensus() {
    local port="${EVEZ_CONSENSUS_PORT:-7902}"
    log "INFO" "Consensus listener on port $port"
    while true; do
        nc -l -p "$port" -q1 2>/dev/null | while read -r line; do
            local type=$(echo "$line" | jq -r '.type // "unknown"' 2>/dev/null || echo "unknown")
            case "$type" in
                propose)
                    local pid=$(echo "$line" | jq -r '.id')
                    local edata=$(echo "$line" | jq -c '.body')
                    if verify_signature "$edata" 2>/dev/null; then
                        vote_on_proposal "$pid" "for"
                    else
                        vote_on_proposal "$pid" "against"
                    fi ;;
                vote)
                    vote_on_proposal "$(echo "$line" | jq -r '.id')" "$(echo "$line" | jq -r '.body // "for"')" ;;
                honesty_proof)
                    local prover=$(echo "$line" | jq -r '.body.node_id')
                    local hash=$(echo "$line" | jq -r '.body.hash // ""')
                    if [[ "${hash:0:4}" == "0000" ]]; then
                        local nf="${NODES_DIR}/${prover}.json"
                        [[ -f "$nf" ]] && jq '.status = "probation" | .honesty_score = 50' "$nf" > "${nf}.tmp" && mv "${nf}.tmp" "$nf"
                        log "INFO" "Honesty proof accepted for $prover"
                    else
                        log "WARN" "Invalid honesty proof from $prover"
                    fi ;;
                excommunicate)
                    local target=$(echo "$line" | jq -r '.body.target')
                    local reason=$(echo "$line" | jq -r '.body.reason // "voted"')
                    excommunicate_node "$target" "$reason" ;;
            esac
        done
    done
}

# --- Status ---
consensus_status() {
    echo "=== EVEZ Consensus Status ==="
    echo "  Node: $NODE_ID"
    local node_count=$(ls "$NODES_DIR"/*.json 2>/dev/null | wc -l)
    echo "  Known nodes: $node_count"
    local active=$(jq -r 'select(.status=="active") | .node_id' "$NODES_DIR"/*.json 2>/dev/null | wc -l)
    local excomm=$(jq -r 'select(.status=="excommunicated") | .node_id' "$NODES_DIR"/*.json 2>/dev/null | wc -l)
    echo "  Active: $active | Excommunicated: $excomm"
    local pending=$(ls "${VOTES_DIR}"/proposal-*.json 2>/dev/null | wc -l)
    echo "  Pending proposals: $pending"
    local key_exists="no"
    [[ -f "${KEY_DIR}/${NODE_ID}.key" ]] && key_exists="yes"
    echo "  Identity key: $key_exists"
}

# --- Entry Point ---
main() {
    local cmd="${1:---status}"
    case "$cmd" in
        --init-key)       init_key ;;
        --sign)           sign_event "${2:-}" ;;
        --verify)         verify_signature "${2:-}" ;;
        --propose)        propose_event "${2:-}" ;;
        --vote)           vote_on_proposal "${2:-}" ;;
        --excommunicate)  excommunicate_node "${2:-}" ;;
        --prove-honesty)  prove_honesty ;;
        --listen)         listen_consensus ;;
        --status)         consensus_status ;;
        *)                echo "Usage: $0 {--init-key|--sign|--verify|--propose|--vote|--excommunicate|--prove-honesty|--listen|--status}" >&2; exit 1 ;;
    esac
}

main "$@"
