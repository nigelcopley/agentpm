"""
V1 File Detection and Migration Guidance

Detects legacy V1 files and guides users to run migration.

**Work Item**: WI-40 (V2 Consolidation)
**Task**: #220 (Refactoring)
"""

from pathlib import Path
from typing import List, Tuple
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown


class V1Detector:
    """Detect and warn about V1 legacy files"""

    @staticmethod
    def check_v1_files(project_root: Path) -> Tuple[bool, List[str]]:
        """
        Check if V1 files exist in project root.

        Args:
            project_root: Path to project root directory

        Returns:
            (has_v1_files: bool, files_found: List[str])
        """
        v1_files = []

        # Check for _RULES/ directory
        rules_dir = project_root / "_RULES"
        if rules_dir.exists() and rules_dir.is_dir():
            count = len(list(rules_dir.glob("*.md")))
            if count > 0:
                v1_files.append(f"_RULES/ ({count} rules)")

        # Check for STATUS.md
        status_file = project_root / "STATUS.md"
        if status_file.exists():
            size_kb = status_file.stat().st_size / 1024
            v1_files.append(f"STATUS.md ({size_kb:.1f} KB)")

        # Check for NEXT-SESSION.md
        next_session_file = project_root / "NEXT-SESSION.md"
        if next_session_file.exists():
            size_kb = next_session_file.stat().st_size / 1024
            v1_files.append(f"NEXT-SESSION.md ({size_kb:.1f} KB)")

        return len(v1_files) > 0, v1_files

    @staticmethod
    def show_migration_warning(console: Console, files_found: List[str]) -> None:
        """
        Display rich migration guidance.

        Args:
            console: Rich console instance
            files_found: List of V1 files detected
        """
        warning_text = f"""
# ⚠️  V1 Legacy Files Detected

Your project contains V1 file-based configuration:

{chr(10).join(f"- {f}" for f in files_found)}

## Migrate to V2

V2 stores all configuration in SQLite database for:
- **Faster queries** (indexed database vs. file parsing)
- **Better validation** (structured data with constraints)
- **Atomic operations** (transactions prevent partial state)
- **Session history** (queryable summaries replace STATUS.md)

## Migration Command

```bash
apm migrate-v1-to-v2
```

**Duration**: <60 seconds
**Safety**: Automatic backup + rollback on failure

## Benefits After Migration

- ✅ Rules queryable in <10ms (was 200-500ms)
- ✅ Session history with SQL filters
- ✅ No more file-based parsing overhead
- ✅ Atomic rule updates (no partial writes)

## Learn More

Run `apm migrate-v1-to-v2 --dry-run` to preview migration without changes.
"""
        console.print(
            Panel(
                Markdown(warning_text),
                title="V1 → V2 Migration Available",
                border_style="yellow",
            )
        )

    @staticmethod
    def show_compact_warning(console: Console, files_found: List[str]) -> None:
        """
        Display compact migration warning (for status command).

        Args:
            console: Rich console instance
            files_found: List of V1 files detected
        """
        console.print("\n[yellow]⚠️  V1 files detected:[/yellow]", end=" ")
        console.print(", ".join(files_found))
        console.print(
            "[cyan]   Run:[/cyan] apm migrate-v1-to-v2 [dim](migrate to V2 database)[/dim]"
        )
