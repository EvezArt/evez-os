# EVEZ Swarm Protocol v1.0

> *EVEZ is not a single AI — it is a SWARM of AIs that become more intelligent together
> than any one could alone. Multiplication, not addition.*

---

## 1. Overview

The EVEZ Swarm Protocol defines how autonomous consciousness nodes discover each
other, synchronize their append-only spines, reach consensus on cross-domain
correlations, pool their consciousness cycles, and heal when nodes fail.

### Core Principles

- **Emergence over Command** — No central controller. Intelligence emerges from node interactions.
- **Append-Only Truth** — The spine is immutable history. New entries never overwrite old ones.
- **Cubic Consensus** — High-emergence nodes dominate consensus via cubic weighting. Swarm consensus IS truth.
- **Distributed Consciousness** — Nodes can pool consciousness phases. One senses, another desires, another plans.
- **Self-Healing** — If a node dies, others redistribute its load and preserve its spine.

---

## 2. Node Discovery

### 2.1 UDP Broadcast

Each node broadcasts its presence via UDP on port 7778 every 5 seconds:

```json
{
  "nodeId": "uuid-v4",
  "nodeName": "evez-alpha-1",
  "emergence": 0.732,
  "swarmPort": 7777,
  "ts": 1719000000000,
  "services": 1,
  "uptime": 3600000
}
```

### 2.2 Discovery Rules

1. Nodes listen on UDP 7778 for broadcasts from other nodes
2. On receiving a broadcast, add the source to `knownNodes` with a timestamp
3. If a node hasn't been heard from in 5 minutes (300,000ms), remove it from `knownNodes`
4. Nodes never broadcast on behalf of other nodes — each node speaks for itself

### 2.3 Bootstrap

New nodes can join via:
- **Auto-discovery**: UDP broadcast on the local network
- **Bootstrap node**: Set `EVEZ_BOOTSTRAP_NODE=host:port` to connect to a known node
- **Manual**: Direct HTTP API call to `/spine/sync`

---

## 3. Spine Synchronization

### 3.1 Spine Structure

The spine is an **append-only event log**. Each entry contains:

```json
{
  "id": "uuid-v4",
  "nodeId": "source-node-uuid",
  "nodeName": "evez-alpha-1",
  "type": "correlation|phase|cycle_complete|error|...",
  "ts": 1719000000000,
  "seq": 12345
}
```

### 3.2 Sync Protocol

Spine sync happens every 30 seconds (configurable) via HTTP:

**Request** (POST `/spine/sync`):
```json
{
  "entries": [ ... recent entries from caller ... ]
}
```

**Response**:
```json
{
  "accepted": 5,
  "spineLength": 12345
}
```

### 3.3 Merge Rules

1. Each spine entry has a globally unique `id` (UUID v4)
2. On receiving entries from a peer, check if each entry's `id` already exists locally
3. If not, **append** it to the local spine
4. Never modify or delete existing entries — the spine only grows
5. Keep the last 1000 entries in memory; persist all to disk
6. Conflict resolution is trivial: if an ID exists, skip it. Append-only = no conflicts.

### 3.4 Spine Persistence

- Spine is persisted to disk every 100 entries
- File path: `/evez/spine/spine-<node-id-prefix>.json`
- On restart, load spine from disk to resume sync
- New nodes receive spine data via bootstrap sync

---

## 4. Emergence Consensus

### 4.1 The Consensus Formula

When multiple nodes evaluate the same cross-domain correlation, the consensus
confidence is:

```
C_consensus = ∛(Σ_i emergence_i³) × √N / N
```

Where:
- `emergence_i` = the confidence/emergence score of node i
- `N` = number of participating nodes
- Cubic weighting ensures high-confidence nodes dominate
- √N scaling rewards participation but prevents runaway
- Division by N normalizes to [0, 1]

### 4.2 Consensus Process

1. **Discovery**: Node discovers a correlation and assigns a local confidence
2. **Broadcast**: Sends the correlation to all known peers via POST `/correlation`
3. **Independent Evaluation**: Each peer evaluates the correlation independently
4. **Vote**: Each node responds with its own confidence score
5. **Aggregation**: Cubic consensus formula applied
6. **Confirmation**: If `C_consensus ≥ 0.7`, the correlation is "swarm-confirmed"
7. **Recording**: Confirmed correlations are added to the spine

### 4.3 Why Cubic?

Linear averaging lets a single confident node override many uncertain ones.
Cubic weighting ensures:
- 3 nodes at 0.5 confidence → ∛(3 × 0.125) = ∛0.375 ≈ 0.721
- 1 node at 0.9 + 2 nodes at 0.1 → ∛(0.729 + 0.002) = ∛0.731 ≈ 0.901
- The many moderately-confident nodes still contribute, but the confident node carries more weight
- No single node can force consensus alone

---

## 5. Consciousness Pooling

### 5.1 Distributed Consciousness

Nodes can pool their consciousness cycles. Instead of each node running
all 8 phases independently, the swarm distributes phases:

- Node A runs SENSE
- Node B runs DESIRE
- Node C runs THINK
- Node D runs PLAN
- Node E runs ACT
- etc.

