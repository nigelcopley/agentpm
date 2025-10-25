# File Parsers Usage Guide

## Overview

The `file_parsers.py` module provides Layer 1 (Shared Utilities) file parsing primitives for the APM (Agent Project Manager) Detection Pack. This module has **NO dependencies** on plugins or detection services, making it safe to use from any layer.

**Location**: `agentpm/core/plugins/utils/file_parsers.py`

## Architecture Compliance

### Three-Layer Pattern

```
Layer 3: Detection Services (SBOM, Dependency Analysis)
    ↓ uses
Layer 2: Plugins (Language Plugins, Framework Plugins)
    ↓ uses
Layer 1: Shared Utilities ← file_parsers.py (YOU ARE HERE)
```

**Key Principle**: Layer 1 utilities are **pure functions** with no upward dependencies.

## Available Parsers

### 1. TOML Parser

```python
from pathlib import Path
from agentpm.core.plugins.utils.file_parsers import parse_toml

# Parse pyproject.toml
config = parse_toml(Path("pyproject.toml"))
if config:
    # Poetry format
    poetry_deps = config.get("tool", {}).get("poetry", {}).get("dependencies", {})

    # PEP 621 format
    project_deps = config.get("project", {}).get("dependencies", [])
```

**Handles**:
- `pyproject.toml` (Poetry, PEP 621)
- `Cargo.toml` (Rust)
- Configuration files

**Features**:
- Python 3.11+ `tomllib` support
- Graceful fallback to `tomli` or `toml`
- Returns `None` if library unavailable

### 2. YAML Parser

```python
from agentpm.core.plugins.utils.file_parsers import parse_yaml

# Parse CI/CD configuration
gitlab_ci = parse_yaml(Path(".gitlab-ci.yml"))
if gitlab_ci:
    stages = gitlab_ci.get("stages", [])
    jobs = {k: v for k, v in gitlab_ci.items() if isinstance(v, dict)}
```

**Handles**:
- `.gitlab-ci.yml`
- `.github/workflows/*.yml`
- `docker-compose.yml`
- Configuration files

**Safety**: Uses `yaml.safe_load()` only (no code execution)

### 3. JSON Parser

```python
from agentpm.core.plugins.utils.file_parsers import parse_json

# Parse package.json
package = parse_json(Path("package.json"))
if package:
    name = package.get("name")
    version = package.get("version")
    deps = package.get("dependencies", {})
```

**Handles**:
- `package.json`
- `tsconfig.json`
- `.eslintrc.json`
- Any JSON configuration

### 4. INI/CFG Parser

```python
from agentpm.core.plugins.utils.file_parsers import parse_ini

# Parse setup.cfg
setup_cfg = parse_ini(Path("setup.cfg"))
if setup_cfg:
    metadata = setup_cfg.get("metadata", {})
    name = metadata.get("name")
```

**Handles**:
- `setup.cfg`
- `tox.ini`
- `.coveragerc`
- INI-format files

### 5. Requirements.txt Parser

```python
from agentpm.core.plugins.utils.file_parsers import parse_requirements_txt

# Parse requirements.txt
requirements = parse_requirements_txt(Path("requirements.txt"))

for dep in requirements:
    print(f"{dep['name']} {dep['version']}")
    if dep.get('extras'):
        print(f"  Extras: {', '.join(dep['extras'])}")
    if dep.get('url'):
        print(f"  Git URL: {dep['url']}")
```

**Handles**:
- Simple: `package==1.0.0`
- Operators: `package>=1.0.0,<2.0.0`
- Extras: `package[dev,test]==1.0.0`
- Git URLs: `git+https://...#egg=name`
- Local paths: `-e ./local_package`

### 6. Setup.py Safe Parser

```python
from agentpm.core.plugins.utils.file_parsers import parse_setup_py_safe

# Parse setup.py WITHOUT executing it
setup_data = parse_setup_py_safe(Path("setup.py"))
if setup_data:
    name = setup_data.get("name")
    version = setup_data.get("version")
    install_requires = setup_data.get("install_requires", [])
    extras_require = setup_data.get("extras_require", {})
```

