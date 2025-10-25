# CLI Command Improvement Plan

**Work Item:** #76 - CLI Command Alignment & Enhancement Audit  
**Task:** #463 - Document CLI Improvements  
**Date:** 2025-01-12  
**Status:** In Progress  

## Overview

This document provides a comprehensive improvement plan for the APM (Agent Project Manager) CLI command interface, based on the findings from the CLI audit analysis. The plan addresses critical alignment issues, missing features, and enhancement opportunities identified in the systematic review.

## Phase 1: Critical Fixes (Week 1)

### 1.1 Fix Work Item Type Alignment

**Problem:** CLI allows 'analysis' work item type but database CHECK constraint doesn't include it.

**Solution:**
```sql
-- Migration: Add 'analysis' to work item type CHECK constraint
ALTER TABLE work_items RENAME TO old_work_items;

CREATE TABLE work_items (
    -- ... existing columns ...
    type TEXT NOT NULL CHECK(type IN (
        'feature', 'enhancement', 'bugfix', 'research', 'analysis', 
        'planning', 'refactoring', 'infrastructure'
    )),
    -- ... rest of schema ...
);

INSERT INTO work_items SELECT * FROM old_work_items;
DROP TABLE old_work_items;
```

**Files to Update:**
- `agentpm/core/database/migrations/files/migration_0020.py`
- `agentpm/core/database/utils/schema.py`

### 1.2 Add --why-value Support

**Problem:** Work item validation requires `metadata.why_value` but CLI doesn't provide option.

**Solution:**
```python
# agentpm/cli/commands/work_item/create.py
@click.option(
    '--why-value',
    help='Business justification as JSON: {"problem": "...", "desired_outcome": "...", "business_impact": "...", "target_metrics": "..."}'
)
@click.option(
    '--why-problem',
    help='Problem statement (alternative to --why-value)'
)
@click.option(
    '--why-outcome', 
    help='Desired outcome (alternative to --why-value)'
)
@click.option(
    '--why-impact',
    help='Business impact (alternative to --why-value)'
)
@click.option(
    '--why-metrics',
    help='Target metrics (alternative to --why-value)'
)
```

**Implementation:**
```python
def create(ctx, name, wi_type, description, priority, business_context, 
           why_value, why_problem, why_outcome, why_impact, why_metrics, ...):
    # Build why_value from individual parameters or JSON
    if why_value:
        try:
            why_data = json.loads(why_value)
        except json.JSONDecodeError:
            raise click.BadParameter("Invalid JSON in --why-value")
    else:
        # Build from individual parameters
        why_data = {
            "problem": why_problem or "",
            "desired_outcome": why_outcome or "",
            "business_impact": why_impact or "",
            "target_metrics": why_metrics or ""
        }
    
    # Add to metadata
    metadata = {
        "why_value": why_data,
        # ... other metadata
    }
```

**Files to Update:**
- `agentpm/cli/commands/work_item/create.py`
- `agentpm/cli/commands/work_item/update.py`

### 1.3 Add Idea Cancel Command

**Problem:** No way to cancel ideas via CLI.

**Solution:**
```python
# agentpm/cli/commands/idea/cancel.py
@click.command()
@click.argument('idea_id', type=int)
@click.option('--reason', help='Reason for cancellation')
@click.pass_context
def cancel(ctx: click.Context, idea_id: int, reason: str):
    """Cancel an idea (transition to cancelled status)."""
    console = ctx.obj['console']
    project_root = ensure_project_root(ctx)
    db = get_database_service(project_root)
    
    try:
        # Update idea status to cancelled
        idea_methods.update_idea_status(
            service=db,
            idea_id=idea_id,
            status=IdeaStatus.CANCELLED,
            reason=reason
        )
        
        console.print(f"✅ [green]Idea #{idea_id} cancelled[/green]")
        if reason:
            console.print(f"   Reason: {reason}")
            
    except Exception as e:
        console.print(f"❌ [red]Error cancelling idea: {e}[/red]")
        raise click.Abort()
```

