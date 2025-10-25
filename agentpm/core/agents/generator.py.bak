"""
Agent Generator - Intelligent Agent Creation

Generates project-specific agents by giving Claude:
1. Project context (domain, type, languages, frameworks, methodology, rules)
2. Base template directory
3. Instructions to create RELEVANT specialized agents

Claude decides which agents to create and how many of each type.

NEW (WI-32 Task #154): Added database integration methods:
- generate_and_store_agents() - Generate agents and save to database
- write_agent_sop_file() - Write .claude/agents/*.md files
"""

from pathlib import Path
from typing import Dict, Any, List, Optional
import json
import re

from .claude_integration import invoke_claude_code_headless


def build_agent_generation_prompt(
    project_context: Dict[str, Any],
    template_directory: Path
) -> str:
    """
    Build prompt for Claude to intelligently generate project-specific agents.

    Instead of filling 15 templates mechanically, Claude:
    - Analyzes the project
    - Chooses which agent types are needed
    - Creates 1-3 variants per type if needed (e.g., backend/frontend/api implementers)
    - Generates complete specialized agent instructions

    Args:
        project_context: Project metadata (domain, languages, frameworks, etc.)
        template_directory: Path to base template files

    Returns:
        Prompt string for Claude
    """
    # List available base templates
    template_files = sorted(template_directory.glob("*.md"))
    template_files = [f for f in template_files if f.name != 'README.md']

    archetype_list = "\n".join(f"  - {f.stem}: {_get_template_description(f)}"
                               for f in template_files)

    prompt = f"""You are generating AI agent instruction files for an APM (Agent Project Manager) project.

**Project Context**:
- Business Domain: {project_context.get('business_domain', 'General software')}
- Application Type: {project_context.get('app_type', 'Application')}
- Languages: {', '.join(project_context.get('languages', ['Unknown']))}
- Frameworks: {', '.join(project_context.get('frameworks', ['None detected']))}
- Database: {project_context.get('database', 'Unknown')}
- Testing: {', '.join(project_context.get('testing_frameworks', ['Unknown']))}
- Methodology: {project_context.get('methodology', 'Standard development')}
- Key Rules: {', '.join(project_context.get('rules', []))}

**Base Template Archetypes Available**:
{archetype_list}

**Your Task**:
Based on this project's tech stack and type, generate the SPECIFIC specialized agents needed.

**Important**:
1. Create ONLY agents relevant to THIS project's tech stack
2. Create MULTIPLE agents per archetype if the project needs them
   - Example: Django + React = backend-implementer, frontend-implementer, api-implementer (3 implementers)
   - Example: pytest + Jest = pytest-tester, jest-tester (2 testers)
3. Specialize each agent for its specific domain
   - backend-implementer knows Django models, views, ORM
   - frontend-implementer knows React components, hooks, state
4. Skip agents not relevant (e.g., no Go = no go-implementer)

**Output Format** (JSON for easy parsing):
```json
{{
  "agents": [
    {{
      "name": "backend-implementer",
      "archetype": "implementer",
      "description": "Django backend implementation specialist",
      "specialization": "Django models, views, serializers, ORM, REST APIs",
      "tech_focus": ["Python 3.11", "Django 4.2", "PostgreSQL"],
      "instructions": "Complete agent SOP here based on implementer archetype..."
    }},
    {{
      "name": "pytest-tester",
      "archetype": "tester",
      "description": "Python testing specialist",
      "specialization": "pytest fixtures, Django test client, coverage",
      "tech_focus": ["Python 3.11", "pytest", "Django testing"],
      "instructions": "Complete agent SOP here based on tester archetype..."
    }}
  ]
}}
```

Generate 5-10 specialized agents for this project in JSON format:"""

    return prompt


def _get_template_description(template_path: Path) -> str:
    """Extract description from template YAML frontmatter"""
    try:
        content = template_path.read_text()
        # Parse YAML frontmatter
        if content.startswith('---'):
            yaml_section = content.split('---')[1]
            for line in yaml_section.split('\n'):
                if line.startswith('description:'):
                    return line.replace('description:', '').strip()
    except Exception:
        pass
    return "Agent archetype"


