"""
Unit Tests for File Parsing Utilities

Tests for agentpm/core/plugins/utils/file_parsers.py

Coverage targets:
- >90% line coverage
- All parsing functions
- Error handling paths
- Edge cases

Test Structure (AAA Pattern):
- Arrange: Setup test data
- Act: Call function under test
- Assert: Verify expected behavior
"""

import json
import tempfile
from pathlib import Path
from typing import Dict, Any

import pytest

from agentpm.utils.file_parsers import (
    parse_toml,
    parse_yaml,
    parse_json,
    parse_ini,
    parse_python_dependencies,
    parse_javascript_dependencies,
    parse_requirements_txt,
    parse_setup_py_safe,
    TOML_AVAILABLE,
    YAML_AVAILABLE,
)


# ========== Fixtures ==========

@pytest.fixture
def temp_dir(tmp_path):
    """Create temporary directory for test files"""
    return tmp_path


@pytest.fixture
def sample_pyproject_toml(temp_dir):
    """Create sample pyproject.toml (Poetry format)"""
    content = """
[tool.poetry]
name = "test-package"
version = "1.0.0"

[tool.poetry.dependencies]
python = "^3.9"
requests = "^2.28.0"
click = ">=8.0.0"

[tool.poetry.group.dev.dependencies]
pytest = "^7.2.0"
black = "^22.0.0"
"""
    path = temp_dir / "pyproject.toml"
    path.write_text(content)
    return path


@pytest.fixture
def sample_pyproject_pep621(temp_dir):
    """Create sample pyproject.toml (PEP 621 format)"""
    content = """
[project]
name = "test-package"
version = "1.0.0"
dependencies = [
    "requests>=2.28.0",
    "click>=8.0.0"
]

[project.optional-dependencies]
dev = ["pytest>=7.2.0", "black>=22.0.0"]
"""
    path = temp_dir / "pyproject_pep621.toml"
    path.write_text(content)
    return path


@pytest.fixture
def sample_package_json(temp_dir):
    """Create sample package.json"""
    data = {
        "name": "test-package",
        "version": "1.0.0",
        "dependencies": {
            "express": "^4.18.0",
            "lodash": "^4.17.21"
        },
        "devDependencies": {
            "jest": "^29.0.0",
            "eslint": "^8.0.0"
        },
        "peerDependencies": {
            "react": ">=17.0.0"
        },
        "optionalDependencies": {
            "fsevents": "^2.3.0"
        }
    }
    path = temp_dir / "package.json"
    path.write_text(json.dumps(data, indent=2))
    return path


@pytest.fixture
def sample_requirements_txt(temp_dir):
    """Create sample requirements.txt"""
    content = """
# Core dependencies
requests==2.28.1
click>=8.0.0,<9.0.0
pydantic[email,dotenv]==1.10.2

# Database
sqlalchemy>=1.4.0

# Git dependency
-e git+https://github.com/user/repo.git#egg=custom-package

# Local dependency
-e ./local_package

# Comment line
# Another comment

# Empty line above
flask
"""
    path = temp_dir / "requirements.txt"
    path.write_text(content)
    return path


@pytest.fixture
def sample_setup_py(temp_dir):
    """Create sample setup.py"""
    content = """
from setuptools import setup, find_packages

setup(
    name="test-package",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "requests>=2.28.0",
        "click>=8.0.0"
    ],
    extras_require={
        "dev": ["pytest>=7.2.0", "black>=22.0.0"],
        "test": ["coverage>=6.0.0"]
    },
    python_requires=">=3.9"
)
"""
    path = temp_dir / "setup.py"
    path.write_text(content)
    return path


@pytest.fixture
def sample_setup_cfg(temp_dir):
    """Create sample setup.cfg"""
    content = """
[metadata]
name = test-package
version = 1.0.0
author = Test Author
description = A test package

[options]
packages = find:
python_requires = >=3.9

[options.packages.find]
exclude = tests*
"""
    path = temp_dir / "setup.cfg"
    path.write_text(content)
    return path


@pytest.fixture
def sample_yaml(temp_dir):
    """Create sample YAML file"""
    content = """
stages:
  - build
  - test
  - deploy

build_job:
  stage: build
  script:
    - echo "Building..."
    - make build

test_job:
  stage: test
  script:
    - pytest tests/
"""
    path = temp_dir / ".gitlab-ci.yml"
    path.write_text(content)
    return path


# ========== Test parse_toml ==========