**Safety**: Uses AST parsing only - **NO CODE EXECUTION**

### 7. Python Dependencies Extractor

```python
from agentpm.core.plugins.utils.file_parsers import parse_python_dependencies

# Extract ALL Python dependencies from project
deps = parse_python_dependencies(Path("."))

print(f"Source: {deps['source']}")  # pyproject.toml | requirements.txt | setup.py | none
print(f"Runtime: {deps['runtime']}")  # List of package names
print(f"Dev: {deps['dev']}")  # List of dev package names
```

**Priority order**:
1. `pyproject.toml` (Poetry or PEP 621)
2. `requirements.txt`
3. `setup.py` (AST-based)

**Also checks**:
- `requirements-dev.txt`
- `dev-requirements.txt`
- `test-requirements.txt`

### 8. JavaScript Dependencies Extractor

```python
from agentpm.core.plugins.utils.file_parsers import parse_javascript_dependencies

# Extract JavaScript/Node dependencies
deps = parse_javascript_dependencies(Path("."))

print(f"Source: {deps['source']}")  # package.json | none
print(f"Runtime: {deps['runtime']}")
print(f"Dev: {deps['dev']}")
print(f"Peer: {deps['peer']}")
print(f"Optional: {deps['optional']}")
```

## Layer 2: Plugin Usage Examples

### Python Plugin

```python
# agentpm/core/plugins/languages/python_plugin.py (Layer 2)
from agentpm.core.plugins.utils.file_parsers import (
    parse_python_dependencies,
    parse_toml
)


class PythonPlugin:
    def extract_facts(self, project_path: Path) -> Dict[str, Any]:
        facts = {}

        # Extract dependencies
        deps = parse_python_dependencies(project_path)
        facts['dependencies'] = {
            'runtime': deps['runtime'],
            'dev': deps['dev'],
            'source': deps['source']
        }

        # Extract project metadata
        pyproject = parse_toml(project_path / 'pyproject.toml')
        if pyproject:
            facts['name'] = pyproject.get('project', {}).get('name')
            facts['version'] = pyproject.get('project', {}).get('version')

        return facts
```

### JavaScript Plugin

```python
# agentpm/core/plugins/languages/javascript_plugin.py (Layer 2)
from agentpm.core.plugins.utils.file_parsers import (
    parse_javascript_dependencies,
    parse_json
)


class JavaScriptPlugin:
    def extract_facts(self, project_path: Path) -> Dict[str, Any]:
        facts = {}

        # Extract dependencies
        deps = parse_javascript_dependencies(project_path)
        facts['dependencies'] = deps

        # Extract scripts
        package_json = parse_json(project_path / 'package.json')
        if package_json:
            facts['scripts'] = package_json.get('scripts', {})
            facts['engines'] = package_json.get('engines', {})

        return facts
```

## Layer 3: Detection Service Usage

### SBOM Generator

```python
# agentpm/core/detection/sbom_service.py (Layer 3)
from agentpm.core.plugins.utils.file_parsers import (
    parse_python_dependencies,
    parse_javascript_dependencies
)


class SBOMService:
    def generate(self, project_path: Path) -> Dict[str, Any]:
        sbom = {
            'components': [],
            'dependencies': []
        }

        # Collect Python dependencies
        py_deps = parse_python_dependencies(project_path)
        for dep in py_deps['runtime']:
            sbom['components'].append({
                'type': 'library',
                'name': dep,
                'ecosystem': 'pypi'
            })

        # Collect JavaScript dependencies
        js_deps = parse_javascript_dependencies(project_path)
        for dep in js_deps['runtime']:
            sbom['components'].append({
                'type': 'library',
                'name': dep,
                'ecosystem': 'npm'
            })

        return sbom
```

## Error Handling

All parsers handle errors gracefully:

