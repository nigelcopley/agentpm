"""
apm migrate-v1-to-v2 - Atomic V1 to V2 migration orchestrator

Migrates ALL V1 file-based systems to V2 database in single atomic operation.

Migration Scope:
- _RULES/ directory → rules table
- STATUS.md → work_item_summaries table
- NEXT-SESSION.md → work_item_summaries table

Phases:
A. Backup (5s): Complete V1 snapshot for rollback
B. Migrate (20-30s): All systems in single transaction
C. Validate (10s): 7-check comprehensive validation
D. Cleanup/Rollback (5s): Finalize or restore V1

Design: docs/artifacts/deliverables/v2-consolidation-architecture.md
"""

import click
import json
import re
import shutil
import sqlite3
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from rich.console import Console
from rich.table import Table

from agentpm.cli.utils.project import ensure_project_root
from agentpm.cli.utils.services import get_database_service
from agentpm.core.database.models import Rule, WorkItem, WorkItemSummary
from agentpm.core.database.enums import (
    EnforcementLevel,
    WorkItemStatus,
    WorkItemType,
)


# ============================================================================
# Data Structures
# ============================================================================


@dataclass
class BackupManifest:
    """Tracks all backup artifacts for rollback."""

    backup_dir: Path
    timestamp: datetime
    artifacts: Dict[str, Path] = field(default_factory=dict)

    def add_artifact(self, name: str, path: Path):
        """Register a backup artifact."""
        self.artifacts[name] = path


@dataclass
class MigrationResult:
    """Results of Phase B migration."""

    success: bool = False
    error: Optional[str] = None
    rules_migrated: int = 0
    status_summaries_created: int = 0
    handover_summary_created: bool = False
    duration_ms: float = 0


@dataclass
class ValidationResult:
    """Results of Phase C validation."""

    passes: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)

    def add_pass(self, msg: str):
        self.passes.append(msg)

    def add_warning(self, msg: str):
        self.warnings.append(msg)

    def add_error(self, msg: str):
        self.errors.append(msg)

    def is_successful(self) -> bool:
        return len(self.errors) == 0


@dataclass
class FinalResult:
    """Results of Phase D cleanup/rollback."""

    success: bool = False
    action_taken: str = ""  # "cleanup" or "rollback"
    message: str = ""


@dataclass
class MigrationReport:
    """Complete migration report."""

    backup: Optional[BackupManifest] = None
    migration: Optional[MigrationResult] = None
    validation: Optional[ValidationResult] = None
    final: Optional[FinalResult] = None


# ============================================================================
# Phase A: Backup
# ============================================================================


def phase_a_backup(project_root: Path) -> BackupManifest:
    """
    Create complete V1 snapshot for rollback.

    Duration: ~5 seconds

    Returns:
        BackupManifest with paths to all backup artifacts
    """
    timestamp = datetime.now()
    backup_dir = project_root / ".aipm" / "v1-backup" / timestamp.strftime("%Y%m%d-%H%M%S")
    backup_dir.mkdir(parents=True, exist_ok=True)

    manifest = BackupManifest(backup_dir=backup_dir, timestamp=timestamp)

    # 1. Backup database (SQLite copy)
    db_path = project_root / ".aipm" / "data" / "aipm.db"
    if db_path.exists():
        db_backup = backup_dir / "aipm.db.backup"
        shutil.copy2(db_path, db_backup)
        manifest.add_artifact("database", db_backup)

    # 2. Backup _RULES/ directory
    rules_dir = project_root / "_RULES"
    if rules_dir.exists():
        rules_backup = backup_dir / "_RULES"
        shutil.copytree(rules_dir, rules_backup)
        manifest.add_artifact("rules_dir", rules_backup)

    # 3. Backup STATUS.md
    status_file = project_root / "STATUS.md"
    if status_file.exists():
        status_backup = backup_dir / "STATUS.md"
        shutil.copy2(status_file, status_backup)
        manifest.add_artifact("status_md", status_backup)

    # 4. Backup NEXT-SESSION.md
    next_session_file = project_root / "NEXT-SESSION.md"
    if next_session_file.exists():
        next_session_backup = backup_dir / "NEXT-SESSION.md"
        shutil.copy2(next_session_file, next_session_backup)
        manifest.add_artifact("next_session_md", next_session_backup)

    # 5. Create manifest.json
    metadata = {
        "backup_timestamp": timestamp.isoformat(),
        "project_root": str(project_root),
        "artifacts": {name: str(path) for name, path in manifest.artifacts.items()},
        "migration_version": "1.0.0",
    }

    manifest_path = backup_dir / "manifest.json"
    manifest_path.write_text(json.dumps(metadata, indent=2))
    manifest.add_artifact("manifest", manifest_path)

    return manifest