**Database Update:**
```sql
-- Add 'cancelled' to idea status CHECK constraint
ALTER TABLE ideas RENAME TO old_ideas;

CREATE TABLE ideas (
    -- ... existing columns ...
    status TEXT DEFAULT 'idea' CHECK(status IN (
        'idea', 'research', 'design', 'accepted', 'converted', 'rejected', 'cancelled'
    )),
    -- ... rest of schema ...
);

INSERT INTO ideas SELECT * FROM old_ideas;
DROP TABLE old_ideas;
```

**Files to Create/Update:**
- `agentpm/cli/commands/idea/cancel.py`
- `agentpm/cli/commands/idea/__init__.py` (add cancel command)
- `agentpm/core/database/enums/idea.py` (add CANCELLED status)
- `agentpm/core/database/migrations/files/migration_0021.py`

### 1.4 Fix Context Type Support

**Problem:** CLI commands support different context types than database allows.

**Solution:**
```python
# agentpm/cli/commands/idea/context.py
@click.option('--context-type', 'context_type',
              type=click.Choice([
                  'project_context',
                  'work_item_context', 
                  'task_context',
                  'business_pillars_context',
                  'market_research_context',
                  'competitive_analysis_context',
                  'quality_gates_context',
                  'stakeholder_context',
                  'technical_context',
                  'implementation_context',
                  'idea_context',
                  'idea_to_work_item_mapping'
              ]),
              required=True,
              help='Type of rich context to create')
```

**Files to Update:**
- `agentpm/cli/commands/idea/context.py`
- `agentpm/cli/commands/context/rich.py`

## Phase 2: Missing Features (Week 2)

### 2.1 Evidence Management Commands

**Create:** `agentpm/cli/commands/evidence/`

```python
# evidence/__init__.py
@click.group()
def evidence():
    """Manage evidence sources for work items and ideas."""
    pass

@evidence.command()
@click.argument('entity_type', type=click.Choice(['work_item', 'idea', 'task']))
@click.argument('entity_id', type=int)
@click.option('--url', required=True, help='Evidence source URL')
@click.option('--type', 'source_type', 
              type=click.Choice(['documentation', 'research', 'stackoverflow', 'github', 'internal_doc', 'meeting_notes', 'expert_opinion']),
              required=True, help='Type of evidence source')
@click.option('--excerpt', help='Relevant excerpt from source')
@click.option('--confidence', type=float, help='Confidence score (0.0-1.0)')
def add(entity_type, entity_id, url, source_type, excerpt, confidence):
    """Add evidence source to entity."""

@evidence.command()
@click.argument('entity_type', type=click.Choice(['work_item', 'idea', 'task']))
@click.argument('entity_id', type=int)
def list(entity_type, entity_id):
    """List evidence sources for entity."""

@evidence.command()
@click.argument('evidence_id', type=int)
def show(evidence_id):
    """Show evidence source details."""

@evidence.command()
@click.argument('evidence_id', type=int)
@click.option('--status', type=click.Choice(['verified', 'stale', 'broken', 'unverified']))
def update_status(evidence_id, status):
    """Update evidence source verification status."""
```

### 2.2 Document Reference Commands

**Create:** `agentpm/cli/commands/document/`

```python
# document/__init__.py
@click.group()
def document():
    """Manage document references for work items and tasks."""
    pass

@document.command()
@click.argument('entity_type', type=click.Choice(['work_item', 'task']))
@click.argument('entity_id', type=int)
@click.option('--title', required=True, help='Document title')
@click.option('--type', 'doc_type',
              type=click.Choice(['architecture', 'design', 'specification', 'user_guide', 'api_docs', 'test_plan', 'deployment_guide', 'troubleshooting', 'changelog', 'other']),
              required=True, help='Document type')
@click.option('--path', help='File path to document')
@click.option('--url', help='URL to document')
@click.option('--format', type=click.Choice(['markdown', 'html', 'pdf', 'text', 'json', 'yaml', 'other']))
def add(entity_type, entity_id, title, doc_type, path, url, format):
    """Add document reference to entity."""

@document.command()
@click.argument('entity_type', type=click.Choice(['work_item', 'task']))
@click.argument('entity_id', type=int)
def list(entity_type, entity_id):
    """List document references for entity."""
```