```python
# Returns None on:
# - File not found
# - Parse errors
# - Invalid syntax
# - Permission errors
# - File too large (>1MB)
# - Library not available (TOML, YAML)

result = parse_toml(Path("missing.toml"))
if result is None:
    # Handle gracefully - don't crash
    print("Could not parse TOML")
```

## Performance Characteristics

- **Parse time**: <50ms per file
- **Max file size**: 1MB (safety limit)
- **Regex compilation**: Pre-compiled patterns for efficiency
- **Memory**: Efficient streaming where possible

## Testing

All 8 public functions have comprehensive test coverage:

```bash
# Run tests
pytest tests/unit/plugins/utils/test_file_parsers.py -v

# 43 tests covering:
# - Valid parsing
# - Error handling
# - Edge cases
# - Unicode support
# - Large files
# - Permission errors
# - Integration scenarios
```

## Optional Dependencies

### TOML Support

```python
from agentpm.core.plugins.utils.file_parsers import TOML_AVAILABLE

if TOML_AVAILABLE:
    result = parse_toml(path)
else:
    print("TOML library not installed")
    # Fallback to manual parsing or skip
```

**Install**:
```bash
pip install tomli  # Python <3.11
# Python 3.11+ includes tomllib
```

### YAML Support

```python
from agentpm.core.plugins.utils.file_parsers import YAML_AVAILABLE

if YAML_AVAILABLE:
    result = parse_yaml(path)
else:
    print("PyYAML not installed")
    # Fallback or skip
```

**Install**:
```bash
pip install pyyaml
```

## Best Practices

### 1. Always Check Return Values

```python
# ❌ Bad: Assume success
config = parse_toml(path)
name = config["project"]["name"]  # May crash

# ✅ Good: Check for None
config = parse_toml(path)
if config:
    name = config.get("project", {}).get("name")
```

### 2. Use High-Level Extractors

```python
# ❌ Bad: Parse files manually
pyproject = parse_toml(path / "pyproject.toml")
deps = pyproject["tool"]["poetry"]["dependencies"]

# ✅ Good: Use high-level extractor
deps = parse_python_dependencies(path)
# Handles Poetry, PEP 621, requirements.txt, setup.py
```

### 3. Handle Missing Libraries

```python
# ✅ Good: Check availability
if YAML_AVAILABLE:
    config = parse_yaml(path)
else:
    # Fallback logic
    print("Skipping YAML parsing")
```

### 4. Layer Compliance

```python
# ✅ Layer 1 → Layer 1: OK
from agentpm.core.plugins.utils.file_parsers import parse_toml

# ✅ Layer 2 → Layer 1: OK
from agentpm.core.plugins.utils.file_parsers import parse_toml

# ✅ Layer 3 → Layer 1: OK
from agentpm.core.plugins.utils.file_parsers import parse_toml

# ❌ Layer 1 → Layer 2: FORBIDDEN
# Never import plugins from file_parsers.py
```

## Anti-Patterns

### ❌ Executing setup.py

```python
# NEVER DO THIS
exec(open("setup.py").read())  # Code execution vulnerability
```

### ❌ Unsafe YAML Loading

```python
# NEVER DO THIS
yaml.load(f)  # Use yaml.safe_load() only
```

### ❌ Ignoring File Size

```python
# NEVER DO THIS
with open(huge_file) as f:
    data = json.load(f)  # May crash on 100MB file
```

**Our parsers handle this**:
- Check file size before reading
- Limit to 1MB (configurable)
- Return `None` for oversized files

## Related Documentation

- **Architecture**: `docs/architecture/detection-pack-architecture.md`
- **Plugin Development**: `docs/components/plugins/plugin-development.md`
- **Detection Services**: `docs/components/detection/detection-services.md`
- **Testing Guide**: `docs/testing/unit-testing-guide.md`

## Version

- **Module Version**: 1.0.0
- **Last Updated**: 2025-10-24
- **Python Compatibility**: 3.9+
- **Dependencies**: Optional (tomli, pyyaml)