@pytest.mark.skipif(not TOML_AVAILABLE, reason="TOML library not available")
def test_parse_toml_poetry_format(sample_pyproject_toml):
    """Test parsing Poetry-format pyproject.toml"""
    # Act
    result = parse_toml(sample_pyproject_toml)

    # Assert
    assert result is not None
    assert "tool" in result
    assert "poetry" in result["tool"]
    assert result["tool"]["poetry"]["name"] == "test-package"
    assert result["tool"]["poetry"]["version"] == "1.0.0"


@pytest.mark.skipif(not TOML_AVAILABLE, reason="TOML library not available")
def test_parse_toml_pep621_format(sample_pyproject_pep621):
    """Test parsing PEP 621 format pyproject.toml"""
    # Act
    result = parse_toml(sample_pyproject_pep621)

    # Assert
    assert result is not None
    assert "project" in result
    assert result["project"]["name"] == "test-package"
    assert len(result["project"]["dependencies"]) == 2


def test_parse_toml_nonexistent_file(temp_dir):
    """Test parsing nonexistent TOML file returns None"""
    # Arrange
    path = temp_dir / "nonexistent.toml"

    # Act
    result = parse_toml(path)

    # Assert
    assert result is None


@pytest.mark.skipif(not TOML_AVAILABLE, reason="TOML library not available")
def test_parse_toml_invalid_syntax(temp_dir):
    """Test parsing invalid TOML returns None"""
    # Arrange
    path = temp_dir / "invalid.toml"
    path.write_text("this is not valid TOML ][")

    # Act
    result = parse_toml(path)

    # Assert
    assert result is None


@pytest.mark.skipif(not TOML_AVAILABLE, reason="TOML library not available")
def test_parse_toml_large_file(temp_dir):
    """Test parsing file >1MB returns None (safety check)"""
    # Arrange
    path = temp_dir / "large.toml"
    # Create 2MB file
    path.write_text("key = 'value'\n" * 100_000)

    # Act
    result = parse_toml(path)

    # Assert
    assert result is None


# ========== Test parse_yaml ==========

@pytest.mark.skipif(not YAML_AVAILABLE, reason="YAML library not available")
def test_parse_yaml_valid_file(sample_yaml):
    """Test parsing valid YAML file"""
    # Act
    result = parse_yaml(sample_yaml)

    # Assert
    assert result is not None
    assert "stages" in result
    assert len(result["stages"]) == 3
    assert "build" in result["stages"]


def test_parse_yaml_nonexistent_file(temp_dir):
    """Test parsing nonexistent YAML file returns None"""
    # Arrange
    path = temp_dir / "nonexistent.yml"

    # Act
    result = parse_yaml(path)

    # Assert
    assert result is None


@pytest.mark.skipif(not YAML_AVAILABLE, reason="YAML library not available")
def test_parse_yaml_invalid_syntax(temp_dir):
    """Test parsing invalid YAML returns None"""
    # Arrange
    path = temp_dir / "invalid.yml"
    path.write_text("key: value\n  invalid indentation\n- list item")

    # Act
    result = parse_yaml(path)

    # Assert
    assert result is None


@pytest.mark.skipif(not YAML_AVAILABLE, reason="YAML library not available")
def test_parse_yaml_empty_file(temp_dir):
    """Test parsing empty YAML file returns empty dict"""
    # Arrange
    path = temp_dir / "empty.yml"
    path.write_text("")

    # Act
    result = parse_yaml(path)

    # Assert
    assert result == {}


# ========== Test parse_json ==========

def test_parse_json_valid_file(sample_package_json):
    """Test parsing valid JSON file"""
    # Act
    result = parse_json(sample_package_json)

    # Assert
    assert result is not None
    assert result["name"] == "test-package"
    assert "dependencies" in result
    assert len(result["dependencies"]) == 2


def test_parse_json_nonexistent_file(temp_dir):
    """Test parsing nonexistent JSON file returns None"""
    # Arrange
    path = temp_dir / "nonexistent.json"

    # Act
    result = parse_json(path)

    # Assert
    assert result is None


def test_parse_json_invalid_syntax(temp_dir):
    """Test parsing invalid JSON returns None"""
    # Arrange
    path = temp_dir / "invalid.json"
    path.write_text("{ invalid json }")

    # Act
    result = parse_json(path)

    # Assert
    assert result is None


def test_parse_json_non_dict_returns_none(temp_dir):
    """Test parsing JSON array returns None (expects dict)"""
    # Arrange
    path = temp_dir / "array.json"
    path.write_text('["item1", "item2"]')

    # Act
    result = parse_json(path)

    # Assert
    assert result is None


# ========== Test parse_ini ==========