# ============================================================================
# Phase B: Migrate
# ============================================================================


def phase_b_migrate(
    db_service, project_id: int, project_root: Path
) -> MigrationResult:
    """
    Execute all migrations in single atomic transaction.

    Duration: ~20-30 seconds

    All migrations succeed OR all rollback (no partial state).

    Returns:
        MigrationResult with counts and status
    """
    start_time = datetime.now()
    result = MigrationResult()

    try:
        with db_service.transaction() as conn:
            # Step 1: Migrate _RULES/
            rules_migrated = migrate_rules_to_db(conn, project_id, project_root)
            result.rules_migrated = rules_migrated

            # Step 2: Create work item for session tracking
            session_wi = create_session_tracking_work_item(conn, project_id)

            # Step 3: Migrate STATUS.md sessions
            status_summaries = migrate_status_md(
                conn, session_wi["id"], project_root
            )
            result.status_summaries_created = status_summaries

            # Step 4: Migrate NEXT-SESSION.md handover
            handover_created = migrate_next_session_md(
                conn, session_wi["id"], project_root
            )
            result.handover_summary_created = handover_created

            # COMMIT: All succeeded
            result.success = True

    except Exception as e:
        # ROLLBACK: Any failure reverts all changes
        result.success = False
        result.error = str(e)

    result.duration_ms = (datetime.now() - start_time).total_seconds() * 1000
    return result