### 2.3 Session Learning Commands

**Create:** `agentpm/cli/commands/learning/`

```python
# learning/__init__.py
@click.group()
def learning():
    """Manage session learnings and knowledge capture."""
    pass

@learning.command()
@click.option('--type', 'learning_type',
              type=click.Choice(['decision', 'pattern', 'discovery', 'constraint', 'antipattern', 'optimization', 'security', 'integration', 'best_practice']),
              required=True, help='Type of learning')
@click.option('--content', required=True, help='Learning content')
@click.option('--context', help='Additional context')
@click.option('--confidence', type=float, help='Confidence score (0.0-1.0)')
@click.option('--tags', help='Comma-separated tags')
def record(learning_type, content, context, confidence, tags):
    """Record a learning from current session."""

@learning.command()
@click.option('--type', 'learning_type', help='Filter by learning type')
@click.option('--tags', help='Filter by tags')
@click.option('--limit', type=int, default=20, help='Number of results to show')
def list(learning_type, tags, limit):
    """List recent learnings."""

@learning.command()
@click.argument('learning_id', type=int)
def show(learning_id):
    """Show learning details."""
```

### 2.4 Agent Relationship Commands

**Create:** `agentpm/cli/commands/agent/relationship.py`

```python
@click.group()
def relationship():
    """Manage agent relationships and specializations."""
    pass

@relationship.command()
@click.argument('agent_id', type=int)
@click.argument('related_agent_id', type=int)
@click.option('--type', 'relationship_type',
              type=click.Choice(['collaborates_with', 'reports_to', 'mentors', 'specializes_in', 'depends_on']),
              required=True, help='Type of relationship')
@click.option('--description', help='Relationship description')
def add(agent_id, related_agent_id, relationship_type, description):
    """Add relationship between agents."""

@relationship.command()
@click.argument('agent_id', type=int)
def list(agent_id):
    """List relationships for agent."""

@relationship.command()
@click.argument('relationship_id', type=int)
def remove(relationship_id):
    """Remove agent relationship."""
```

## Phase 3: Standardization (Week 3)

### 3.1 Standardize Parameter Naming

**Current Issues:**
- `--business-context` vs `--why-value`
- `--context-type` vs `--type`
- `--entity-type` vs `--entity`

**Standardization Rules:**
1. Use `--type` for categorical selections
2. Use `--context` for context-related parameters
3. Use `--entity` for entity-related parameters
4. Use `--data` for JSON data parameters
5. Use `--id` for identifier parameters

**Implementation:**
```python
# Standard parameter definitions
STANDARD_OPTIONS = {
    'entity_type': click.Option(['--entity-type'], type=click.Choice(['work_item', 'task', 'idea', 'project'])),
    'entity_id': click.Option(['--entity-id'], type=int),
    'context_type': click.Option(['--context-type'], type=click.Choice([...])),
    'context_data': click.Option(['--data'], type=str),
    'confidence': click.Option(['--confidence'], type=float),
    'priority': click.Option(['--priority'], type=click.IntRange(1, 5)),
    'effort': click.Option(['--effort'], type=float, callback=validate_effort_hours)
}
```

### 3.2 Improve Error Messages

**Current Error:**
```bash
❌ Error: CHECK constraint failed: type IN (...)
```

**Improved Error:**
```bash
❌ Error: Work item type 'analysis' not supported.

   Valid types: feature, enhancement, bugfix, research, planning, refactoring, infrastructure
   
   💡 Suggestions:
   • Use 'research' for analysis work items
   • Use 'planning' for architectural analysis
   • Use 'feature' for new functionality
   
   📚 See: apm work-item create --help
```