def test_parse_ini_valid_file(sample_setup_cfg):
    """Test parsing valid INI/CFG file"""
    # Act
    result = parse_ini(sample_setup_cfg)

    # Assert
    assert result is not None
    assert "metadata" in result
    assert result["metadata"]["name"] == "test-package"
    assert result["metadata"]["version"] == "1.0.0"


def test_parse_ini_nonexistent_file(temp_dir):
    """Test parsing nonexistent INI file returns None"""
    # Arrange
    path = temp_dir / "nonexistent.cfg"

    # Act
    result = parse_ini(path)

    # Assert
    assert result is None


def test_parse_ini_invalid_syntax(temp_dir):
    """Test parsing invalid INI returns None"""
    # Arrange
    path = temp_dir / "invalid.cfg"
    # Invalid: no section header
    path.write_text("key = value")

    # Act
    result = parse_ini(path)

    # Assert
    assert result is None


# ========== Test parse_requirements_txt ==========

def test_parse_requirements_txt_valid_file(sample_requirements_txt):
    """Test parsing valid requirements.txt"""
    # Act
    result = parse_requirements_txt(sample_requirements_txt)

    # Assert
    assert len(result) > 0

    # Check simple requirement
    requests_dep = next((d for d in result if d['name'] == 'requests'), None)
    assert requests_dep is not None
    assert requests_dep['version'] == '==2.28.1'
    assert requests_dep['extras'] is None

    # Check requirement with extras
    pydantic_dep = next((d for d in result if d['name'] == 'pydantic'), None)
    assert pydantic_dep is not None
    assert pydantic_dep['extras'] == ['email', 'dotenv']

    # Check version range
    click_dep = next((d for d in result if d['name'] == 'click'), None)
    assert click_dep is not None
    assert '>=8.0.0' in click_dep['version']

    # Check git dependency
    git_dep = next((d for d in result if d.get('url')), None)
    assert git_dep is not None
    assert 'custom-package' in git_dep['name']

    # Check local dependency
    local_dep = next((d for d in result if d.get('path')), None)
    assert local_dep is not None


def test_parse_requirements_txt_nonexistent_file(temp_dir):
    """Test parsing nonexistent requirements.txt returns empty list"""
    # Arrange
    path = temp_dir / "nonexistent.txt"

    # Act
    result = parse_requirements_txt(path)

    # Assert
    assert result == []


def test_parse_requirements_txt_empty_file(temp_dir):
    """Test parsing empty requirements.txt returns empty list"""
    # Arrange
    path = temp_dir / "empty.txt"
    path.write_text("")

    # Act
    result = parse_requirements_txt(path)

    # Assert
    assert result == []


def test_parse_requirements_txt_comments_only(temp_dir):
    """Test parsing requirements.txt with only comments"""
    # Arrange
    path = temp_dir / "comments.txt"
    path.write_text("# Comment 1\n# Comment 2\n\n")

    # Act
    result = parse_requirements_txt(path)

    # Assert
    assert result == []


def test_parse_requirements_txt_no_version(temp_dir):
    """Test parsing requirement without version specifier"""
    # Arrange
    path = temp_dir / "no_version.txt"
    path.write_text("flask\ndjango\n")

    # Act
    result = parse_requirements_txt(path)

    # Assert
    assert len(result) == 2
    assert result[0]['name'] == 'flask'
    assert result[0]['version'] == 'any'


# ========== Test parse_setup_py_safe ==========

def test_parse_setup_py_safe_valid_file(sample_setup_py):
    """Test parsing valid setup.py"""
    # Act
    result = parse_setup_py_safe(sample_setup_py)

    # Assert
    assert result is not None
    assert result["name"] == "test-package"
    assert result["version"] == "1.0.0"
    assert len(result["install_requires"]) == 2
    assert "dev" in result["extras_require"]
    assert result["python_requires"] == ">=3.9"


def test_parse_setup_py_safe_nonexistent_file(temp_dir):
    """Test parsing nonexistent setup.py returns None"""
    # Arrange
    path = temp_dir / "nonexistent.py"

    # Act
    result = parse_setup_py_safe(path)

    # Assert
    assert result is None


def test_parse_setup_py_safe_invalid_syntax(temp_dir):
    """Test parsing setup.py with syntax errors returns None"""
    # Arrange
    path = temp_dir / "invalid.py"
    path.write_text("this is not valid python ][")

    # Act
    result = parse_setup_py_safe(path)

    # Assert
    assert result is None