def migrate_rules_to_db(
    conn: sqlite3.Connection, project_id: int, project_root: Path
) -> int:
    """Parse _RULES/*.md and insert into rules table."""
    rules_dir = project_root / "_RULES"
    if not rules_dir.exists():
        return 0

    rules_created = 0

    # Category mapping
    file_to_category = {
        "CORE_PRINCIPLES.md": "core",
        "DEVELOPMENT_PRINCIPLES.md": "development",
        "ARCHITECTURE_PRINCIPLES.md": "architecture",
        "TESTING_RULES.md": "testing",
        "TASK_WORKFLOW_RULES.md": "workflow",
        "WORK_ITEM_WORKFLOW_RULES.md": "workflow",
        "FEATURE_WORKFLOW_RULES.md": "workflow",
        "CODE_QUALITY_STANDARDS.md": "code_quality",
        "DATA_GOVERNANCE.md": "data_governance",
        "OPERATIONAL_STANDARDS.md": "operations",
        "CONTEXT_STRUCTURE.md": "context",
        "AGENT_SELECTION.md": "agent_selection",
    }

    for md_file in rules_dir.glob("*.md"):
        if md_file.name in ["README.md", "QUICK_REFERENCE.md", "RULES_COVERAGE_MATRIX.md"]:
            continue

        category = file_to_category.get(md_file.name, "general")
        rules = parse_rules_from_markdown(md_file, category)

        for rule_data in rules:
            # Insert rule
            conn.execute(
                """
                INSERT INTO rules (
                    project_id, rule_id, name, description, category,
                    enforcement_level, validation_logic, error_message,
                    config, enabled
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    project_id,
                    rule_data["rule_id"],
                    rule_data["name"],
                    rule_data["description"],
                    rule_data["category"],
                    rule_data["enforcement_level"],
                    rule_data.get("validation_logic"),
                    rule_data.get("error_message"),
                    json.dumps(rule_data.get("config", {})),
                    1,  # enabled=True
                ),
            )
            rules_created += 1

    return rules_created


def parse_rules_from_markdown(filepath: Path, category: str) -> List[Dict]:
    """
    Extract structured rules from markdown file.

    Pattern recognition:
    - Rule IDs: DP-001, WF-002, CQ-003, TEST-004, etc.
    - Enforcement: [BLOCK], [LIMIT], [GUIDE], [ENHANCE]
    - Description: Following paragraphs
    """
    with open(filepath, "r") as f:
        content = f.read()

    rules = []

    # Pattern: Rule ID followed by ANYTHING then [ENFORCEMENT]
    # Example: "DP-001: Time-Boxing Implementation Tasks [BLOCK]"
    # Use DOTALL to match across lines
    pattern = r"([A-Z]{2,4}-\d{3})[:\s]+(.+?)\[(BLOCK|LIMIT|GUIDE|ENHANCE)\]"

    for match in re.finditer(pattern, content, re.DOTALL):
        rule_id = match.group(1)
        rest_text = match.group(2).strip()
        enforcement = match.group(3)

        # Extract name (first sentence or up to newline)
        name_match = re.match(r"^(.*?)(?:\.|$)", rest_text)
        name = name_match.group(1).strip() if name_match else rest_text[:50]

        # Convert to kebab-case
        name_kebab = name.lower().replace(" ", "-").replace("_", "-")
        name_kebab = re.sub(r"[^a-z0-9-]", "", name_kebab)
        name_kebab = re.sub(r"-+", "-", name_kebab).strip("-")

        # Extract description (next paragraph after rule declaration)
        desc_start = match.end()
        desc_end = content.find("\n\n", desc_start)
        if desc_end == -1:
            desc_end = desc_start + 200
        description = content[desc_start:desc_end].strip()

        # Limit description length
        if len(description) > 500:
            description = description[:497] + "..."

        rules.append(
            {
                "rule_id": rule_id,
                "name": name_kebab[:100],  # Max 100 chars
                "description": description or name,
                "category": category,
                "enforcement_level": enforcement,
                "validation_logic": None,
                "error_message": None,
                "config": {},
            }
        )

    return rules


def create_session_tracking_work_item(
    conn: sqlite3.Connection, project_id: int
) -> Dict:
    """Create work item for migrated session history."""
    cursor = conn.execute(
        """
        INSERT INTO work_items (
            project_id, name, type, status, description
        )
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            project_id,
            "V1 Session History (Migrated)",
            WorkItemType.PLANNING.value,
            WorkItemStatus.DONE.value,
            "Migrated session history from V1 STATUS.md and NEXT-SESSION.md files",
        ),
    )

    work_item_id = cursor.lastrowid

    # Fetch the created work item
    cursor = conn.execute(
        "SELECT * FROM work_items WHERE id = ?", (work_item_id,)
    )
    row = cursor.fetchone()

    return {
        "id": row[0],
        "project_id": row[1],
        "name": row[2],
        "type": row[3],
        "status": row[4],
    }


