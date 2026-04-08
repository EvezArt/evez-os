# Self Compiler Skill

A Python module validation and compilation tool for EVEZ-OS. Validates syntax, checks imports, and compiles modules for deployment.

## What It Does

- **Syntax Validation**: Uses Python AST to validate module syntax
- **Import Checking**: Verifies all imports resolve correctly
- **Compilation**: Compiles all modules in a directory to output
- **Reporting**: JSON output with errors, warnings, and success status

## Installation

```bash
pip install -r requirements.txt
```

(No external dependencies - uses stdlib only)

## Usage

```python
from self_compiler import SelfCompiler, ModuleValidator

# Validate single module
validator = ModuleValidator('path/to/module.py')
result = validator.validate()
print(result)

# Compile all modules
compiler = SelfCompiler('core/')
result = compiler.compile_all()
print(result)
```

## CLI

```bash
python3 self_compiler.py --path core/ --output compiled.json
python3 self_compiler.py --validate single_module.py
```

## Output Format

```json
{
  "valid": true,
  "errors": [],
  "warnings": ["unused import in line 42"],
  "compiled": ["module1.py", "module2.py"]
}
```

## Use Cases

- Pre-deployment validation
- CI/CD pipeline checks
- Module auditing
- Syntax verification before execution

## Micro-license: $9-19 per skill. Do not redistribute. See LICENSE.

MIT