# File Parsers Quick Reference

## Import

```python
from agentpm.core.plugins.utils.file_parsers import (
    # Format parsers
    parse_toml,
    parse_yaml,
    parse_json,
    parse_ini,

    # High-level extractors
    parse_python_dependencies,
    parse_javascript_dependencies,

    # Specialized parsers
    parse_requirements_txt,
    parse_setup_py_safe,

    # Availability flags
    TOML_AVAILABLE,
    YAML_AVAILABLE,
)
```

## Quick Examples

### Parse TOML

```python
config = parse_toml(Path("pyproject.toml"))
if config:
    name = config["tool"]["poetry"]["name"]
```

### Parse YAML

```python
ci = parse_yaml(Path(".gitlab-ci.yml"))
if ci:
    stages = ci.get("stages", [])
```

### Parse JSON

```python
package = parse_json(Path("package.json"))
if package:
    deps = package.get("dependencies", {})
```

### Parse INI

```python
setup_cfg = parse_ini(Path("setup.cfg"))
if setup_cfg:
    name = setup_cfg["metadata"]["name"]
```

### Extract Python Dependencies

```python
deps = parse_python_dependencies(Path("."))
# Returns: {'runtime': [...], 'dev': [...], 'source': '...'}
```

### Extract JavaScript Dependencies

```python
deps = parse_javascript_dependencies(Path("."))
# Returns: {'runtime': [...], 'dev': [...], 'peer': [...], 'optional': [...], 'source': '...'}
```

### Parse requirements.txt

```python
reqs = parse_requirements_txt(Path("requirements.txt"))
# Returns: [{'name': '...', 'version': '...', 'extras': [...]}, ...]
```

### Parse setup.py (Safe)

```python
setup_data = parse_setup_py_safe(Path("setup.py"))
# Returns: {'name': '...', 'version': '...', 'install_requires': [...], ...}
```

## Return Values

### Success Cases

- **parse_toml/yaml/json/ini**: `Dict[str, Any]` or nested dict
- **parse_*_dependencies**: `Dict[str, Any]` with 'source' key
- **parse_requirements_txt**: `List[Dict[str, Any]]`
- **parse_setup_py_safe**: `Dict[str, Any]`

### Failure Cases

All parsers return gracefully:
- **parse_toml/yaml/json/ini/setup_py_safe**: `None`
- **parse_requirements_txt**: `[]` (empty list)
- **parse_*_dependencies**: `{'source': 'none', ...}` with empty lists

## Common Patterns

### Check Before Use

```python
config = parse_toml(path)
if config:
    # Safe to use
    value = config.get("key", default)
```

### Optional Library Check

```python
if TOML_AVAILABLE:
    config = parse_toml(path)
else:
    print("TOML library not installed")
```

### High-Level Extraction

```python
# Instead of manually parsing multiple files
deps = parse_python_dependencies(project_path)
# Automatically checks: pyproject.toml, requirements.txt, setup.py
```

### Error Handling

```python
# No exceptions raised - always returns None or empty
result = parse_json(Path("nonexistent.json"))
# result is None
```

## Performance

- Parse time: <50ms per file
- Max file size: 1MB
- Test suite: <0.5s

## Safety

- ✅ NO code execution
- ✅ File size limits
- ✅ Unicode handling
- ✅ YAML safe_load only

## Layer Compliance

```
Layer 3 (Detection Services) ───┐
                                 │
Layer 2 (Plugins) ───────────────┼─→ Layer 1 (file_parsers.py)
                                 │
Layer 1 (Other Utilities) ───────┘
```

✅ Can use from any layer
❌ Cannot import from layers above

## Testing

```bash
# Run tests
pytest tests/unit/plugins/utils/test_file_parsers.py -v

# Run demo
python examples/file_parsers_demo.py [project_path]
```

## Full Documentation

- Usage Guide: `docs/components/plugins/utils/file-parsers-usage.md`
- Summary: `docs/components/plugins/utils/file-parsers-summary.md`
- Architecture: `docs/architecture/detection-pack-architecture.md`