def migrate_status_md(
    conn: sqlite3.Connection, work_item_id: int, project_root: Path
) -> int:
    """Parse STATUS.md and create session summaries."""
    status_file = project_root / "STATUS.md"
    if not status_file.exists():
        return 0

    sessions = parse_status_md_sessions(status_file)
    summaries_created = 0

    for session in sessions:
        conn.execute(
            """
            INSERT INTO work_item_summaries (
                work_item_id, session_date, session_duration_hours,
                summary_text, summary_type, created_by, context_metadata
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                work_item_id,
                session["date"],
                session.get("duration_hours"),
                session["content"],
                "session",
                "V1 Migration",
                json.dumps(
                    {
                        "migrated_from": "STATUS.md",
                        "session_title": session.get("title"),
                        "work_items_completed": session.get("completed_wis", []),
                    }
                ),
            ),
        )
        summaries_created += 1

    return summaries_created


def parse_status_md_sessions(filepath: Path) -> List[Dict]:
    """
    Parse STATUS.md into session records.

    Pattern: Sessions marked by date headers or completion markers.
    """
    with open(filepath, "r") as f:
        content = f.read()

    sessions = []

    # Pattern: Various date formats in headers
    # "## 🎉 What's Complete Today (YYYY-MM-DD)"
    # "## Session YYYY-MM-DD"
    # "**Date**: YYYY-MM-DD"
    date_patterns = [
        r"##.*?\((?P<date>\d{4}-\d{2}-\d{2})\)",
        r"##\s+Session\s+(?P<date>\d{4}-\d{2}-\d{2})",
        r"\*\*Date\*\*:\s*(?P<date>\d{4}-\d{2}-\d{2})",
    ]

    for pattern in date_patterns:
        for match in re.finditer(pattern, content):
            session_start = match.end()

            # Find next session or end of file
            next_match = None
            for next_pattern in date_patterns:
                next_search = re.search(next_pattern, content[session_start:])
                if next_search and (not next_match or next_search.start() < next_match.start()):
                    next_match = next_search

            session_end = (
                session_start + next_match.start() if next_match else len(content)
            )

            session_content = content[session_start:session_end].strip()

            # Skip if content too short (likely just a header)
            if len(session_content) < 50:
                continue

            # Extract duration
            duration_match = re.search(
                r"\*\*Duration\*\*:\s*(\d+(?:\.\d+)?)\s*h(?:ours?)?",
                session_content,
                re.IGNORECASE,
            )
            duration = float(duration_match.group(1)) if duration_match else None

            sessions.append(
                {
                    "date": match.group("date"),
                    "duration_hours": duration,
                    "content": session_content[:5000],  # Limit size
                    "title": extract_session_title(session_content),
                    "completed_wis": extract_completed_work_items(session_content),
                }
            )

    return sessions


def extract_session_title(content: str) -> str:
    """Extract session title from content."""
    # Look for "## Title" or "### Title" after date
    title_match = re.search(r"^#{2,3}\s+(.+?)$", content, re.MULTILINE)
    if title_match:
        return title_match.group(1).strip()
    return "Session"


def extract_completed_work_items(content: str) -> List[str]:
    """Extract WI-XXX references from content."""
    wi_pattern = r"WI-(\d{4})"
    matches = re.findall(wi_pattern, content)
    return [f"WI-{m}" for m in matches]


def migrate_next_session_md(
    conn: sqlite3.Connection, work_item_id: int, project_root: Path
) -> bool:
    """Parse NEXT-SESSION.md and create handover summary."""
    next_session_file = project_root / "NEXT-SESSION.md"
    if not next_session_file.exists():
        return False

    with open(next_session_file, "r") as f:
        content = f.read()

    # Extract metadata
    last_updated_match = re.search(
        r"\*\*Last Updated\*\*:\s*(.+?)$", content, re.MULTILINE
    )
    session_id_match = re.search(
        r"\*\*Session ID\*\*:\s*(.+?)$", content, re.MULTILINE
    )

    # Parse date or use current date
    try:
        if last_updated_match:
            date_str = last_updated_match.group(1).strip()
            session_date = datetime.fromisoformat(date_str).date()
        else:
            session_date = datetime.now().date()
    except:
        session_date = datetime.now().date()

    conn.execute(
        """
        INSERT INTO work_item_summaries (
            work_item_id, session_date, summary_text,
            summary_type, created_by, context_metadata
        )
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            work_item_id,
            session_date.isoformat(),
            content[:5000],  # Limit size
            "session",
            "V1 Migration",
            json.dumps(
                {
                    "migrated_from": "NEXT-SESSION.md",
                    "session_id": session_id_match.group(1)
                    if session_id_match
                    else None,
                }
            ),
        ),
    )

    return True


# ============================================================================
# Phase C: Validate
# ============================================================================


