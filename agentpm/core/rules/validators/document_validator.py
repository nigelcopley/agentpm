"""
Validator for DOC-020: Database-First Document Creation

This validator enforces that all documents in docs/ must have
corresponding database records in the document_references table.

Additionally validates document visibility rules:
- visibility must be 'private', 'public', or 'internal'
- File path consistency: private documents in .agentpm/docs/, public/internal in docs/
- Internal document types (testing, analysis) must be 'private'
- Published documents must match file location
"""

from pathlib import Path
from typing import List, Tuple, Optional, Dict, Any
import sqlite3
import re


class DocumentValidator:
    """Validates all documents created via database."""

    def __init__(self, project_root: Path, db_path: Path):
        """
        Initialize validator with project paths.

        Args:
            project_root: Absolute path to project root
            db_path: Absolute path to database file
        """
        self.project_root = project_root
        self.db_path = db_path

    def validate_all_documents(self) -> Tuple[bool, List[str]]:
        """
        Check that all .md files in docs/ have database records.

        Returns:
            Tuple of (is_valid, violations)
            - is_valid: True if all documents have database records
            - violations: List of violation messages
        """
        violations = []

        # Find all .md files in docs/
        docs_dir = self.project_root / "docs"
        if not docs_dir.exists():
            return True, []

        md_files = list(docs_dir.rglob("*.md"))

        if not md_files:
            return True, []

        # Check each file has database record
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            for md_file in md_files:
                # Get relative path
                rel_path = md_file.relative_to(self.project_root)

                # Check if in database
                cursor.execute(
                    "SELECT id FROM document_references WHERE file_path = ?",
                    (str(rel_path),)
                )
                result = cursor.fetchone()

                if not result:
                    violations.append(
                        f"File '{rel_path}' created without database record. "
                        f"Violation of DOC-020. "
                        f"Recreate using: apm document add --file-path='{rel_path}' ..."
                    )

            conn.close()
        except Exception as e:
            violations.append(
                f"Error checking database records: {e}"
            )

        return len(violations) == 0, violations

    def scan_for_direct_creation(self, code_content: str) -> List[str]:
        """
        Scan code for direct file creation patterns.

        Detects:
        - Write(file_path="docs/...")
        - Bash(command="echo ... > docs/...")
        - Bash(command="cat > docs/...")

        Args:
            code_content: String content to scan (agent code, prompts, etc.)

        Returns:
            List of violation messages
        """
        violations = []

        # Check for Write tool with docs/ path
        if 'Write(' in code_content and 'file_path' in code_content:
            # Match Write(file_path="docs/...") or Write(file_path='docs/...')
            write_pattern = r'Write\s*\([^)]*file_path\s*=\s*["\']([^"\']+)["\']'
            matches = re.finditer(write_pattern, code_content, re.DOTALL)
            for match in matches:
                file_path = match.group(1)
                if file_path.startswith('docs/') or 'docs/' in file_path:
                    violations.append(
                        f"Detected Write tool usage for docs/ file: '{file_path}'. "
                        f"Violation of DOC-020. Use 'apm document add' instead."
                    )

        # Check for Bash with file redirection to docs/
        if 'Bash(' in code_content:
            # Match echo ... > docs/... or cat ... > docs/...
            bash_redirect_patterns = [
                r'echo\s+[^>]+>\s*docs/',
                r'cat\s+[^>]*>\s*docs/',
                r'echo\s+[^>]+>docs/',
                r'cat\s+[^>]*>docs/'
            ]

            for pattern in bash_redirect_patterns:
                if re.search(pattern, code_content):
                    violations.append(
                        "Detected Bash file creation for docs/ file. "
                        "Violation of DOC-020. Use 'apm document add' instead."
                    )
                    break  # Only report once per content

        return violations

    def scan_file_for_violations(self, file_path: Path) -> List[str]:
        """
        Scan a file for DOC-020 violations.

        Args:
            file_path: Path to file to scan

        Returns:
            List of violation messages
        """
        try:
            content = file_path.read_text()
            return self.scan_for_direct_creation(content)
        except Exception as e:
            return [f"Error scanning {file_path}: {e}"]

    def scan_project_for_violations(
        self,
        paths: Optional[List[Path]] = None
    ) -> Tuple[bool, List[str]]:
        """
        Scan project files for DOC-020 violations.

        Args:
            paths: Optional list of specific paths to scan.
                   If None, scans .claude/agents/ directory.

        Returns:
            Tuple of (is_valid, violations)
        """
        violations = []

        if paths is None:
            # Default: scan agent definitions
            agents_dir = self.project_root / ".claude" / "agents"
            if not agents_dir.exists():
                return True, []

            paths = list(agents_dir.rglob("*.md"))

        for path in paths:
            if path.is_file():
                file_violations = self.scan_file_for_violations(path)
                violations.extend(file_violations)

        return len(violations) == 0, violations

    def generate_remediation_command(
        self,
        file_path: str,
        entity_type: str = "work-item",
        entity_id: Optional[int] = None,
        category: str = "planning",
        doc_type: str = "requirements",
        title: Optional[str] = None
    ) -> str:
        """
        Generate remediation command for a violation.

        Args:
            file_path: Path to the file (relative to project root)
            entity_type: Type of entity (work-item, task, project)
            entity_id: ID of entity (if known)
            category: Document category
            doc_type: Document type
            title: Document title (if known)

        Returns:
            Full apm document add command string
        """
        if entity_id is None:
            entity_id_str = "<ID>"
        else:
            entity_id_str = str(entity_id)

        if title is None:
            # Generate title from file path
            file_name = Path(file_path).stem
            title = file_name.replace("-", " ").replace("_", " ").title()

        command = f'''apm document add \\
  --entity-type={entity_type} \\
  --entity-id={entity_id_str} \\
  --file-path="{file_path}" \\
  --category={category} \\
  --type={doc_type} \\
  --title="{title}" \\
  --description="<Add description>" \\
  --content="$(cat <<'EOF'
<Add content here>
EOF
)"'''

        return command

    def validate_document_visibility(
        self,
        visibility: str,
        file_path: str,
        document_type: str,
        lifecycle_stage: Optional[str] = None,
        published_path: Optional[str] = None
    ) -> Tuple[bool, List[str]]:
        """
        Validate document visibility rules.

        Rules:
        1. visibility must be 'private', 'public', or 'internal'
        2. File path consistency:
           - private → .agentpm/docs/
           - public/internal → docs/
        3. Internal types (testing, analysis, investigation) must be 'private'
        4. Published documents must match file location

        Args:
            visibility: Document visibility level
            file_path: Document file path (relative to project root)
            document_type: Document type (e.g., 'user_guide', 'test_plan')
            lifecycle_stage: Optional lifecycle stage (draft, approved, published)
            published_path: Optional published path (for published documents)

        Returns:
            Tuple of (is_valid, violations)
            - is_valid: True if all rules pass
            - violations: List of violation messages
        """
        violations = []

        # Rule 1: Valid visibility values
        valid_visibility = ['private', 'public', 'internal']
        if visibility not in valid_visibility:
            violations.append(
                f"Invalid visibility '{visibility}'. Must be one of: {', '.join(valid_visibility)}"
            )
            return False, violations  # Early return for critical error

        # Rule 2: File path consistency
        is_private_path = file_path.startswith('.agentpm/docs/')
        is_public_path = file_path.startswith('docs/')

        if visibility == 'private' and not is_private_path:
            violations.append(
                f"Private document must be in .agentpm/docs/, not '{file_path}'. "
                f"Move to .agentpm/docs/ or change visibility to 'public'/'internal'."
            )

        if visibility in ['public', 'internal'] and is_private_path:
            violations.append(
                f"{visibility.capitalize()} document cannot be in .agentpm/docs/ ('{file_path}'). "
                f"Move to docs/ or change visibility to 'private'."
            )

        # Rule 3: Internal types must be private
        internal_types = [
            'test_plan', 'test_report', 'coverage_report', 'validation_report',
            'analysis_report', 'investigation_report', 'assessment_report',
            'session_summary', 'internal_note'
        ]

        if document_type in internal_types and visibility != 'private':
            violations.append(
                f"Document type '{document_type}' is internal and must be 'private', "
                f"not '{visibility}'. Change visibility to 'private'."
            )

        # Rule 4: Publishing state consistency
        if lifecycle_stage == 'published':
            if visibility == 'private':
                violations.append(
                    f"Published document cannot be 'private'. "
                    f"Change lifecycle_stage to 'approved' or visibility to 'public'/'internal'."
                )

            if published_path and not published_path.startswith('docs/'):
                violations.append(
                    f"Published document must have published_path in docs/, "
                    f"not '{published_path}'."
                )

        return len(violations) == 0, violations

    def validate_visibility_for_document_id(
        self,
        document_id: int
    ) -> Tuple[bool, List[str]]:
        """
        Validate visibility for a specific document by ID.

        Queries database for document details and runs validation.

        Args:
            document_id: Document ID in database

        Returns:
            Tuple of (is_valid, violations)
        """
        violations = []

        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Get document details
            cursor.execute(
                """
                SELECT visibility, file_path, document_type, lifecycle_stage, published_path
                FROM document_references
                WHERE id = ?
                """,
                (document_id,)
            )
            result = cursor.fetchone()

            conn.close()

            if not result:
                violations.append(f"Document ID {document_id} not found in database")
                return False, violations

            visibility, file_path, document_type, lifecycle_stage, published_path = result

            # Run validation
            return self.validate_document_visibility(
                visibility=visibility,
                file_path=file_path,
                document_type=document_type or 'other',
                lifecycle_stage=lifecycle_stage,
                published_path=published_path
            )

        except Exception as e:
            violations.append(f"Error validating document {document_id}: {e}")
            return False, violations

    def validate_all_document_visibility(self) -> Tuple[bool, List[str]]:
        """
        Validate visibility rules for all documents in database.

        Returns:
            Tuple of (is_valid, violations)
            - is_valid: True if all documents pass validation
            - violations: List of violation messages with document IDs
        """
        violations = []

        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Get all documents
            cursor.execute(
                """
                SELECT id, visibility, file_path, document_type, lifecycle_stage, published_path, title
                FROM document_references
                ORDER BY id
                """
            )
            documents = cursor.fetchall()

            conn.close()

            for doc in documents:
                doc_id, visibility, file_path, document_type, lifecycle_stage, published_path, title = doc

                # Run validation for this document
                is_valid, doc_violations = self.validate_document_visibility(
                    visibility=visibility,
                    file_path=file_path,
                    document_type=document_type or 'other',
                    lifecycle_stage=lifecycle_stage,
                    published_path=published_path
                )

                if not is_valid:
                    # Prefix each violation with document ID and title
                    for violation in doc_violations:
                        violations.append(
                            f"Document #{doc_id} ({title or file_path}): {violation}"
                        )

        except Exception as e:
            violations.append(f"Error validating documents: {e}")

        return len(violations) == 0, violations

    def validate_and_report(self) -> bool:
        """
        Run all validations and print report.

        Returns:
            True if all validations pass, False otherwise
        """
        print("=" * 80)
        print("DOC-020 Validation Report: Database-First Document Creation")
        print("=" * 80)

        # Check 1: All docs/ files have database records
        print("\n[1] Checking all docs/ files have database records...")
        is_valid_docs, doc_violations = self.validate_all_documents()

        if is_valid_docs:
            print("✅ PASS: All documents have database records")
        else:
            print(f"❌ FAIL: Found {len(doc_violations)} orphaned documents")
            for violation in doc_violations:
                print(f"    - {violation}")

        # Check 2: Scan agent files for violations
        print("\n[2] Scanning agent definitions for direct file creation...")
        is_valid_agents, agent_violations = self.scan_project_for_violations()

        if is_valid_agents:
            print("✅ PASS: No direct file creation detected in agents")
        else:
            print(f"❌ FAIL: Found {len(agent_violations)} violations in agents")
            for violation in agent_violations:
                print(f"    - {violation}")

        # Check 3: Validate document visibility rules
        print("\n[3] Validating document visibility rules...")
        is_valid_visibility, visibility_violations = self.validate_all_document_visibility()

        if is_valid_visibility:
            print("✅ PASS: All documents have valid visibility settings")
        else:
            print(f"❌ FAIL: Found {len(visibility_violations)} visibility violations")
            for violation in visibility_violations:
                print(f"    - {violation}")

        # Overall result
        print("\n" + "=" * 80)
        overall_valid = is_valid_docs and is_valid_agents and is_valid_visibility
        if overall_valid:
            print("✅ VALIDATION PASSED: DOC-020 compliance verified")
        else:
            print("❌ VALIDATION FAILED: DOC-020 violations detected")
            print("\nRemediation:")
            print("1. Delete orphaned files: rm <file>")
            print("2. Recreate using: apm document add ...")
            print("3. Update agent definitions to use apm document add")
            print("4. Fix visibility violations: apm document update <id> --visibility=<value>")
        print("=" * 80)

        return overall_valid
