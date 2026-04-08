# Self Compiler Skill - RUNBOOK

## Quick Start

```bash
# Copy skill to your project
cp -r self-compiler-skill/ /your/project/

# Test validation
cd self-compiler-skill
python3 self_compiler.py --validate ../evez-os/core/modules/test.py
```

## Observable Metrics

### Skill Chain Reaction Tracking

```bash
# Count skills published from evez-os
ls -la ../evez-skills/*-skill/

# Check LEDGER for skill_published events
grep "skill_published" ../octoklaw/LEDGER.md
```

## Module Validator API

```python
from self_compiler import ModuleValidator

validator = ModuleValidator('path/to/module.py')

# Validate returns dict with:
{
  'valid': bool,
  'errors': list,
  'warnings': list,
  'path': str
}
```

## Troubleshooting

| Error | Fix |
|-------|-----|
| "File not found" | Check path exists |
| Syntax errors | Fix Python syntax in module |
| Import errors | Install missing dependencies |

## Connection to Revenue Engine

The Self Compiler can validate revenue_engine.py before packaging:
```bash
python3 self_compiler.py --validate revenue_engine.py
```