def phase_c_validate(
    db_service, project_id: int, migration_result: MigrationResult
) -> ValidationResult:
    """
    Comprehensive validation of V2-only system.

    Duration: ~10 seconds

    All validations must pass for migration to complete.

    Returns:
        ValidationResult with passes/warnings/errors
    """
    validation = ValidationResult()

    # Check 1: Database integrity
    try:
        with db_service.connect() as conn:
            # Verify tables exist
            cursor = conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name IN ('rules', 'work_item_summaries')"
            )
            tables = [row[0] for row in cursor.fetchall()]

            if "rules" in tables and "work_item_summaries" in tables:
                validation.add_pass("✅ Database schema valid (rules + work_item_summaries)")
            else:
                validation.add_error(
                    f"Database schema incomplete: missing {set(['rules', 'work_item_summaries']) - set(tables)}"
                )
    except Exception as e:
        validation.add_error(f"Database integrity check failed: {e}")

    # Check 2: Rules count
    if migration_result.rules_migrated > 0:
        validation.add_pass(
            f"✅ Rules migrated: {migration_result.rules_migrated}"
        )
    else:
        validation.add_warning("No rules were migrated (is _RULES/ empty?)")

    # Check 3: Session summaries
    if migration_result.status_summaries_created > 0:
        validation.add_pass(
            f"✅ Session summaries: {migration_result.status_summaries_created}"
        )
    else:
        validation.add_warning("No STATUS.md sessions migrated")

    if migration_result.handover_summary_created:
        validation.add_pass("✅ NEXT-SESSION.md handover migrated")
    else:
        validation.add_warning("No NEXT-SESSION.md found")

    # Check 4: Query rules table
    try:
        with db_service.connect() as conn:
            cursor = conn.execute(
                "SELECT COUNT(*) FROM rules WHERE project_id = ? AND enabled = 1",
                (project_id,),
            )
            enabled_count = cursor.fetchone()[0]

            if enabled_count > 0:
                validation.add_pass(f"✅ Rules queryable: {enabled_count} enabled")
            else:
                validation.add_error("No enabled rules found in database")
    except Exception as e:
        validation.add_error(f"Rules query failed: {e}")

    # Check 5: Work item summaries queryable
    try:
        with db_service.connect() as conn:
            cursor = conn.execute(
                """
                SELECT COUNT(*) FROM work_item_summaries wis
                JOIN work_items wi ON wis.work_item_id = wi.id
                WHERE wi.project_id = ?
                """,
                (project_id,),
            )
            summary_count = cursor.fetchone()[0]

            if summary_count > 0:
                validation.add_pass(
                    f"✅ Session summaries queryable: {summary_count} records"
                )
            else:
                validation.add_warning("No session summaries found")
    except Exception as e:
        validation.add_error(f"Summaries query failed: {e}")

    # Check 6: V1 files still exist (for rollback)
    project_root = Path.cwd()
    if (project_root / "_RULES").exists():
        validation.add_pass("✅ V1 files preserved for rollback")
    else:
        validation.add_warning("V1 _RULES/ directory not found")

    # Check 7: Migration duration
    if migration_result.duration_ms < 60000:  # <60s
        validation.add_pass(
            f"✅ Migration duration: {migration_result.duration_ms / 1000:.1f}s"
        )
    else:
        validation.add_warning(
            f"Migration took longer than expected: {migration_result.duration_ms / 1000:.1f}s"
        )

    return validation


# ============================================================================
# Phase D: Cleanup or Rollback
# ============================================================================


def phase_d_cleanup_or_rollback(
    validation: ValidationResult, backup: BackupManifest, project_root: Path
) -> FinalResult:
    """
    Finalize migration or restore V1.

    Duration: ~5 seconds

    If validation failed: Rollback to V1
    If validation passed: Archive V1 files, keep database

    Returns:
        FinalResult with action taken
    """
    final = FinalResult()

    if validation.is_successful():
        # SUCCESS: Archive V1 files
        final.action_taken = "cleanup"

        # Move V1 files to archive directory
        archive_dir = project_root / ".aipm" / "v1-archive"
        archive_dir.mkdir(parents=True, exist_ok=True)

        # Archive _RULES/
        rules_dir = project_root / "_RULES"
        if rules_dir.exists():
            archive_rules = archive_dir / "_RULES"
            if archive_rules.exists():
                shutil.rmtree(archive_rules)
            shutil.move(str(rules_dir), str(archive_rules))

        # Archive STATUS.md
        status_file = project_root / "STATUS.md"
        if status_file.exists():
            shutil.move(str(status_file), str(archive_dir / "STATUS.md"))

        # Archive NEXT-SESSION.md
        next_session_file = project_root / "NEXT-SESSION.md"
        if next_session_file.exists():
            shutil.move(
                str(next_session_file), str(archive_dir / "NEXT-SESSION.md")
            )

        final.success = True
        final.message = (
            f"Migration complete! V1 files archived to {archive_dir}"
        )

    else:
        # FAILURE: Rollback to V1
        final.action_taken = "rollback"

        try:
            # Restore database from backup
            db_backup = backup.artifacts.get("database")
            if db_backup:
                db_path = project_root / ".aipm" / "data" / "aipm.db"
                shutil.copy2(db_backup, db_path)

            final.success = True
            final.message = f"Rolled back to V1. Backup preserved at {backup.backup_dir}"

        except Exception as e:
            final.success = False
            final.message = f"Rollback failed: {e}. Manual recovery needed from {backup.backup_dir}"

    return final