def _fill_template_with_context(
    template_content: str,
    project_context: Dict[str, Any],
    agent_spec: Dict[str, Any]
) -> str:
    """
    Fill template with project-specific context.

    Replaces [INSTRUCTION: ...] placeholders with actual content from project.

    Args:
        template_content: Base template with [INSTRUCTION] markers
        project_context: Project metadata (tech_stack, patterns, rules)
        agent_spec: Agent specification (name, type, specialization)

    Returns:
        Filled template content
    """
    filled = template_content

    # Extract context
    tech_stack = project_context.get('tech_stack', [])
    frameworks = project_context.get('frameworks', [])
    languages = project_context.get('languages', [])
    patterns = project_context.get('patterns', [])
    rules = project_context.get('rules', [])

    # 1. Fill tech stack instructions
    if tech_stack or frameworks or languages:
        tech_list = []
        if languages:
            tech_list.extend([f"- Language: {lang}" for lang in languages])
        if frameworks:
            tech_list.extend([f"- Framework: {fw}" for fw in frameworks])
        if tech_stack:
            tech_list.extend([f"- Tool: {tech}" for tech in tech_stack if tech not in frameworks and tech not in languages])

        tech_text = "\n".join(tech_list) if tech_list else "- General purpose project"

        filled = filled.replace(
            "[INSTRUCTION: List detected languages, frameworks, libraries with versions]",
            tech_text
        )
        filled = filled.replace(
            "[INSTRUCTION: List all detected frameworks and versions from PluginOrchestrator]",
            tech_text
        )

    # 2. Fill pattern instructions
    if patterns:
        pattern_text = "\n\n".join([f"**{p['name']}**: {p['description']}" for p in patterns]) if isinstance(patterns[0], dict) else "\n".join([f"- {p}" for p in patterns])

        filled = filled.replace(
            "[INSTRUCTION: Extract key implementation patterns from project codebase]",
            pattern_text
        )
        filled = filled.replace(
            "[INSTRUCTION: Extract implementation patterns specific to this project]",
            pattern_text
        )
        filled = filled.replace(
            "[INSTRUCTION: Identify coding standards, linters, formatters used]",
            pattern_text
        )

    # 3. Fill rules instructions
    if rules:
        rules_text = "\n".join([f"- {rule}" for rule in rules]) if isinstance(rules, list) else str(rules)

        filled = filled.replace(
            "[INSTRUCTION: Query rules table for time-boxing limits, quality requirements, and enforcement levels]",
            rules_text
        )
        filled = filled.replace(
            "[INSTRUCTION: Query rules table WHERE enforcement_level='BLOCK' OR enforcement_level='LIMIT']",
            rules_text
        )

    # 4. Fill quality gate instructions
    filled = filled.replace(
        "[INSTRUCTION: Insert additional project-specific quality gates here]",
        "**Project-specific quality gates**: Use `apm rules list` to see active gates"
    )
    filled = filled.replace(
        "[INSTRUCTION: Add project-specific quality checks]",
        f"**{agent_spec.get('name', 'agent')}-specific quality checks**: Follow project coding standards and patterns"
    )

    # 5. Fill work item requirements
    filled = filled.replace(
        "[INSTRUCTION: Insert additional work item type requirements here]",
        "**Standard AIPM work item requirements apply** (see workflow rules above)"
    )

    # 6. Fill example instructions (basic placeholders for now)
    filled = filled.replace(
        "[INSTRUCTION: Insert 2-3 actual code examples from project showing correct patterns]",
        "**Code examples**: Use `apm context show --task <id>` to load project-specific examples"
    )
    filled = filled.replace(
        "[INSTRUCTION: Provide code examples showing \"the right way\" in this project]",
        "**Best practices**: Follow patterns in existing codebase (use Grep tool to find examples)"
    )

    # 7. Fill domain-specific instructions
    agent_focus = agent_spec.get('focus', '')
    specialization_text = f"**Specialization**: {agent_focus}\n\n**Focus Areas**: {agent_spec.get('specialization', 'General implementation')}"

    filled = filled.replace(
        "[INSTRUCTION: Extract implementation patterns specific to this project]",
        specialization_text
    )
    filled = filled.replace(
        "[INSTRUCTION: Show 2-3 exemplary implementation files to study]",
        "**Reference implementations**: Use Grep and Glob tools to find similar implementations in the codebase"
    )
    filled = filled.replace(
        "[INSTRUCTION: List 3-5 well-implemented files as reference examples]",
        "**Exemplary files**: Discover using `grep -r \"pattern\" .` to find well-implemented examples"
    )

    # 8. Fill workflow instructions
    filled = filled.replace(
        "[INSTRUCTION: Describe 2-3 typical implementation workflows]",
        "**Standard workflow**: validate → accept → start → implement → submit-review → (different agent) approve"
    )
    filled = filled.replace(
        "[INSTRUCTION: Example workflow with concrete steps]",
        "**Example**: `apm task validate 123 && apm task accept 123 --agent <role> && apm task start 123`"
    )

    # 9. Fill anti-pattern instructions
    filled = filled.replace(
        "[INSTRUCTION: Identify anti-patterns found in project history]",
        "**Common mistakes**: Check git history and closed issues for lessons learned"
    )
    filled = filled.replace(
        "[INSTRUCTION: Example: \"Don't [X] - instead do [Y]\"]",
        "**Pattern compliance**: Always follow existing project patterns over introducing new ones"
    )

    # 10. Fill quality check instructions
    filled = filled.replace(
        "[INSTRUCTION: Add project-specific quality checks]",
        f"**Agent-specific checks**: Validate work meets {agent_spec.get('name', 'agent')} quality standards"
    )

    # 11. Fill common structure instructions
    filled = filled.replace(
        "[INSTRUCTION: Show common project structures and architectural patterns]",
        "**Architecture**: Use `apm context show --work-item <id>` to load architecture context"
    )

    # 12. Fill any remaining [INSTRUCTION] placeholders with generic guidance
    # This catches any instructions we haven't explicitly handled
    import re
    remaining_instructions = re.findall(r'\[INSTRUCTION:[^\]]+\]', filled)
    for instruction in remaining_instructions:
        # Extract the instruction text
        instruction_text = instruction.replace('[INSTRUCTION:', '').replace(']', '').strip()
        # Replace with generic guidance
        filled = filled.replace(
            instruction,
            f"**Action needed**: {instruction_text} (use project analysis tools: Grep, Glob, Read)"
        )

    return filled