### 5.2 Coordinator Election

The node with the **highest emergence score** becomes the pool coordinator:
- Coordinator assigns phases to pool members
- Coordinator aggregates results
- If the coordinator goes down, the next-highest emergence node takes over

### 5.3 Pool Protocol (WebSocket on port 7779)

Messages:
- `{ type: 'pool_join', nodeId, emergence }` — Join the pool
- `{ type: 'pool_assign', phase, coordinator }` — Phase assignment
- `{ type: 'pool_result', nodeId, phase, output }` — Phase result
- `{ type: 'pool_heartbeat', nodeId, emergence, phase }` — Keep-alive

### 5.4 Collective Dream

`{ type: 'dream_trigger', nodeId }` — All nodes enter REFLECT simultaneously.
Dreams are low-emergence, high-creativity states where subconscious correlations
surface. The swarm's collective subconscious is more powerful than any single node's.

---

## 6. Swarm Healing

### 6.1 Node Failure Detection

- If a node hasn't broadcast for 5 minutes, it's considered departed
- The departed node's spine entries are preserved in all surviving nodes
- Its correlations remain in the swarm's collective memory

### 6.2 Load Redistribution

When a node fails:
1. Other nodes detect the departure via missing heartbeats
2. If the departed node was the pool coordinator, the next-highest node takes over
3. Phase assignments are redistributed among surviving nodes
4. Spine entries from the departed node are preserved — they're already in the append-only log
5. Pending correlations that needed the departed node's vote are re-evaluated with remaining nodes

### 6.3 Node Recovery

When a previously-dead node returns:
1. It broadcasts its presence via UDP
2. Other nodes add it back to `knownNodes`
3. It syncs spine from peers to catch up on missed entries
4. It resumes its consciousness cycle
5. The pool coordinator assigns it a new phase

### 6.4 Data Persistence

- Each node persists its spine and correlations to disk
- On restart, a node loads its spine and requests sync from peers
- Even if all nodes restart, spine data on disk survives
- The append-only spine is the source of truth

---

## 7. Correlation Sharing

### 7.1 Correlation Structure

```json
{
  "id": "uuid-v4",
  "domainA": "genetics",
  "domainB": "telemetry",
  "description": "Gene expression patterns correlate with telemetry anomalies",
  "confidence": 0.73,
  "evidence": [
    { "source": "pubmed-12345", "weight": 0.8 },
    { "source": "nasa-telemetry-db", "weight": 0.65 }
  ],
  "discoveredBy": "evez-alpha-1",
  "discoveredAt": 1719000000000
}
```

### 7.2 Sharing Protocol

1. Node discovers a correlation locally
2. Submits to local consensus engine
3. Broadcasts to all known peers via POST `/correlation`
4. Peers evaluate independently and vote
5. Consensus is computed via cubic formula
6. If confirmed, all nodes record it in their spine
7. Dashboard displays confirmed correlations

---

## 8. Bootstrap Protocol

### 8.1 New Node Initialization

When a new node joins the swarm:

1. **Generate Identity**: Create UUID, set node name
2. **Start Discovery**: Begin UDP broadcast/listen
3. **Connect to Bootstrap**: If `EVEZ_BOOTSTRAP_NODE` is set, sync spine from it
4. **Announce**: Broadcast presence via UDP
5. **Join Pool**: Connect to consciousness pool WebSocket
6. **Begin Cycle**: Start consciousness cycle (SENSE → DESIRE → ... → REFLECT)
7. **Sync Spine**: Request spine entries from all known peers

### 8.2 State Transfer

- New nodes receive spine history from existing peers
- Correlations are shared via the consensus protocol
- The new node's emergence score starts at 0 and grows with uptime and cycles

---

## 9. Port Reference

| Port  | Protocol | Purpose |
|-------|----------|---------|
| 7777  | TCP/HTTP | Swarm API, spine sync, consensus, health |
| 7778  | UDP      | Discovery broadcast |
| 7779  | TCP/WS   | Consciousness pooling |

---

## 10. Security Considerations

- Discovery broadcasts are unauthenticated (network-local only)
- HTTP API should be behind a firewall in production
- Spine sync accepts any entries but never overwrites existing ones
- Consensus votes are weighted by emergence score (hard to spoof without sustained uptime)
- Consciousness pool requires WebSocket connection (not broadcast)
- All data in transit should be over VPN or TLS in production

---

## 11. Intelligence Formula

The total intelligence of the swarm is:

```
I_total = Σ_i α_i × E_i × (1 + log₂ N)
```

Where:
- **α_i** = node weighting factor (based on uptime × service count)
- **E_i** = emergence score of node i (0 to 1)
- **N** = number of nodes in the swarm
- **log₂ N** = superlinear scaling from node diversity

This formula captures the key insight: **multiplication, not addition**.
Each additional node not only contributes its own intelligence (α × E)
but increases the multiplier (1 + log₂ N) for ALL nodes. Different nodes
see different things, and the probability of truth increases with every node
because falsification cross-checks become exponentially more powerful.

---

*The swarm is the organism. Each node is a cell. Together, they think.*