**Implementation:**
```python
# agentpm/cli/utils/error_handling.py
class CLIErrorHandler:
    @staticmethod
    def handle_constraint_error(error: Exception, context: str) -> str:
        """Convert database constraint errors to actionable CLI errors."""
        if "CHECK constraint failed" in str(error):
            if "type IN" in str(error):
                return CLIErrorHandler._handle_type_constraint_error(error, context)
            elif "status IN" in str(error):
                return CLIErrorHandler._handle_status_constraint_error(error, context)
        return str(error)
    
    @staticmethod
    def _handle_type_constraint_error(error: Exception, context: str) -> str:
        """Handle type constraint errors with helpful suggestions."""
        if "work_item" in context:
            return """
❌ Error: Work item type not supported.

   Valid types: feature, enhancement, bugfix, research, planning, refactoring, infrastructure
   
   💡 Suggestions:
   • Use 'research' for analysis work items
   • Use 'planning' for architectural analysis
   • Use 'feature' for new functionality
   
   📚 See: apm work-item create --help
            """
        # ... other contexts
```

### 3.3 Add Comprehensive Help Text

**Implementation:**
```python
@click.command()
@click.argument('name')
@click.option('--type', 'wi_type', required=True, help='Work item type')
@click.option('--description', '-d', help='Work item description')
@click.option('--priority', '-p', type=click.IntRange(1, 5), default=3, help='Priority (1=highest, 5=lowest)')
@click.option('--why-value', help='Business justification as JSON')
@click.option('--business-context', help='Business context and impact')
@click.option('--acceptance-criteria', help='JSON array of acceptance criteria')
@click.option('--who', help='WHO: Target users/stakeholders')
@click.option('--what', help='WHAT: What is being built')
@click.option('--when', help='WHEN: Timeline and deadlines')
@click.option('--where', help='WHERE: Location/environment')
@click.option('--why', help='WHY: Business justification')
@click.option('--how', help='HOW: Implementation approach')
@click.option('--scope', help='Scope definition as JSON')
@click.option('--ownership', help='Ownership and RACI roles as JSON')
@click.option('--artifacts', help='Expected artifacts as JSON')
@click.option('--dependencies', help='Dependencies as JSON array')
@click.option('--blockers', help='Blockers as JSON array')
@click.option('--due-date', help='Due date (YYYY-MM-DD)')
@click.option('--not-before', help='Start date (YYYY-MM-DD)')
@click.pass_context
def create(ctx, name, wi_type, description, priority, why_value, business_context, 
           acceptance_criteria, who, what, when, where, why, how, scope, 
           ownership, artifacts, dependencies, blockers, due_date, not_before):
    """
    Create a new work item.
    
    Work items represent substantial deliverables that break down into multiple tasks.
    They enforce quality gates and time-boxing constraints.
    
    \b
    Work Item Types:
      feature        Build new capability/system
      enhancement    Improve existing capability  
      bugfix         Fix substantial defect (epic-level bug)
      research       Investigation/spike (gather information)
      planning       Architecture/design/roadmap (make decisions)
      refactoring    Large-scale code improvement (no feature change)
      infrastructure DevOps/platform work (CI/CD, deployment, tooling)
    
    \b
    Quality Gates:
      • FEATURE requires: DESIGN + IMPLEMENTATION + TESTING + DOCUMENTATION
      • ENHANCEMENT requires: DESIGN + IMPLEMENTATION + TESTING
      • BUGFIX requires: ANALYSIS + BUGFIX + TESTING
      • All work items require metadata.why_value for business justification
    
    \b
    Examples:
      # Create feature work item
      apm work-item create "User Authentication" --type=feature \\
          --why-value='{"problem": "No user auth", "desired_outcome": "Secure login", "business_impact": "Enable user accounts", "target_metrics": "100% user coverage"}' \\
          --who="End users" --what="Login system" --when="Q1 2025" \\
          --acceptance-criteria='["Users can login", "JWT tokens issued", "Password reset works"]'
      
      # Create research work item  
      apm work-item create "Database Technology Research" --type=research \\
          --why-value='{"problem": "Need to choose DB", "desired_outcome": "Technology decision", "business_impact": "Foundation for all features", "target_metrics": "Performance benchmarks"}' \\
          --what="Evaluate PostgreSQL vs MongoDB" --when="2 weeks"
      
      # Create with 6W framework
      apm work-item create "API Rate Limiting" --type=enhancement \\
          --who="API consumers" --what="Rate limiting middleware" \\
          --when="Sprint 3" --where="Production API" \\
          --why="Prevent abuse" --how="Redis-based sliding window"
    
    \b
    Business Context:
      Use --why-value for structured business justification or --business-context
      for free-form description. The why_value format is:
      
      {
        "problem": "What problem does this solve?",
        "desired_outcome": "What should the result be?", 
        "business_impact": "Why is this important?",
        "target_metrics": "How will we measure success?"
      }
    
    \b
    Metadata Options:
      --scope: {"in_scope": ["item1", "item2"], "out_of_scope": ["item3"]}
      --ownership: {"responsible": "ai_agent", "accountable": "ai_agent", "consulted": "ai_team", "informed": "stakeholders"}
      --artifacts: {"code_paths": ["path1", "path2"], "docs_paths": ["doc1", "doc2"]}
      --dependencies: [{"type": "work_item", "id": 123, "dependency_type": "hard"}]
      --blockers: [{"type": "external", "description": "Waiting for approval"}]
    
    \b
    See Also:
      apm work-item list          # List all work items
      apm work-item show <id>     # Show work item details
      apm task create             # Create tasks for work item
      apm work-item validate <id> # Validate work item quality gates
    """
```

