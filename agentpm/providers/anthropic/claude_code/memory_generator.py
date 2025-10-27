"""
Claude Code Memory Generator

Generates structured memory files in .claude/memory/ from APM database entities.
Implements 4-tier memory hierarchy with @import resolution and security validation.

Architecture:
- MemoryGenerator: Main generator class for memory files
- SecureImportResolver: @import resolution with security controls
- Memory templates: Jinja2 templates for structured memory content

Pattern: Template Method Pattern with security-first design
"""

from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
import hashlib
import json
import re

from agentpm.core.database.service import DatabaseService
from agentpm.core.database.models.project import Project
from agentpm.providers.base import (
    TemplateBasedMixin,
    FileOutput
)


class SecurityError(Exception):
    """Raised when security validation fails."""
    pass


class SecureImportResolver:
    """
    Secure @import resolution with multiple security layers.

    Security Controls:
    - Recursion depth limiting (5 levels max)
    - Path validation (project boundaries)
    - Circular import detection
    - Symbolic link prevention
    - Sensitive file blacklist
    - File size limits (1 MB max)
    - Content validation (UTF-8, size)
    - Import caching (performance + security)

    Example:
        >>> resolver = SecureImportResolver(project_root=Path("/project"))
        >>> resolved = resolver.resolve("@/docs/file.md", base_path=Path("/project/.claude"))
    """

    # Maximum import depth (prevent infinite recursion)
    MAX_IMPORT_DEPTH = 5

    # Maximum file size per import (prevent DoS)
    MAX_FILE_SIZE = 1_000_000  # 1 MB

    # Sensitive file patterns (blacklist)
    SENSITIVE_PATTERNS = [
        '.env', 'credentials.json', '.aws/', '.ssh/',
        'id_rsa', 'private.key', 'secret', '.pem',
        'config.json', 'settings.json', 'secrets.',
        'password', 'token', 'api_key'
    ]

    def __init__(self, project_root: Path):
        """
        Initialize import resolver.

        Args:
            project_root: Project root directory (security boundary)
        """
        self.project_root = project_root.resolve()
        self._import_stack: List[Path] = []
        self._resolved_cache: Dict[str, str] = {}

    def resolve(self, content: str, base_path: Path) -> str:
        """
        Resolve all @import directives in content with security validation.

        Security Layers:
        1. Recursion depth limiting
        2. Path validation (boundaries)
        3. Symbolic link prevention
        4. Sensitive file blacklist
        5. File size limits
        6. Circular import detection
        7. Content validation

        Args:
            content: Content with @import directives
            base_path: Base directory for relative imports

        Returns:
            Content with imports resolved

        Example:
            >>> content = "# Doc\\n@/docs/api.md\\n## More"
            >>> resolved = resolver.resolve(content, Path("/project"))
        """
        lines = content.split('\n')
        resolved_lines = []

        for line in lines:
            stripped = line.strip()
            if stripped.startswith('@') and not stripped.startswith('@['):
                # @import directive
                import_path = stripped[1:].strip()  # Remove @

                try:
                    # Resolve import with security checks
                    imported_content = self._import_file(import_path, base_path)
                    resolved_lines.append(imported_content)
                except SecurityError as e:
                    # Log security violation
                    print(f"⚠️ Import security violation: {e}")
                    resolved_lines.append(f"<!-- SECURITY: Import blocked - {e} -->")
                except Exception as e:
                    # Log error but continue
                    print(f"⚠️ Import failed: {e}")
                    resolved_lines.append(f"<!-- ERROR: Import failed - {import_path} -->")
            else:
                resolved_lines.append(line)

        return '\n'.join(resolved_lines)

    def _import_file(self, import_path: str, base_path: Path) -> str:
        """
        Import a single file with comprehensive security checks.

        Security Validation Order:
        1. Check recursion depth
        2. Resolve path safely
        3. Validate within project boundaries
        4. Check for circular imports
        5. Validate not symbolic link
        6. Check against sensitive file blacklist
        7. Validate file size
        8. Read and recursively resolve

        Args:
            import_path: Import path from @directive
            base_path: Base directory for relative imports

        Returns:
            Resolved file content

        Raises:
            SecurityError: If security validation fails
        """

        # Layer 1: Check recursion depth
        if len(self._import_stack) >= self.MAX_IMPORT_DEPTH:
            raise SecurityError(
                f"Max import depth ({self.MAX_IMPORT_DEPTH}) exceeded. "
                f"Import stack: {[str(p) for p in self._import_stack]}"
            )

        # Layer 2: Resolve path safely
        try:
            resolved = self._resolve_path(import_path, base_path)
        except Exception as e:
            raise SecurityError(f"Path resolution failed: {e}")

        # Layer 3: Validate within project boundaries
        if not self._is_within_project(resolved):
            raise SecurityError(
                f"Import outside project boundaries: {import_path} "
                f"resolved to {resolved}"
            )

        # Layer 4: Check for circular imports
        if resolved in self._import_stack:
            raise SecurityError(
                f"Circular import detected: {import_path}. "
                f"Import chain: {[str(p) for p in self._import_stack]} → {resolved}"
            )

        # Layer 5: Validate not symbolic link
        if resolved.is_symlink():
            raise SecurityError(
                f"Symbolic links not allowed: {import_path} "
                f"(points to {resolved.readlink()})"
            )

        # Layer 6: Check sensitive file blacklist
        if self._is_sensitive_file(resolved):
            raise SecurityError(
                f"Cannot import sensitive file: {import_path} "
                f"(matches blacklist pattern)"
            )

        # Layer 7: Validate file size
        try:
            if not resolved.exists():
                raise SecurityError(f"File not found: {import_path}")

            file_size = resolved.stat().st_size
            if file_size > self.MAX_FILE_SIZE:
                raise SecurityError(
                    f"Import file too large: {import_path} "
                    f"({file_size / 1_000_000:.2f} MB > {self.MAX_FILE_SIZE / 1_000_000} MB)"
                )
        except OSError as e:
            raise SecurityError(f"Cannot access file: {import_path} - {e}")

        # Layer 8: Read and recursively resolve
        self._import_stack.append(resolved)
        try:
            # Check cache first
            cache_key = str(resolved)
            if cache_key in self._resolved_cache:
                return self._resolved_cache[cache_key]

            # Read file content
            try:
                content = resolved.read_text(encoding='utf-8')
            except UnicodeDecodeError:
                raise SecurityError(f"File not valid UTF-8: {import_path}")

            # Validate content size
            if len(content) > self.MAX_FILE_SIZE:
                raise SecurityError(f"Content too large: {import_path}")

            # Recursively resolve nested imports
            resolved_content = self.resolve(content, resolved.parent)

            # Cache result
            self._resolved_cache[cache_key] = resolved_content

            return resolved_content

        finally:
            self._import_stack.pop()

    def _resolve_path(self, import_path: str, base_path: Path) -> Path:
        """
        Resolve import path to absolute path.

        Supported formats:
        - @/docs/file.md    (absolute from project root)
        - @docs/file.md     (relative to current file)
        - @~/docs/file.md   (user home directory, if within project)

        Args:
            import_path: Import path from @directive
            base_path: Base directory for relative imports

        Returns:
            Resolved absolute path
        """
        # Remove leading @ if present
        if import_path.startswith('@'):
            import_path = import_path[1:]

        # Resolve based on path format
        if import_path.startswith('/'):
            # Absolute from project root
            resolved = (self.project_root / import_path[1:]).resolve()
        elif import_path.startswith('~/'):
            # User home directory
            resolved = Path(import_path).expanduser().resolve()
        else:
            # Relative to current file
            resolved = (base_path / import_path).resolve()

        return resolved

    def _is_within_project(self, path: Path) -> bool:
        """Check if path is within project boundaries."""
        try:
            path.relative_to(self.project_root)
            return True
        except ValueError:
            return False

    def _is_sensitive_file(self, path: Path) -> bool:
        """Check if path matches sensitive file blacklist."""
        path_str = str(path).lower()
        return any(
            pattern.lower() in path_str
            for pattern in self.SENSITIVE_PATTERNS
        )