# ============================================================================
# Orchestrator
# ============================================================================


def orchestrate_migration(project_root: Path) -> MigrationReport:
    """
    Execute complete V1 → V2 migration in single atomic operation.

    Duration: <60 seconds total

    Single atomic operation: all succeed OR all rollback.

    Returns:
        MigrationReport with results from all phases
    """
    report = MigrationReport()
    console = Console()

    try:
        # Initialize database
        db = get_database_service(project_root)

        # Get project ID
        with db.connect() as conn:
            cursor = conn.execute(
                "SELECT id FROM projects WHERE path = ?",
                (str(project_root),)
            )
            row = cursor.fetchone()
            if not row:
                raise ValueError(f"Project not found at {project_root}")
            project_id = row[0]

        # Phase A: Backup (5 seconds)
        console.print("\n[bold cyan]Phase A: Creating V1 backup...[/bold cyan]")
        backup = phase_a_backup(project_root)
        report.backup = backup
        console.print(f"✅ Backup complete: {backup.backup_dir}\n")

        # Phase B: Migrate (20-30 seconds)
        console.print("[bold cyan]Phase B: Migrating to V2...[/bold cyan]")
        migration_result = phase_b_migrate(db, project_id, project_root)
        report.migration = migration_result

        if not migration_result.success:
            console.print(
                f"[bold red]❌ Migration failed:[/bold red] {migration_result.error}\n"
            )
            raise ValueError(f"Migration failed: {migration_result.error}")

        console.print("✅ Migration complete:")
        console.print(f"   - {migration_result.rules_migrated} rules migrated")
        console.print(
            f"   - {migration_result.status_summaries_created} session summaries created"
        )
        console.print(
            f"   - {1 if migration_result.handover_summary_created else 0} handover summary created\n"
        )

        # Phase C: Validate (10 seconds)
        console.print("[bold cyan]Phase C: Validating V2 system...[/bold cyan]")
        validation = phase_c_validate(db, project_id, migration_result)
        report.validation = validation

        if not validation.is_successful():
            console.print(
                f"[bold red]❌ Validation failed ({len(validation.errors)} errors)[/bold red]"
            )
            for error in validation.errors:
                console.print(f"   - {error}")
            console.print()
        else:
            console.print(
                f"[bold green]✅ Validation passed ({len(validation.passes)} checks)[/bold green]"
            )
            for check in validation.passes:
                console.print(f"   {check}")
            if validation.warnings:
                console.print("\n[bold yellow]Warnings:[/bold yellow]")
                for warning in validation.warnings:
                    console.print(f"   ⚠️  {warning}")
            console.print()

        # Phase D: Cleanup or Rollback (5 seconds)
        console.print("[bold cyan]Phase D: Finalizing...[/bold cyan]")
        final = phase_d_cleanup_or_rollback(validation, backup, project_root)
        report.final = final

        if final.success:
            if final.action_taken == "cleanup":
                console.print("[bold green]✅ V2 migration complete![/bold green]")
                console.print("\n[cyan]V1 files archived at:[/cyan]")
                console.print(f"   {project_root / '.aipm' / 'v1-archive'}")
                console.print("\n[cyan]Backup preserved at:[/cyan]")
                console.print(f"   {backup.backup_dir}")
            else:
                console.print(
                    "[bold yellow]⚠️  Migration rolled back[/bold yellow]"
                )
                console.print(f"\n{final.message}")
        else:
            console.print(f"[bold red]❌ {final.message}[/bold red]")

        console.print()

    except Exception as e:
        console.print(f"\n[bold red]❌ Migration failed:[/bold red] {e}\n")

        # Attempt emergency rollback
        if report.backup:
            console.print("[yellow]Attempting emergency rollback...[/yellow]")
            validation = ValidationResult()
            validation.add_error(str(e))
            final = phase_d_cleanup_or_rollback(validation, report.backup, project_root)
            report.final = final

            if final.success:
                console.print(f"[green]✅ {final.message}[/green]\n")
            else:
                console.print(f"[red]❌ {final.message}[/red]\n")

        raise

    return report