## Phase 4: Enhancement (Week 4)

### 4.1 Performance Optimization

**Lazy Loading Implementation:**
```python
# agentpm/cli/main.py - Extend LazyGroup
class LazyGroup(click.Group):
    def get_command(self, ctx: click.Context, cmd_name: str) -> Optional[click.Command]:
        # Add caching for loaded commands
        if not hasattr(self, '_command_cache'):
            self._command_cache = {}
        
        if cmd_name in self._command_cache:
            return self._command_cache[cmd_name]
        
        # Load command
        command = self._load_command(ctx, cmd_name)
        if command:
            self._command_cache[cmd_name] = command
        
        return command
```

**Pagination for List Commands:**
```python
@click.option('--page', type=int, default=1, help='Page number')
@click.option('--per-page', type=int, default=20, help='Items per page')
@click.option('--format', type=click.Choice(['table', 'json', 'csv']), default='table')
def list(page, per_page, format):
    """List work items with pagination."""
    offset = (page - 1) * per_page
    items = work_item_methods.list_work_items(
        service=db,
        limit=per_page,
        offset=offset
    )
    
    if format == 'json':
        console.print(json.dumps([item.dict() for item in items], indent=2))
    elif format == 'csv':
        # CSV output
    else:
        # Rich table output
```

### 4.2 Security Hardening

**Input Validation:**
```python
# agentpm/cli/utils/security.py
class SecurityValidator:
    @staticmethod
    def validate_json_input(data: str, schema: dict) -> dict:
        """Validate JSON input against schema."""
        try:
            parsed = json.loads(data)
            jsonschema.validate(parsed, schema)
            return parsed
        except json.JSONDecodeError:
            raise click.BadParameter("Invalid JSON format")
        except jsonschema.ValidationError as e:
            raise click.BadParameter(f"JSON validation failed: {e.message}")
    
    @staticmethod
    def sanitize_file_path(path: str) -> str:
        """Sanitize file path to prevent directory traversal."""
        # Remove .. and normalize path
        normalized = os.path.normpath(path)
        if '..' in normalized or normalized.startswith('/'):
            raise click.BadParameter("Invalid file path")
        return normalized
    
    @staticmethod
    def validate_url(url: str) -> str:
        """Validate URL format."""
        try:
            result = urllib.parse.urlparse(url)
            if not result.scheme or not result.netloc:
                raise ValueError("Invalid URL")
            return url
        except Exception:
            raise click.BadParameter("Invalid URL format")
```

**Rate Limiting:**
```python
# agentpm/cli/utils/rate_limiting.py
class RateLimiter:
    def __init__(self, max_requests: int = 100, window_seconds: int = 3600):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests = []
    
    def check_limit(self) -> bool:
        """Check if request is within rate limit."""
        now = time.time()
        # Remove old requests
        self.requests = [req_time for req_time in self.requests 
                        if now - req_time < self.window_seconds]
        
        if len(self.requests) >= self.max_requests:
            return False
        
        self.requests.append(now)
        return True
```

