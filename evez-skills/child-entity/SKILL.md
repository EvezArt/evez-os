# EVEZ Child Entity

Generate 5 hypotheses — from obvious to unexpected. Rate novelty + feasibility.

## Input

```json
{
  "objective": "string"
}
```

## Output

```json
{
  "hypotheses": [
    {"id": "h1", "text": "...", "novelty": 5, "feasibility": 4, "score": 9},
    ...
  ]
}
```

## Usage

```python
from child_entity import ChildEntity
child = ChildEntity()
results = child.generate("Solve the problem")
```

## Rating

- **Novelty** (1-5): How unexpected is this?
- **Feasibility** (1-5): Can this actually work?
- **Score**: Novelty + Feasibility

Built by EVEZ-ART | Part of the EVEZ Sensory Engine