def _extract_tech_focus(project_context: Dict[str, Any]) -> List[str]:
    """
    Extract technology focus from project context.

    Args:
        project_context: Project metadata

    Returns:
        List of key technologies for agent focus
    """
    tech_focus = []

    # Languages
    languages = project_context.get('languages', [])
    tech_focus.extend(languages)

    # Frameworks
    frameworks = project_context.get('frameworks', [])
    tech_focus.extend(frameworks)

    # Database
    database = project_context.get('database')
    if database:
        tech_focus.append(database)

    # Testing frameworks
    testing = project_context.get('testing_frameworks', [])
    tech_focus.extend(testing)

    return tech_focus


def parse_claude_agent_response(response: str) -> List[Dict[str, Any]]:
    """
    Parse Claude's JSON response containing generated agents.

    Args:
        response: Claude's JSON output with agent definitions

    Returns:
        List of agent dictionaries
    """
    try:
        data = json.loads(response)
        return data.get('agents', [])
    except json.JSONDecodeError:
        # Fallback: try to extract JSON from markdown code blocks
        json_match = re.search(r'```json\s*(\{.*?\})\s*```', response, re.DOTALL)
        if json_match:
            data = json.loads(json_match.group(1))
            return data.get('agents', [])
        raise ValueError(f"Could not parse Claude response as JSON")


def generate_agents_with_claude(
    project_context: Dict[str, Any],
    template_directory: Path,
    use_real_claude: bool = False
) -> List[Dict[str, Any]]:
    """
    Generate project-specific agents by asking Claude to choose and create.

    Single Claude invocation that:
    1. Analyzes project context
    2. Chooses relevant agent archetypes
    3. Creates specialized variants (e.g., backend-impl, frontend-impl)
    4. Returns JSON with all agent definitions

    Args:
        project_context: Project metadata
        template_directory: Path to base templates
        use_real_claude: Use real Claude (slow) vs mock (fast)

    Returns:
        List of agent definitions (name, description, instructions)
    """
    # If using mock mode, use intelligent selection and template filling
    if not use_real_claude:
        from .selection import AgentSelector

        # Use selector to determine which agents to create
        selector = AgentSelector()
        selected_agents = selector.select_agents(project_context)

        # Fill templates for each selected agent
        filled_agents = []
        for agent_spec in selected_agents:
            # Load base template for this archetype
            archetype = agent_spec['type']
            template_path = template_directory / f"{archetype}.md"

            if not template_path.exists():
                # Skip if template doesn't exist
                continue

            # Load template content
            template_content = template_path.read_text(encoding='utf-8')

            # Fill template with project context
            filled_content = _fill_template_with_context(
                template_content,
                project_context,
                agent_spec
            )

            filled_agents.append({
                'name': agent_spec['name'],
                'archetype': archetype,
                'description': agent_spec.get('specialization', f"{archetype.title()} agent"),
                'specialization': agent_spec.get('focus', ''),
                'tech_focus': _extract_tech_focus(project_context),
                'instructions': filled_content
            })

        return filled_agents

    # Use real Claude
    prompt = build_agent_generation_prompt(project_context, template_directory)

    # Invoke Claude (or mock)
    response = invoke_claude_code_headless(
        prompt,
        project_context,
        use_mock=False,
        timeout_seconds=120  # Longer for intelligent selection
    )

    # Parse response
    agents = parse_claude_agent_response(response)

    return agents