class MemoryGenerator(TemplateBasedMixin):
    """
    Generate structured memory files in .claude/memory/ from APM database.

    Memory Structure:
    - decisions/: Architecture decision records (from decisions table)
    - learnings/: Project learnings (from learnings table)
    - patterns/: Code patterns and conventions (from database)
    - context/: Project context (from project metadata)

    Features:
    - Database sync (decisions, learnings, memory_files tables)
    - Structured templates (decision.md.j2, learning.md.j2, etc.)
    - @import resolution with security validation
    - File hash tracking for change detection
    - Validation status tracking

    Example:
        >>> generator = MemoryGenerator(db_service)
        >>> files = generator.generate_memory_files(project, output_dir)
        >>> print(f"Generated {len(files)} memory files")
    """

    def __init__(self, db_service: DatabaseService):
        """
        Initialize memory generator.

        Args:
            db_service: Database service for accessing APM data

        Raises:
            FileNotFoundError: If template directory doesn't exist
        """
        self.db = db_service

        # Initialize Jinja2 templates
        template_dir = Path(__file__).parent / "templates" / "memory"
        self._init_templates(template_dir)

        # Register custom filters
        self._register_custom_filters()

    def generate_memory_files(
        self,
        project: Project,
        output_dir: Path,
        **kwargs
    ) -> List[FileOutput]:
        """
        Generate all memory files from database entities.

        Creates:
        - .claude/memory/decisions/decision-NNNN.md (from decisions table)
        - .claude/memory/learnings/learning-NNNN.md (from learnings table)
        - .claude/memory/patterns/pattern-NNNN.md (from patterns)
        - .claude/memory/context/project_context.md (from project metadata)

        Args:
            project: Project metadata
            output_dir: .claude directory path
            **kwargs: Optional parameters:
                - include_decisions (bool): Generate decision files (default: True)
                - include_learnings (bool): Generate learning files (default: True)
                - include_patterns (bool): Generate pattern files (default: True)
                - include_context (bool): Generate context file (default: True)
                - resolve_imports (bool): Resolve @import directives (default: True)

        Returns:
            List of FileOutput for each generated memory file

        Example:
            >>> files = generator.generate_memory_files(
            ...     project=project,
            ...     output_dir=Path("/project/.claude"),
            ...     include_decisions=True,
            ...     resolve_imports=True
            ... )
        """
        files: List[FileOutput] = []
        memory_dir = output_dir / "memory"
        memory_dir.mkdir(parents=True, exist_ok=True)

        # Initialize import resolver
        project_root = output_dir.parent  # .claude -> project root
        resolver = SecureImportResolver(project_root) if kwargs.get("resolve_imports", True) else None

        # 1. Generate decision files (from decisions table)
        if kwargs.get("include_decisions", True):
            decision_files = self._generate_decision_files(
                project=project,
                memory_dir=memory_dir,
                resolver=resolver
            )
            files.extend(decision_files)

        # 2. Generate learning files (from learnings table)
        if kwargs.get("include_learnings", True):
            learning_files = self._generate_learning_files(
                project=project,
                memory_dir=memory_dir,
                resolver=resolver
            )
            files.extend(learning_files)

        # 3. Generate pattern files (from database patterns)
        if kwargs.get("include_patterns", True):
            pattern_files = self._generate_pattern_files(
                project=project,
                memory_dir=memory_dir,
                resolver=resolver
            )
            files.extend(pattern_files)

        # 4. Generate project context (from project metadata)
        if kwargs.get("include_context", True):
            context_file = self._generate_context_file(
                project=project,
                memory_dir=memory_dir,
                resolver=resolver
            )
            files.append(context_file)

        # 5. Track generated files in memory_files table
        self._track_memory_files(project, files)

        return files

    def _generate_decision_files(
        self,
        project: Project,
        memory_dir: Path,
        resolver: Optional[SecureImportResolver]
    ) -> List[FileOutput]:
        """
        Generate decision files from decisions table.

        Args:
            project: Project metadata
            memory_dir: .claude/memory directory path
            resolver: Optional import resolver

        Returns:
            List of FileOutput for decision files
        """
        files: List[FileOutput] = []
        decisions_dir = memory_dir / "decisions"
        decisions_dir.mkdir(parents=True, exist_ok=True)

        # Query decisions from database
        # Note: decisions table schema may not exist yet (Task 1134)
        # Gracefully handle missing table
        try:
            decisions = self.db.execute(
                """
                SELECT id, title, decision, context, consequences, alternatives, status
                FROM decisions
                WHERE project_id = ?
                ORDER BY created_at DESC
                """,
                (project.id,)
            ).fetchall()
        except Exception:
            # Table doesn't exist yet, return empty list
            decisions = []

        for decision in decisions:
            # Render template
            context = {
                "decision": decision,
                "project": project,
                "generation_time": datetime.utcnow().isoformat()
            }

            content = self._render_template("decision.md.j2", context)

            # Resolve imports if enabled
            if resolver:
                content = resolver.resolve(content, decisions_dir)

            # Write file
            output_path = decisions_dir / f"decision-{decision['id']:04d}.md"
            output_path.write_text(content)

            files.append(FileOutput.create_from_content(output_path, content))

        return files

    def _generate_learning_files(
        self,
        project: Project,
        memory_dir: Path,
        resolver: Optional[SecureImportResolver]
    ) -> List[FileOutput]:
        """
        Generate learning files from learnings table.

        Args:
            project: Project metadata
            memory_dir: .claude/memory directory path
            resolver: Optional import resolver

        Returns:
            List of FileOutput for learning files
        """
        files: List[FileOutput] = []
        learnings_dir = memory_dir / "learnings"
        learnings_dir.mkdir(parents=True, exist_ok=True)

        # Query learnings from database
        # Note: learnings table schema may not exist yet (Task 1134)
        # Gracefully handle missing table
        try:
            learnings = self.db.execute(
                """
                SELECT id, title, learning, context, examples, category
                FROM learnings
                WHERE project_id = ?
                ORDER BY created_at DESC
                """,
                (project.id,)
            ).fetchall()
        except Exception:
            # Table doesn't exist yet, return empty list
            learnings = []

        for learning in learnings:
            # Render template
            context = {
                "learning": learning,
                "project": project,
                "generation_time": datetime.utcnow().isoformat()
            }

            content = self._render_template("learning.md.j2", context)

            # Resolve imports if enabled
            if resolver:
                content = resolver.resolve(content, learnings_dir)

            # Write file
            output_path = learnings_dir / f"learning-{learning['id']:04d}.md"
            output_path.write_text(content)

            files.append(FileOutput.create_from_content(output_path, content))

        return files

    def _generate_pattern_files(
        self,
        project: Project,
        memory_dir: Path,
        resolver: Optional[SecureImportResolver]
    ) -> List[FileOutput]:
        """
        Generate pattern files from database patterns.

        Args:
            project: Project metadata
            memory_dir: .claude/memory directory path
            resolver: Optional import resolver

        Returns:
            List of FileOutput for pattern files
        """
        files: List[FileOutput] = []
        patterns_dir = memory_dir / "patterns"
        patterns_dir.mkdir(parents=True, exist_ok=True)

        # Query patterns from database (if patterns table exists)
        # For now, create a default patterns file from project conventions

        context = {
            "project": project,
            "patterns": self._extract_patterns_from_project(project),
            "generation_time": datetime.utcnow().isoformat()
        }

        content = self._render_template("pattern.md.j2", context)

        # Resolve imports if enabled
        if resolver:
            content = resolver.resolve(content, patterns_dir)

        # Write file
        output_path = patterns_dir / "patterns.md"
        output_path.write_text(content)

        files.append(FileOutput.create_from_content(output_path, content))

        return files

    def _generate_context_file(
        self,
        project: Project,
        memory_dir: Path,
        resolver: Optional[SecureImportResolver]
    ) -> FileOutput:
        """
        Generate project context file from project metadata.

        Args:
            project: Project metadata
            memory_dir: .claude/memory directory path
            resolver: Optional import resolver

        Returns:
            FileOutput for context file
        """
        context_dir = memory_dir / "context"
        context_dir.mkdir(parents=True, exist_ok=True)

        # Render template
        context = {
            "project": project,
            "generation_time": datetime.utcnow().isoformat()
        }

        content = self._render_template("context.md.j2", context)

        # Resolve imports if enabled
        if resolver:
            content = resolver.resolve(content, context_dir)

        # Write file
        output_path = context_dir / "project_context.md"
        output_path.write_text(content)

        return FileOutput.create_from_content(output_path, content)

    def _extract_patterns_from_project(self, project: Project) -> List[Dict[str, Any]]:
        """
        Extract coding patterns from project metadata.

        Args:
            project: Project metadata

        Returns:
            List of pattern dictionaries
        """
        # Default patterns from project conventions
        patterns = [
            {
                "name": "Three-Layer Architecture",
                "description": "Models → Adapters → Methods pattern for database operations",
                "category": "architecture",
                "examples": []
            },
            {
                "name": "Database-First",
                "description": "All data operations go through database, not files",
                "category": "data",
                "examples": []
            },
            {
                "name": "Template-Based Generation",
                "description": "Use Jinja2 templates for code generation, not f-strings",
                "category": "code-generation",
                "examples": []
            }
        ]

        return patterns

    def _track_memory_files(
        self,
        project: Project,
        files: List[FileOutput]
    ) -> None:
        """
        Track generated memory files in memory_files table.

        Args:
            project: Project metadata
            files: List of generated files
        """
        now = datetime.utcnow().isoformat()

        for file_output in files:
            # Determine file type from path
            file_type = self._infer_file_type(file_output.path)
            if not file_type:
                continue

            # Calculate content hash
            content_hash = hashlib.sha256(file_output.content.encode()).hexdigest()

            # Upsert into memory_files table
            try:
                self.db.execute(
                    """
                    INSERT INTO memory_files (
                        project_id, file_type, file_path, file_hash, content,
                        source_tables, template_version, confidence_score,
                        completeness_score, validation_status, generated_by,
                        generated_at, created_at, updated_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ON CONFLICT(project_id, file_type) DO UPDATE SET
                        file_path = excluded.file_path,
                        file_hash = excluded.file_hash,
                        content = excluded.content,
                        generated_at = excluded.generated_at,
                        updated_at = excluded.updated_at
                    """,
                    (
                        project.id,
                        file_type,
                        str(file_output.path),
                        content_hash,
                        file_output.content,
                        json.dumps([]),  # source_tables (to be populated)
                        "1.0.0",  # template_version
                        1.0,  # confidence_score
                        1.0,  # completeness_score
                        "validated",  # validation_status
                        "memory_generator",  # generated_by
                        now,  # generated_at
                        now,  # created_at
                        now   # updated_at
                    )
                )
                self.db.commit()
            except Exception as e:
                print(f"⚠️ Failed to track memory file {file_output.path}: {e}")

    def _infer_file_type(self, path: Path) -> Optional[str]:
        """
        Infer file type from path for memory_files table.

        Args:
            path: File path

        Returns:
            File type or None if not memory file
        """
        path_str = str(path)

        if "memory/decisions/" in path_str:
            return "ideas"  # Decisions tracked as ideas
        elif "memory/learnings/" in path_str:
            return "principles"  # Learnings as principles
        elif "memory/patterns/" in path_str:
            return "principles"  # Patterns as principles
        elif "memory/context/" in path_str:
            return "project"  # Context as project info

        return None

    def _register_custom_filters(self) -> None:
        """Register memory-specific Jinja2 filters."""
        super()._register_custom_filters()

        # Add custom filters if needed
        pass