def test_parse_setup_py_safe_no_setup_call(temp_dir):
    """Test parsing Python file without setup() call returns None"""
    # Arrange
    path = temp_dir / "no_setup.py"
    path.write_text("print('Hello World')")

    # Act
    result = parse_setup_py_safe(path)

    # Assert
    assert result is None


def test_parse_setup_py_safe_setuptools_setup(temp_dir):
    """Test parsing setup.py with setuptools.setup() call"""
    # Arrange
    content = """
import setuptools

setuptools.setup(
    name="test-package",
    version="1.0.0"
)
"""
    path = temp_dir / "setuptools_setup.py"
    path.write_text(content)

    # Act
    result = parse_setup_py_safe(path)

    # Assert
    assert result is not None
    assert result["name"] == "test-package"


# ========== Test parse_python_dependencies ==========

def test_parse_python_dependencies_poetry_format(temp_dir, sample_pyproject_toml):
    """Test extracting dependencies from Poetry format"""
    # Act
    result = parse_python_dependencies(temp_dir)

    # Assert
    assert result["source"] == "pyproject.toml"
    assert len(result["runtime"]) > 0
    assert "requests" in result["runtime"]
    assert "click" in result["runtime"]
    assert "pytest" in result["dev"]


def test_parse_python_dependencies_pep621_format(temp_dir):
    """Test extracting dependencies from PEP 621 format"""
    # Arrange
    content = """
[project]
name = "test"
dependencies = ["requests>=2.28.0", "click>=8.0.0"]

[project.optional-dependencies]
dev = ["pytest>=7.2.0"]
"""
    (temp_dir / "pyproject.toml").write_text(content)

    # Act
    result = parse_python_dependencies(temp_dir)

    # Assert
    assert result["source"] == "pyproject.toml"
    assert "requests" in result["runtime"]
    assert "pytest" in result["dev"]


def test_parse_python_dependencies_requirements_txt(temp_dir, sample_requirements_txt):
    """Test extracting dependencies from requirements.txt"""
    # Act
    result = parse_python_dependencies(temp_dir)

    # Assert
    assert result["source"] == "requirements.txt"
    assert len(result["runtime"]) > 0
    assert "requests" in result["runtime"]


def test_parse_python_dependencies_setup_py(temp_dir, sample_setup_py):
    """Test extracting dependencies from setup.py"""
    # Act
    result = parse_python_dependencies(temp_dir)

    # Assert
    assert result["source"] == "setup.py"
    assert len(result["runtime"]) > 0
    assert "requests" in result["runtime"]
    assert "pytest" in result["dev"]


def test_parse_python_dependencies_no_files(temp_dir):
    """Test extracting dependencies when no dependency files exist"""
    # Act
    result = parse_python_dependencies(temp_dir)

    # Assert
    assert result["source"] == "none"
    assert result["runtime"] == []
    assert result["dev"] == []


def test_parse_python_dependencies_dev_requirements(temp_dir):
    """Test extracting dev dependencies from dev-requirements.txt"""
    # Arrange
    (temp_dir / "requirements.txt").write_text("flask==2.0.0")
    (temp_dir / "requirements-dev.txt").write_text("pytest==7.0.0")

    # Act
    result = parse_python_dependencies(temp_dir)

    # Assert
    assert result["source"] == "requirements.txt"
    assert "flask" in result["runtime"]
    assert "pytest" in result["dev"]


# ========== Test parse_javascript_dependencies ==========

def test_parse_javascript_dependencies_valid_package_json(temp_dir, sample_package_json):
    """Test extracting dependencies from package.json"""
    # Act
    result = parse_javascript_dependencies(temp_dir)

    # Assert
    assert result["source"] == "package.json"
    assert "express" in result["runtime"]
    assert "lodash" in result["runtime"]
    assert "jest" in result["dev"]
    assert "eslint" in result["dev"]
    assert "react" in result["peer"]
    assert "fsevents" in result["optional"]


def test_parse_javascript_dependencies_no_package_json(temp_dir):
    """Test extracting dependencies when package.json doesn't exist"""
    # Act
    result = parse_javascript_dependencies(temp_dir)

    # Assert
    assert result["source"] == "none"
    assert result["runtime"] == []
    assert result["dev"] == []


def test_parse_javascript_dependencies_minimal_package_json(temp_dir):
    """Test extracting dependencies from minimal package.json"""
    # Arrange
    data = {"name": "test", "version": "1.0.0"}
    (temp_dir / "package.json").write_text(json.dumps(data))

    # Act
    result = parse_javascript_dependencies(temp_dir)

    # Assert
    assert result["source"] == "none"  # No dependencies = none
    assert result["runtime"] == []