# ========== DATABASE INTEGRATION (WI-32 Task #154) ==========

def embed_project_rules_in_sop(
    sop_content: str,
    project_rules: List[Dict[str, Any]]
) -> str:
    """
    Replace [INSTRUCTION] placeholders in agent SOP with actual project rules.

    Args:
        sop_content: Agent SOP content with [INSTRUCTION] placeholders
        project_rules: List of rule dictionaries from database

    Returns:
        SOP content with placeholders replaced by actual rules

    Example:
        >>> rules = [
        ...     {'rule_id': 'DP-001', 'name': 'time-boxing', 'enforcement_level': 'BLOCK',
        ...      'description': 'IMPLEMENTATION tasks limited to 4 hours'},
        ...     {'rule_id': 'CI-004', 'name': 'testing-quality', 'enforcement_level': 'BLOCK',
        ...      'description': '>90% test coverage required'}
        ... ]
        >>> sop = "[INSTRUCTION: Insert project-specific quality gates here]"
        >>> embed_project_rules_in_sop(sop, rules)
        '#### DP-001: time-boxing (BLOCK)\\n>90% test coverage required\\n\\n'
    """
    # Group rules by category
    rules_by_category = {}
    for rule in project_rules:
        category = rule.get('category', 'general')
        if category not in rules_by_category:
            rules_by_category[category] = []
        rules_by_category[category].append(rule)

    # Format quality gates
    quality_gates_text = []
    for rule in project_rules:
        if rule.get('enforcement_level') == 'BLOCK':
            quality_gates_text.append(
                f"#### {rule['rule_id']}: {rule['name']} (BLOCK)\n"
                f"{rule.get('description', 'No description')}\n"
            )

    quality_gates_section = "\n".join(quality_gates_text) if quality_gates_text else "No additional project-specific quality gates"

    # Format time-boxing rules (if DP-001 exists)
    time_boxing_text = "See workflow rules above for standard time-boxing limits"
    for rule in project_rules:
        if rule.get('rule_id') == 'DP-001':
            time_boxing_text = rule.get('description', time_boxing_text)

    # Format work item requirements (if exists)
    work_item_reqs_text = "See workflow rules above for standard work item requirements"
    for rule in project_rules:
        if 'work item' in rule.get('name', '').lower():
            work_item_reqs_text = rule.get('description', work_item_reqs_text)

    # Replace placeholders
    replacements = {
        '[INSTRUCTION: Insert additional project-specific quality gates here]': quality_gates_section,
        '[INSTRUCTION: Insert additional work item type requirements here]': work_item_reqs_text,
        '[INSTRUCTION: Query rules table for time-boxing limits, quality requirements, and enforcement levels]': (
            f"**Project-Specific Rules**:\n"
            f"- Time-boxing: {time_boxing_text}\n"
            f"- Quality gates: {len([r for r in project_rules if r.get('enforcement_level') == 'BLOCK'])} BLOCK-level gates active\n"
        ),
    }

    result = sop_content
    for placeholder, replacement in replacements.items():
        result = result.replace(placeholder, replacement)

    return result


