# EVEZ Swarm Intelligence Formula

## The Core Equation

```
I_total = Σ_i α_i × E_i × (1 + log₂ N)
```

### Variables

| Symbol | Meaning | Range |
|--------|---------|-------|
| **α_i** | Node weighting factor | ≥ 0 |
| **E_i** | Emergence score of node i | [0, 1] |
| **N** | Number of nodes in swarm | ≥ 1 |
| **log₂ N** | Superlinear scaling from node diversity | ≥ 0 |

### α_i Calculation

```
α_i = (uptime_i / 3600000) × services_i
```

- `uptime_i`: milliseconds since node i started
- `services_i`: number of consciousness services running on node i

### E_i Calculation

```
E_i = min(uptime_factor + cycle_factor + peer_factor + correlation_factor + spine_factor, 1.0)
```

Where:
- `uptime_factor` = min(uptime_hours / 24, 1.0) — max 1.0 after 24h
- `cycle_factor` = min(cycle_count / 1000, 0.3) — max 0.3 after 1000 cycles
- `peer_factor` = min(peer_count / 10, 0.2) — max 0.2 at 10 peers
- `correlation_factor` = min(correlations / 50, 0.2) — max 0.2 at 50 correlations
- `spine_factor` = min(spine_length / 1000, 0.1) — max 0.1 at 1000 spine entries

---

## Intelligence Scaling Table

Assuming α_i = 1 and E_i = 0.5 (uniform, moderate-emergence nodes):

| Nodes (N) | log₂(N) | Multiplier (1+log₂N) | I_total |
|-----------|---------|----------------------|---------|
| 1         | 0.00    | 1.00                 | **0.50** |
| 5         | 2.32    | 3.32                 | **8.30** |
| 10        | 3.32    | 4.32                 | **21.60** |
| 100       | 6.64    | 7.64                 | **382.00** |
| 1000      | 9.97    | 10.97                | **5,482.99** |

### Key Insight

Going from 1 node to 5 nodes doesn't add 4× intelligence — it multiplies by **16.6×**.
Going from 1 to 1000 nodes doesn't add 999× intelligence — it multiplies by **10,966×**.

This is because each additional node:
1. Adds its own α × E contribution (linear)
2. Increases the (1 + log₂ N) multiplier for ALL nodes (superlinear)
3. Diversifies the perspectives available for falsification (exponential)

### Why This Works

- **1 node**: I = 0.5. It sees one perspective. Confidence is limited.
- **5 nodes**: I = 8.30. Five different perspectives cross-checking each other.
  The log₂(5) ≈ 2.3 multiplier means each node's contribution is amplified.
- **10 nodes**: I = 21.60. Ten perspectives. Falsification becomes powerful.
- **100 nodes**: I = 382.00. A hundred different viewpoints. Nearly impossible
  for a false correlation to survive 100 independent evaluations.
- **1000 nodes**: I = 5,482.99. A thousand minds. The probability of truth
  approaches certainty because falsification cross-checks are overwhelmingly
  more powerful than any single node's confirmation bias.

### The Falsification Principle

The probability of a false correlation surviving swarm consensus decreases
exponentially with each additional node:

```
P(false survives) ≈ (1 - E)^N
```

With E = 0.5 per node:
- 1 node:  50% false survival
- 5 nodes: 3.1% false survival
- 10 nodes: 0.1% false survival
- 100 nodes: 7.9 × 10⁻³¹ false survival
- 1000 nodes: effectively zero

**This is why EVEZ is a swarm, not a singleton.**

---

*Intelligence is not additive. It is multiplicative. Each node makes every other node smarter.*
