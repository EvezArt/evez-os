# Decentralized Spine — Distributed Append-Only Event Chain

## Overview

The Spine is EVEZ's shared memory — an append-only, hash-chained event log that is NOT stored on one machine. Each node holds a shard. Any node can verify the chain. New events are appended via distributed consensus (Raft-like, but append-only).

## Design Principles

1. **Append-only** — Events are never modified or deleted
2. **Hash-chained** — Each event references the hash of the previous event
3. **Distributed** — No single machine holds the complete chain
4. **Verifiable** — Any node can verify any event's integrity
5. **Byzantine-tolerant** — Survives up to f malicious nodes out of 3f+1

## Data Model

### Event Structure

```json
{
  "id": "spine_0x7f3a...",
  "index": 42847,
  "timestamp": "2026-06-22T14:00:00.000Z",
  "prev_hash": "sha256:a1b2c3d4...",
  "hash": "sha256:e5f6g7h8...",
  "type": "sense.v1.PerceptionEvent",
  "payload": { ... },
  "shard": 3,
  "signatures": [
    { "node": "node-a", "sig": "ed25519:..." },
    { "node": "node-b", "sig": "ed25519:..." },
    { "node": "node-c", "sig": "ed25519:..." }
  ],
  "consensus": {
    "term": 42,
    "leader": "node-b",
    "commit_index": 42845
  }
}
```

### Hash Chain

```
genesis → e0 → e1 → e2 → ... → eN
            ↘ shard[0] holds even indices
            ↘ shard[1] holds odd indices
            ↘ shard[2] holds indices ≡ 0 mod 3
            ↘ ... (overlap for redundancy)
```

Each event's hash = SHA-256(index + prev_hash + type + SHA-256(payload))

## Sharding Strategy

### Deterministic Sharding

Events are assigned to shards by: `shard_id = event.index % num_shards`

### Redundancy

Each event is stored on **R** shards (default R=3):
```
primary_shard = index % N
replica_shards = [(primary_shard + k) % N for k in range(1, R)]
```

### Shard Rebalancing

When nodes join/leave, shards are rebalanced:
1. New node announces itself via mesh discovery
2. Leader runs shard redistribution algorithm
3. Missing replicas are rebuilt from existing replicas
4. No data is ever lost (append-only means no deletions during rebalance)

## Consensus Protocol (SpineRaft)

Modified Raft for append-only semantics:

### Leader Election
1. Nodes send `RequestVote` with their last known index
2. Candidate with the **highest committed index** wins (data-richness heuristic)
3. Term increments on each election
4. Pre-vote phase prevents disruptive elections

### Log Replication
1. Leader receives append request from any pipeline stage
2. Leader appends to local log, sends `AppendEntries` to followers
3. Followers verify: `prev_hash` matches, `index` is sequential
4. Once majority acknowledges, event is **committed**
5. Committed events are **immutable** — they can never be rolled back

### Key Difference from Standard Raft
- **No log truncation** — Followers never delete entries. If they have extra uncommitted entries, they keep them as "fork candidates"
- **No snapshot compression** — Old entries are archived to cold storage but never deleted from the hash chain
- **Merkle checkpoints** — Every 1000 entries, a Merkle root is computed and signed by the cluster. This allows fast verification of large ranges.

## Verification

### Single Event Verification

Any node can verify an event:
```python
def verify_event(event, prev_event):
    # 1. Hash chain integrity
    computed_hash = sha256(
        str(event.index).encode() +
        prev_event.hash.encode() +
        event.type.encode() +
        sha256(json.dumps(event.payload).encode()).encode()
    )
    assert event.hash == computed_hash
    
    # 2. Sequential index
    assert event.index == prev_event.index + 1
    
    # 3. Signatures (at least f+1 valid)
    valid_sigs = sum(1 for s in event.signatures if verify_sig(s, event.hash))
    assert valid_sigs >= f + 1
    
    return True
```

### Range Verification (Merkle Checkpoints)

```python
def verify_range(start_index, end_index, merkle_root, signatures):
    # Rebuild Merkle tree from events in range
    events = fetch_events(start_index, end_index)
    tree = MerkleTree([e.hash for e in events])
    
    # Verify root matches
    assert tree.root == merkle_root
    
    # Verify signatures (at least f+1)
    valid_sigs = sum(1 for s in signatures if verify_sig(s, merkle_root))
    assert valid_sigs >= f + 1
    
    return True
```

## Query Interface

### Local Query (fast)
```python
spine.query(
    type="sense.v1.PerceptionEvent",
    since="2026-06-22T00:00:00Z",
    limit=100
)
```

### Distributed Query (comprehensive)
```python
spine.distributed_query(
    type="think.v1.ThoughtChain",
    filter={"conclusion.contains": "deploy"},
    consensus_required=True  # verify across shards
)
```

### Semantic Search
Events are embedded into vectors and indexed. Semantic search queries the embedding index:
```python
spine.semantic_search(
    query="what did I learn about distributed systems?",
    top_k=10,
    min_similarity=0.7
)
```

## Compaction & Archive

Old events are archived but never deleted:

```
┌─────────────────┬─────────────────┬─────────────────┐
│  Hot (0-30 days) │  Warm (30-365d) │  Cold (365d+)    │
│  Full replicas  │  Compressed     │  Archive format   │
│  In-memory      │  On SSD         │  On HDD/object    │
│  <10ms query    │  <100ms query   │  <5s query        │
└─────────────────┴─────────────────┴─────────────────┘
```

## Anti-Entropy

Background process that keeps shards consistent:

1. **Merkle tree exchange** — Nodes exchange Merkle roots for each shard
2. **Difference detection** — Roots that differ trigger sync
3. **Missing event recovery** — Pull missing events from peers
4. **Signature repair** — Re-collect signatures for events below threshold

## Security

- **All events signed** by the originating node (Ed25519)
- **All inter-node traffic encrypted** (NaCl box)
- **Write authorization** — Only authorized pipeline stages can append
- **Read authorization** — Configurable per-shard (public, internal, restricted)
- **Immutability proofs** — Any third party can verify the chain is untampered

---

*Spine Version: 1.0.0*
*Last Updated: 2026-06-22*