# ============================================================================
# CLI Command
# ============================================================================


@click.command(name="migrate-v1-to-v2")
@click.option(
    "--dry-run",
    is_flag=True,
    help="Show what would be migrated without making changes",
)
@click.option(
    "--force",
    is_flag=True,
    help="Skip confirmation prompt",
)
@click.pass_context
def migrate_v1_to_v2(ctx: click.Context, dry_run: bool, force: bool):
    """
    Migrate V1 file-based systems to V2 database.

    Atomic migration in 4 phases:
    A. Backup (5s): Create complete V1 snapshot
    B. Migrate (20-30s): Move all systems to database
    C. Validate (10s): Verify V2 functionality
    D. Cleanup/Rollback (5s): Finalize or restore

    Migrates:
    - _RULES/*.md → rules table
    - STATUS.md → work_item_summaries table
    - NEXT-SESSION.md → work_item_summaries table

    \b
    Examples:
      apm migrate-v1-to-v2              # Interactive migration
      apm migrate-v1-to-v2 --force      # Skip confirmation
      apm migrate-v1-to-v2 --dry-run    # Preview only
    """
    console = ctx.obj["console"]
    console_err = ctx.obj["console_err"]
    project_root = ensure_project_root(ctx)

    # Dry run mode
    if dry_run:
        console.print(
            "\n[bold yellow]🔍 DRY RUN: Analyzing V1 files...[/bold yellow]\n"
        )

        # Check what exists
        rules_dir = project_root / "_RULES"
        status_file = project_root / "STATUS.md"
        next_session_file = project_root / "NEXT-SESSION.md"

        table = Table(title="V1 Files to Migrate")
        table.add_column("Item", style="cyan")
        table.add_column("Status", style="green")
        table.add_column("Details")

        if rules_dir.exists():
            rule_files = list(rules_dir.glob("*.md"))
            table.add_row(
                "_RULES/",
                "✅ Found",
                f"{len(rule_files)} markdown files",
            )
        else:
            table.add_row("_RULES/", "❌ Not found", "No migration needed")

        if status_file.exists():
            size_kb = status_file.stat().st_size / 1024
            table.add_row("STATUS.md", "✅ Found", f"{size_kb:.1f} KB")
        else:
            table.add_row("STATUS.md", "❌ Not found", "No migration needed")

        if next_session_file.exists():
            size_kb = next_session_file.stat().st_size / 1024
            table.add_row(
                "NEXT-SESSION.md", "✅ Found", f"{size_kb:.1f} KB"
            )
        else:
            table.add_row(
                "NEXT-SESSION.md", "❌ Not found", "No migration needed"
            )

        console.print(table)
        console.print(
            "\n[cyan]Run without --dry-run to execute migration[/cyan]\n"
        )
        return

    # Confirmation prompt
    if not force:
        console.print("\n[bold yellow]⚠️  V1 → V2 Migration[/bold yellow]")
        console.print("\nThis will:")
        console.print("  1. Backup all V1 files")
        console.print("  2. Migrate _RULES/, STATUS.md, NEXT-SESSION.md to database")
        console.print("  3. Validate V2 system")
        console.print("  4. Archive V1 files (or rollback on failure)")
        console.print("\n[cyan]Duration: <60 seconds[/cyan]")
        console.print("[cyan]Rollback: Automatic on any failure[/cyan]\n")

        if not click.confirm("Proceed with migration?"):
            console.print("\n[yellow]Migration cancelled[/yellow]\n")
            return

    # Execute migration
    try:
        report = orchestrate_migration(project_root)

        # Show final summary
        if report.final and report.final.success:
            console.print(
                "\n[bold green]🎉 Migration successful![/bold green]\n"
            )
        else:
            console_err.print(
                "\n[bold red]❌ Migration failed[/bold red]\n"
            )
            raise click.Abort()

    except Exception as e:
        console_err.print(f"\n[bold red]Migration error:[/bold red] {e}\n")
        raise click.Abort()