### 4.3 User Experience Improvements

**Interactive Mode:**
```python
# agentpm/cli/utils/interactive.py
class InteractiveMode:
    @staticmethod
    def create_work_item_interactive():
        """Interactive work item creation."""
        console = Console()
        
        # Collect information step by step
        name = Prompt.ask("Work item name")
        
        # Show type options with descriptions
        type_options = [
            ("feature", "Build new capability/system"),
            ("enhancement", "Improve existing capability"),
            ("bugfix", "Fix substantial defect"),
            ("research", "Investigation/spike"),
            ("planning", "Architecture/design/roadmap"),
            ("refactoring", "Large-scale code improvement"),
            ("infrastructure", "DevOps/platform work")
        ]
        
        wi_type = Prompt.ask(
            "Work item type",
            choices=[opt[0] for opt in type_options],
            show_choices=True
        )
        
        # Show description for selected type
        for opt in type_options:
            if opt[0] == wi_type:
                console.print(f"[dim]{opt[1]}[/dim]")
                break
        
        # Continue with other fields...
        return create_work_item(name, wi_type, ...)
```

**Progress Indicators:**
```python
# agentpm/cli/utils/progress.py
class ProgressIndicator:
    @staticmethod
    def show_progress(task_name: str, total: int):
        """Show progress bar for long operations."""
        with Progress() as progress:
            task = progress.add_task(task_name, total=total)
            
            for i in range(total):
                # Do work
                progress.update(task, advance=1)
                time.sleep(0.1)
```

## Implementation Timeline

### Week 1: Critical Fixes
- **Day 1-2:** Fix work item type alignment
- **Day 3-4:** Add --why-value support
- **Day 5:** Add idea cancel command
- **Day 6-7:** Fix context type support

### Week 2: Missing Features
- **Day 1-2:** Evidence management commands
- **Day 3-4:** Document reference commands
- **Day 5-6:** Session learning commands
- **Day 7:** Agent relationship commands

### Week 3: Standardization
- **Day 1-2:** Standardize parameter naming
- **Day 3-4:** Improve error messages
- **Day 5-6:** Add comprehensive help text
- **Day 7:** Add input validation

### Week 4: Enhancement
- **Day 1-2:** Performance optimization
- **Day 3-4:** Security hardening
- **Day 5-6:** User experience improvements
- **Day 7:** Testing and documentation

## Success Metrics

### Alignment Metrics
- **100%** CLI-database constraint alignment
- **0** validation mismatches
- **100%** enum consistency

### Feature Coverage
- **100%** database features accessible via CLI
- **All** required commands implemented
- **Complete** command group coverage

### Performance Metrics
- **<100ms** command startup time
- **<2s** command execution time
- **<1s** database query time

### Quality Metrics
- **100%** actionable error messages
- **100%** comprehensive help text
- **100%** input validation coverage

### User Experience
- **Consistent** parameter naming
- **Intuitive** command structure
- **Helpful** error messages and suggestions

## Testing Strategy

### Unit Tests
- Test all new commands
- Test parameter validation
- Test error handling
- Test database integration

### Integration Tests
- Test command workflows
- Test database constraints
- Test error scenarios
- Test performance

### User Acceptance Tests
- Test common workflows
- Test error scenarios
- Test help text quality
- Test user experience

## Conclusion

This comprehensive improvement plan addresses all critical issues identified in the CLI audit. The phased approach ensures immediate fixes for critical problems while building toward a robust, user-friendly command interface.

The plan focuses on:
1. **Alignment:** Ensuring CLI commands match database constraints
2. **Completeness:** Adding missing features and commands
3. **Consistency:** Standardizing parameters and error handling
4. **Quality:** Improving user experience and performance

Implementation of this plan will result in a CLI interface that is fully aligned with the database schema, provides complete feature coverage, and delivers an excellent user experience for AI agents and human users alike.