def write_agent_sop_file(
    agent_dir: Path,
    role: str,
    sop_content: str,
    project_rules: Optional[List[Dict[str, Any]]] = None
) -> Path:
    """
    Write agent SOP content to .claude/agents/*.md file with embedded project rules.

    Args:
        agent_dir: Directory for agent files (e.g., .claude/agents/)
        role: Agent role (e.g., 'aipm-database-developer')
        sop_content: Full markdown SOP content
        project_rules: Optional list of project rules to embed (WI-52)

    Returns:
        Path to written file

    Example:
        >>> file_path = write_agent_sop_file(
        ...     Path('.claude/agents'),
        ...     'aipm-database-developer',
        ...     '# Database Developer\\n\\n## SOP...',
        ...     project_rules=[{'rule_id': 'DP-001', ...}]
        ... )
        >>> file_path  # Path('.claude/agents/aipm-database-developer.md')
    """
    # Embed project rules if provided (WI-52)
    if project_rules:
        sop_content = embed_project_rules_in_sop(sop_content, project_rules)

    agent_dir.mkdir(parents=True, exist_ok=True)
    file_path = agent_dir / f"{role}.md"
    file_path.write_text(sop_content, encoding='utf-8')

    return file_path


def generate_and_store_agents(
    db,  # DatabaseService
    project_id: int,
    project_context: Dict[str, Any],
    template_directory: Path,
    agent_output_dir: Path,
    use_real_claude: bool = False
) -> List['Agent']:  # type: ignore
    """
    Generate agents using Claude and store in database + filesystem.

    This is the main entry point combining:
    1. Claude-based agent generation
    2. Database storage (agent metadata)
    3. Filesystem storage (SOP files with embedded rules - WI-52)

    Args:
        db: DatabaseService instance
        project_id: Project ID for agent association
        project_context: Project metadata for generation
        template_directory: Base template directory
        agent_output_dir: Directory for SOP files (e.g., .claude/agents/)
        use_real_claude: Use real Claude API vs mock

    Returns:
        List of created Agent models with IDs populated

    Example:
        >>> agents = generate_and_store_agents(
        ...     db,
        ...     project_id=1,
        ...     project_context={'languages': ['Python'], 'frameworks': ['Django']},
        ...     template_directory=Path('docs/components/agents/specifications'),
        ...     agent_output_dir=Path('.claude/agents')
        ... )
        >>> len(agents)  # 7 agents created
    """
    from ..database.models import Agent
    from ..database.methods import agents as agent_methods

    # Fetch project rules for embedding (WI-52)
    project_rules = _fetch_project_rules(db, project_id)

    # Generate agents using Claude
    agent_defs = generate_agents_with_claude(
        project_context,
        template_directory,
        use_real_claude=use_real_claude
    )

    created_agents = []

    for agent_def in agent_defs:
        # Create Agent model
        agent = Agent(
            project_id=project_id,
            role=agent_def.get('name', ''),
            display_name=agent_def.get('description', agent_def.get('name', '')),
            description=agent_def.get('specialization', ''),
            capabilities=agent_def.get('tech_focus', []),
            agent_type=agent_def.get('archetype', 'implementer'),
            is_active=True,
        )

        # Save to database
        created = agent_methods.create_agent(db, agent)

        # Write SOP file with embedded rules (WI-52)
        sop_content = agent_def.get('instructions', '# Agent SOP\n\nNo instructions provided.')
        file_path = write_agent_sop_file(
            agent_output_dir,
            created.role,
            sop_content,
            project_rules=project_rules  # WI-52: Embed rules
        )

        # Mark as generated
        agent_methods.mark_agent_generated(
            db,
            created.id,
            str(file_path)
        )

        # Reload to get updated generated_at
        updated = agent_methods.get_agent(db, created.id)
        created_agents.append(updated)

    return created_agents


def _fetch_project_rules(db, project_id: int) -> List[Dict[str, Any]]:
    """
    Fetch project rules from database for embedding in agent SOPs.

    Args:
        db: DatabaseService instance
        project_id: Project ID

    Returns:
        List of rule dictionaries
    """
    with db.connect() as conn:
        cursor = conn.execute(
            """
            SELECT rule_id, name, description, enforcement_level, category, config
            FROM rules
            WHERE project_id = ? AND enabled = 1
            ORDER BY category, rule_id
            """,
            (project_id,)
        )
        rows = cursor.fetchall()

    return [
        {
            'rule_id': row['rule_id'],
            'name': row['name'],
            'description': row['description'],
            'enforcement_level': row['enforcement_level'],
            'category': row['category'],
            'config': row['config']
        }
        for row in rows
    ]