# ========== Edge Cases and Error Handling ==========

def test_parse_toml_unicode_content(temp_dir):
    """Test parsing TOML with Unicode characters"""
    # Arrange
    if not TOML_AVAILABLE:
        pytest.skip("TOML library not available")

    content = """
[tool.poetry]
name = "测试包"
description = "Тестовый пакет with émojis 🎉"
"""
    path = temp_dir / "unicode.toml"
    path.write_text(content, encoding='utf-8')

    # Act
    result = parse_toml(path)

    # Assert
    assert result is not None
    assert "测试包" in result["tool"]["poetry"]["name"]


def test_parse_json_unicode_content(temp_dir):
    """Test parsing JSON with Unicode characters"""
    # Arrange
    data = {"name": "测试", "description": "Test émojis 🎉"}
    path = temp_dir / "unicode.json"
    path.write_text(json.dumps(data, ensure_ascii=False), encoding='utf-8')

    # Act
    result = parse_json(path)

    # Assert
    assert result is not None
    assert result["name"] == "测试"


def test_parse_requirements_txt_complex_version_specs(temp_dir):
    """Test parsing requirements with complex version specifications"""
    # Arrange
    content = """
package1>=1.0.0,<2.0.0,!=1.5.0
package2~=1.4.2
package3===2.0.0
"""
    path = temp_dir / "complex.txt"
    path.write_text(content)

    # Act
    result = parse_requirements_txt(path)

    # Assert
    assert len(result) == 3
    assert result[0]['name'] == 'package1'


def test_all_parsers_handle_permission_errors(temp_dir):
    """Test that all parsers handle permission errors gracefully"""
    # This test verifies error handling but may be skipped on some systems
    import os
    import stat
    import sys

    # Skip on Windows where permission model is different
    if sys.platform == 'win32':
        pytest.skip("Permission test not applicable on Windows")

    # Arrange
    path = temp_dir / "no_permission.txt"
    path.write_text("content")

    # Remove read permissions (but owner on macOS may still be able to read)
    os.chmod(path, 0o000)

    try:
        # Act & Assert - all should return None/empty without raising
        # Note: On macOS, root/owner may still be able to read despite permissions
        # So we just verify no exceptions are raised
        result_toml = parse_toml(path)
        result_json = parse_json(path)
        result_yaml = parse_yaml(path)
        result_ini = parse_ini(path)
        result_req = parse_requirements_txt(path)
        result_setup = parse_setup_py_safe(path)

        # Verify they either return None/empty OR succeed (macOS owner access)
        assert result_toml is None or isinstance(result_toml, dict)
        assert result_json is None or isinstance(result_json, dict)
        assert result_yaml is None or isinstance(result_yaml, dict)
        assert result_ini is None or isinstance(result_ini, dict)
        assert isinstance(result_req, list)
        assert result_setup is None or isinstance(result_setup, dict)

    finally:
        # Restore permissions for cleanup
        os.chmod(path, stat.S_IREAD | stat.S_IWRITE)


# ========== Module Availability Tests ==========

def test_toml_available_flag():
    """Test TOML_AVAILABLE flag is boolean"""
    assert isinstance(TOML_AVAILABLE, bool)


def test_yaml_available_flag():
    """Test YAML_AVAILABLE flag is boolean"""
    assert isinstance(YAML_AVAILABLE, bool)


# ========== Integration Tests ==========

def test_parse_python_dependencies_priority_order(temp_dir):
    """Test that pyproject.toml takes priority over requirements.txt"""
    # Arrange - Create both files
    (temp_dir / "pyproject.toml").write_text("""
[project]
dependencies = ["click>=8.0.0"]
""")
    (temp_dir / "requirements.txt").write_text("flask==2.0.0")

    # Act
    result = parse_python_dependencies(temp_dir)

    # Assert - pyproject.toml should be preferred
    assert result["source"] == "pyproject.toml"
    assert "click" in result["runtime"]


def test_parse_setup_py_with_complex_expressions(temp_dir):
    """Test parsing setup.py with list comprehensions and complex expressions"""
    # Arrange
    content = """
from setuptools import setup

# Complex expression that AST parser should handle
dependencies = ["base-package"]

setup(
    name="complex-package",
    version="1.0.0",
    install_requires=dependencies + ["extra-package"],
)
"""
    path = temp_dir / "complex_setup.py"
    path.write_text(content)

    # Act
    result = parse_setup_py_safe(path)

    # Assert
    # AST parser can only extract literals, not computed values
    # This tests graceful handling of complex expressions
    assert result is not None
    assert result.get("name") == "complex-package"
