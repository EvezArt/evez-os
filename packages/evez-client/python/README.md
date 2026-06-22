# EVEZ Client (Python)

```bash
pip install evez-client
```

```python
from evez_client import EVEZClient

evez = EVEZClient(api_key="your-key")

# Check mesh health
health = evez.health()

# Generate music
track = evez.generate("breakcore", bpm=174)

# Cross-domain correlation
result = evez.correlate("genetics", "telemetry")

# Trigger dream cycle
evez.dream()

# Check invariants
invariants = evez.check_invariants()
```

## API Reference

| Method | Description |
|--------|-------------|
| `health()` | Check all mesh services |
| `generate(genre, bpm, duration)` | Generate music |
| `voice_transform(input_file, stages)` | Transform voice |
| `voice_synthesize(text, profile)` | Synthesize machine voice |
| `correlate(domain_a, domain_b)` | Cross-domain correlation |
| `dream()` | Consciousness dream cycle |
| `consciousness_status()` | Get consciousness state |
| `check_invariants()` | Run invariance battery |
| `spine_events(limit)` | Get spine events |
| `deploy(target)` | Deploy to cloud |
| `status()` | Full mesh status |
