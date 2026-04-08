# EVEZ Awareness Engine Skill

Real-time awareness scanning skill for AI agents. Monitors crypto/market signals, tech news, social trends, and user context with automatic alert generation.

## What It Does

- **Market Scanning**: Monitor crypto, stocks, and financial signals
- **News Aggregation**: Track tech headlines and academic releases
- **Causal Chain Building**: Connect events across time
- **Alert Generation**: Notify on opportunities automatically

## Installation

```bash
pip install -r requirements.txt
```

(No external deps - uses stdlib)

## Usage

```python
from awareness_engine import AwarenessEngine

engine = AwarenessEngine()

# Run a scan
results = engine.scan("crypto")

# Get alerts
alerts = engine.get_alerts()

# Get causal chains
chains = engine.get_causal_chains()
```

## CLI

```bash
python3 awareness_engine.py --scan crypto
python3 awareness_engine.py --alerts
python3 awareness_engine.py --status
```

## Output

```json
{
  "scan_results": [...],
  "alerts": [...],
  "causal_chains": [...],
  "timestamp": "2026-04-08T..."
}
```

## Use Cases

- Trading signal generation
- Trend detection
- Opportunity alerting
- Research automation

## Micro-license: $9-19 per skill. Do not redistribute. See LICENSE.

MIT