"""
Template utilities for CLI commands.

Provides helpers to discover packaged JSON templates, copy them into the
project-specific `.aipm/templates` directory, and load them as dictionaries.
"""

from __future__ import annotations

import json
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional
import importlib.resources as resources


TEMPLATE_PACKAGE = "agentpm.templates.json"


@dataclass(frozen=True)
class TemplateInfo:
    """Metadata about an available template."""

    template_id: str
    package_path: Path
    project_path: Optional[Path] = None

    @property
    def source_path(self) -> Path:
        """Return the path to load content from (project override preferred)."""
        return self.project_path or self.package_path


def _package_root() -> Path:
    """Path to the packaged templates/json directory."""
    return Path(resources.files(TEMPLATE_PACKAGE))


def _normalize_template_id(template_id: str) -> str:
    """Normalise template id to a path relative to templates/json without suffix."""
    tid = template_id.strip().strip("/")
    if not tid:
        raise ValueError("template_id cannot be empty")
    if tid.endswith(".json"):
        tid = tid[:-5]
    return tid


def _project_template_root(project_root: Path) -> Path:
    """Return project-level template root (.aipm/templates/json)."""
    return project_root / ".aipm" / "templates" / "json"


def list_templates(project_root: Optional[Path] = None) -> List[TemplateInfo]:
    """
    List all available templates with optional project overrides.

    Args:
        project_root: Optional project root to look for overrides.

    Returns:
        List of TemplateInfo entries sorted by template_id.
    """
    package_root = _package_root()
    project_root_path = _project_template_root(project_root) if project_root else None

    template_infos: List[TemplateInfo] = []
    for path in sorted(package_root.rglob("*.json")):
        relative = path.relative_to(package_root)
        template_id = str(relative.with_suffix(""))
        project_path = None
        if project_root_path:
            candidate = project_root_path / relative
            if candidate.exists():
                project_path = candidate
        template_infos.append(
            TemplateInfo(
                template_id=template_id.replace("\\", "/"),
                package_path=path,
                project_path=project_path,
            )
        )
    return template_infos


def get_template_info(
    template_id: str, project_root: Optional[Path] = None
) -> TemplateInfo:
    """Return TemplateInfo for a single template id."""
    tid = _normalize_template_id(template_id)
    package_root = _package_root()
    package_path = package_root / f"{tid}.json"
    if not package_path.exists():
        raise FileNotFoundError(f"Template '{tid}' not found in package")

    project_path = None
    if project_root:
        candidate = _project_template_root(project_root) / f"{tid}.json"
        if candidate.exists():
            project_path = candidate

    return TemplateInfo(
        template_id=tid,
        package_path=package_path,
        project_path=project_path,
    )


def ensure_project_copy(template_id: str, project_root: Path) -> Path:
    """
    Copy template into project template directory if not already present.

    Returns path to the project-local copy.
    """
    tid = _normalize_template_id(template_id)
    info = get_template_info(tid, project_root=project_root)
    if info.project_path and info.project_path.exists():
        return info.project_path

    destination = _project_template_root(project_root) / f"{tid}.json"
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(info.package_path, destination)
    return destination


def load_template(
    template_id: str,
    project_root: Optional[Path] = None,
    prefer_project: bool = True,
) -> Any:
    """
    Load a template as JSON (dict/list).

    Args:
        template_id: Template identifier relative to templates/json (with or without .json)
        project_root: Optional project root for overrides
        prefer_project: If True, use project override when available

    Returns:
        Loaded JSON content.
    """
    info = get_template_info(template_id, project_root=project_root)
    path = info.project_path if prefer_project and info.project_path else info.package_path
    with path.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def save_template_content(path: Path, content: Any) -> None:
    """Write JSON content to destination path with formatting."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as fh:
        json.dump(content, fh, indent=2)
        fh.write("\n")
