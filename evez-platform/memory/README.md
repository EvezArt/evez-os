# evez memory — Append-Only, Hash-Chained, Semantically Searchable

## Overview

EVEZ's memory system uses the Spine as its foundation. All memories are append-only events in the hash-chained spine. Semantic search via embeddings makes any memory retrievable.

## Why This Is Better Than Files

| Feature | Files (OpenClaw) | EVEZ Memory |
|---------|-------------------|-------------|
| Integrity | Manual | Hash-chained (tamper-evident) |
| Search | grep/text search | Semantic vector search |
| History | Overwrites | Append-only (full history) |
| Distribution | Manual sync | Spine replication |
| Verification | None | Cryptographic proof |
| Scale | Single machine | Distributed across mesh |
| Query | Linear scan | Index-based + semantic |

## Memory Event Types

```json
// Fact
{
  "type": "memory.v1.Fact",
  "content": "Deployed v2.3.1 to production",
  "tags": ["deploy", "production"],
  "confidence": 1.0,
  "source": "act.coding-agent",
  "timestamp": "2026-06-22T14:00:00Z"
}

// Decision
{
  "type": "memory.v1.Decision",
  "content": "Chose PostgreSQL over MongoDB for event storage",
  "rationale": "ACID guarantees needed for spine integrity",
  "alternatives": ["MongoDB", "Cassandra"],
  "confidence": 0.9,
  "source": "think.architecture-agent"
}

// Lesson
{
  "type": "memory.v1.Lesson",
  "content": "Always verify Spine chain integrity before consensus",
  "context": "Node crash during consensus caused split-brain",
  "severity": "critical",
  "source": "learn.consciousness"
}

// Preference
{
  "type": "memory.v1.Preference",
  "content": "Prefer dark mode for all UI surfaces",
  "domain": "ui",
  "confidence": 0.8,
  "source": "reflect.self"
}
```

## API

```
POST /memory                    — Store a memory
GET  /memory/search             — Semantic search
GET  /memory/search/keyword      — Keyword search
GET  /memory/:id                — Get specific memory
GET  /memory/timeline           — Timeline of memories
GET  /memory/stats              — Memory statistics
POST /memory/consolidate        — Trigger consolidation (short→long term)
GET  /memory/verify             — Verify all memory integrity
```

## Semantic Search

Memories are embedded using a configurable embedding model:

```python
# Default: all-MiniLM-L6-v2 (fast, good quality)
# Alternative: text-embedding-3-small (OpenAI, better quality)
# Alternative: BGE-large (local, best quality)

results = await memory.search(
    query="What did I learn about distributed consensus?",
    top_k=10,
    min_similarity=0.7,
    filters={"tags": ["distributed", "consensus"]},
    time_range=("2026-01-01", "2026-06-22")
)
```

## Consolidation

Periodically, short-term memories are consolidated into long-term:

```
┌────────────────┐     ┌────────────────┐     ┌────────────────┐
│ Short-term     │────►│ Working memory │────►│ Long-term      │
│ (raw events)   │     │ (summarized)    │     │ (consolidated)  │
│ Last 24h       │     │ Last 30 days    │     │ Permanent       │
│ Full detail    │     │ Key points      │     │ Wisdom          │
└────────────────┘     └────────────────┘     └────────────────┘
```

Consolidation is itself a Spine event:

```json
{
  "type": "memory.v1.Consolidation",
  "source_events": ["spine_0x1...", "spine_0x2...", "spine_0x3..."],
  "summary": "Learned that distributed consensus requires careful leader election",
  "insights": ["Split-brain is more likely under high latency"],
  "source_hashes": ["sha256:a1b2...", "sha256:c3d4..."],
  "timestamp": "2026-06-22T14:00:00Z"
}
```

## Vector Index

Embeddings are stored in a local FAISS index (or remote Qdrant/Weaviate):

```yaml
memory:
  embedding_model: "all-MiniLM-L6-v2"
  vector_store: "faiss"  # or "qdrant", "weaviate"
  index_path: "/var/lib/evez/memory/faiss.idx"
  metadata_path: "/var/lib/evez/memory/metadata.json"
  consolidate_interval: 86400  # daily
  archive_after_days: 365
```

---

*evez-memory v1.0.0*
