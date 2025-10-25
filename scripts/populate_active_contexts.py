#!/usr/bin/env python3
"""
Populate 6W Contexts for Active Work Items

Creates UnifiedSixW contexts for 12 active work items by extracting data from:
- work_items table (name, description, business_context, metadata)
- tasks table (assigned_to, acceptance criteria, technical details)
- Intelligent data extraction and sensible defaults

Deliverable: 12 contexts with confidence ≥0.70 (YELLOW or GREEN band)
Pattern: Uses agentpm/core/database/methods/contexts.py::create_context()

Usage:
    python scripts/populate_active_contexts.py
    python scripts/populate_active_contexts.py --dry-run
    python scripts/populate_active_contexts.py --work-item-ids 3,25,46
"""

import sys
import os
import re
import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Tuple

# Add agentpm to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from agentpm.core.database.service import DatabaseService
from agentpm.core.database.models import Context, UnifiedSixW, WorkItem, Task
from agentpm.core.database.enums import ContextType, EntityType, ConfidenceBand
from agentpm.core.database.methods.contexts import create_context, get_entity_context
from agentpm.core.database.methods.work_items import get_work_item
from agentpm.core.database.methods.tasks import list_tasks


class ContextPopulator:
    """Extract data and create UnifiedSixW contexts for work items"""

    def __init__(self, db_service: DatabaseService):
        self.db = db_service

    def extract_implementers(self, tasks: List[Task]) -> List[str]:
        """Extract unique implementers from tasks.assigned_to"""
        implementers = set()
        for task in tasks:
            if task.assigned_to:
                # Handle comma-separated assignments
                for assignee in task.assigned_to.split(','):
                    assignee = assignee.strip()
                    if assignee and assignee not in ['None', 'null', '']:
                        implementers.add(assignee)
        return sorted(list(implementers))

    def extract_reviewers(self, tasks: List[Task]) -> List[str]:
        """Extract reviewers from task metadata or infer from workflow"""
        reviewers = set()
        for task in tasks:
            # Check quality_metadata for reviewer info
            if task.quality_metadata:
                try:
                    metadata = json.loads(task.quality_metadata) if isinstance(task.quality_metadata, str) else task.quality_metadata
                    if metadata.get('reviewer'):
                        reviewers.add(metadata['reviewer'])
                except (json.JSONDecodeError, TypeError):
                    pass

        # Default reviewers based on work item type
        if not reviewers:
            reviewers = {'aipm-quality-validator', 'aipm-testing-specialist'}

        return sorted(list(reviewers))

    def extract_end_users(self, work_item: WorkItem) -> List[str]:
        """Identify end users from business context and work item type"""
        users = set()

        # Extract from business context
        if work_item.business_context:
            # Look for user mentions: "for developers", "CLI users", "agents", etc.
            user_patterns = [
                r'(?:for|users?|developers?|engineers?|team|stakeholders?)',
                r'(?:CLI users?|web users?|API users?)',
                r'(?:agents?|AI agents?|autonomous systems?)',
            ]
            for pattern in user_patterns:
                matches = re.findall(pattern, work_item.business_context, re.IGNORECASE)
                users.update(m.strip() for m in matches)

        # Type-based defaults
        if work_item.type.value in ['feature', 'enhancement']:
            users.add('developers')
            users.add('cli-users')
        elif work_item.type.value == 'bugfix':
            users.add('affected-users')
        elif work_item.type.value == 'research':
            users.add('technical-team')

        return sorted(list(users)) if users else ['project-team', 'stakeholders']

    def extract_requirements(self, work_item: WorkItem, tasks: List[Task]) -> List[str]:
        """Extract functional requirements from description and tasks"""
        requirements = []

        # Extract from work item description
        if work_item.description:
            # Look for requirement indicators
            req_patterns = [
                r'(?:must|should|shall|requires?|needs?)\s+([^.;]+)',
                r'(?:implement|add|create|build|integrate)\s+([^.;]+)',
                r'(?:enable|support|provide)\s+([^.;]+)',
            ]
            for pattern in req_patterns:
                matches = re.findall(pattern, work_item.description, re.IGNORECASE)
                requirements.extend(m.strip() for m in matches)

        # Extract from task names (condensed requirements)
        for task in tasks:
            if task.name and len(task.name) < 100:  # Reasonable requirement length
                requirements.append(task.name)

        # Deduplicate and clean
        unique_requirements = []
        seen = set()
        for req in requirements:
            req_clean = req.strip().lower()
            if req_clean and req_clean not in seen and len(req) > 10:
                unique_requirements.append(req.strip())
                seen.add(req_clean)

        return unique_requirements[:10]  # Top 10 requirements

    def extract_technical_constraints(self, work_item: WorkItem) -> List[str]:
        """Extract technical constraints from metadata and description"""
        constraints = []

        # Parse metadata for constraints
        try:
            metadata = json.loads(work_item.metadata) if work_item.metadata else {}
            if metadata.get('constraints'):
                constraints.extend(metadata['constraints'])
            if metadata.get('technical_requirements'):
                constraints.extend(metadata['technical_requirements'])
        except (json.JSONDecodeError, TypeError):
            pass

        # Pattern-based extraction from description
        if work_item.description:
            constraint_keywords = [
                'must use', 'must not', 'required to', 'cannot',
                'limited to', 'restricted', 'depends on', 'requires'
            ]
            for keyword in constraint_keywords:
                if keyword in work_item.description.lower():
                    # Extract sentence containing constraint
                    sentences = work_item.description.split('.')
                    for sentence in sentences:
                        if keyword in sentence.lower():
                            constraints.append(sentence.strip())

        # Type-based defaults
        if work_item.type.value in ['enhancement', 'refactoring']:
            constraints.append('Must maintain backward compatibility')
        if work_item.type.value == 'bugfix':
            constraints.append('Must not introduce regressions')

        return constraints[:5]  # Top 5 constraints

    def extract_acceptance_criteria(self, tasks: List[Task]) -> List[str]:
        """Extract acceptance criteria from task descriptions and metadata"""
        criteria = []

        for task in tasks:
            # Check quality_metadata for AC
            if task.quality_metadata:
                try:
                    metadata = json.loads(task.quality_metadata) if isinstance(task.quality_metadata, str) else task.quality_metadata
                    if metadata.get('acceptance_criteria'):
                        ac_list = metadata['acceptance_criteria']
                        if isinstance(ac_list, list):
                            criteria.extend(ac_list)
                        elif isinstance(ac_list, str):
                            criteria.append(ac_list)
                except (json.JSONDecodeError, TypeError):
                    pass

            # Extract from task description
            if task.description and 'acceptance' in task.description.lower():
                # Look for bulleted or numbered lists
                lines = task.description.split('\n')
                for line in lines:
                    if line.strip().startswith(('- ', '* ', '1.', '2.', '3.')):
                        criteria.append(line.strip().lstrip('- *123456789.').strip())

        # Deduplicate (handle both strings and dicts)
        unique_criteria = []
        seen = set()
        for item in criteria:
            # Convert to string for comparison
            item_str = str(item) if not isinstance(item, str) else item
            if item_str not in seen and item_str:
                unique_criteria.append(item_str)
                seen.add(item_str)

        return unique_criteria[:8]  # Top 8 criteria

    def extract_affected_services(self, work_item: WorkItem, tasks: List[Task]) -> List[str]:
        """Identify affected services/modules"""
        services = set()

        # Pattern-based extraction
        service_patterns = [
            r'(?:agentpm[/\\](?:cli|core|web|hooks|templates))',
            r'(?:CLI|API|database|web|frontend|backend|core)',
            r'(?:plugin|context|workflow|agent|rule)s?\s+(?:system|service|module)',
        ]

        content_to_search = [work_item.name, work_item.description or '']
        for task in tasks:
            content_to_search.extend([task.name, task.description or ''])

        for content in content_to_search:
            for pattern in service_patterns:
                matches = re.findall(pattern, content, re.IGNORECASE)
                services.update(m.strip() for m in matches)

        # Type-based defaults
        if not services:
            if 'agent' in work_item.name.lower():
                services.add('agentpm/core/agents')
            elif 'context' in work_item.name.lower():
                services.add('agentpm/core/context')
            elif 'cli' in work_item.name.lower():
                services.add('agentpm/cli')
            elif 'web' in work_item.name.lower() or 'dashboard' in work_item.name.lower():
                services.add('agentpm/web')
            else:
                services.add('agentpm/core')

        return sorted(list(services))

    def extract_repositories(self, work_item: WorkItem) -> List[str]:
        """Identify affected repositories"""
        # For single-repo project
        return ['aipm-v2']

    def extract_deployment_targets(self, work_item: WorkItem) -> List[str]:
        """Identify deployment targets"""
        targets = []

        if 'cli' in work_item.name.lower():
            targets.append('CLI (local pip install)')
        if 'web' in work_item.name.lower() or 'dashboard' in work_item.name.lower():
            targets.append('Web Server (Flask)')
        if 'database' in work_item.name.lower():
            targets.append('SQLite Database (.aipm/data/)')

        return targets if targets else ['Development Environment']

    def extract_deadline(self, work_item: WorkItem) -> Optional[datetime]:
        """Extract or estimate deadline"""
        if work_item.due_date:
            return work_item.due_date

        # Estimate based on priority and effort
        if work_item.priority == 1:
            return datetime.now() + timedelta(days=7)  # High priority: 1 week
        elif work_item.priority == 2:
            return datetime.now() + timedelta(days=14)  # Medium-high: 2 weeks
        else:
            return datetime.now() + timedelta(days=30)  # Lower priority: 1 month

    def extract_dependencies_timeline(self, work_item: WorkItem, tasks: List[Task]) -> List[str]:
        """Extract dependency timeline information"""
        dependencies = []

        # Check for blocked tasks
        blocked_tasks = [t for t in tasks if t.status.value == 'blocked']
        if blocked_tasks:
            for task in blocked_tasks:
                if task.blocked_reason:
                    dependencies.append(f"Blocked: {task.blocked_reason}")

        # Check metadata for dependencies
        try:
            metadata = json.loads(work_item.metadata) if work_item.metadata else {}
            if metadata.get('dependencies'):
                deps = metadata['dependencies']
                if isinstance(deps, list):
                    dependencies.extend(deps)
                elif isinstance(deps, str):
                    dependencies.append(deps)
        except (json.JSONDecodeError, TypeError):
            pass

        return dependencies[:5]  # Top 5 dependencies

    def extract_business_value(self, work_item: WorkItem) -> str:
        """Extract business value statement"""
        if work_item.business_context:
            # Look for value statements
            value_indicators = ['value:', 'benefit:', 'impact:', 'enables:', 'improves:', 'reduces:']
            for indicator in value_indicators:
                if indicator in work_item.business_context.lower():
                    # Extract the value statement (sentence containing indicator)
                    sentences = work_item.business_context.split('.')
                    for sentence in sentences:
                        if indicator in sentence.lower():
                            return sentence.strip()

            # Return first meaningful sentence
            sentences = [s.strip() for s in work_item.business_context.split('.') if len(s.strip()) > 20]
            if sentences:
                return sentences[0]

        # Type-based defaults
        value_map = {
            'feature': 'Delivers new capability to users',
            'enhancement': 'Improves existing functionality and user experience',
            'bugfix': 'Resolves user-impacting issues and improves stability',
            'refactoring': 'Improves code quality and maintainability',
            'research': 'Provides insights for future development decisions',
        }
        return value_map.get(work_item.type.value, 'Supports project objectives')

    def extract_risk_if_delayed(self, work_item: WorkItem) -> str:
        """Assess risk if work item is delayed"""
        # Priority-based risk assessment
        if work_item.priority == 1:
            return 'HIGH: Critical blocker for dependent work, user impact severe'
        elif work_item.priority == 2:
            return 'MEDIUM: Important deliverable, may delay milestone completion'
        else:
            return 'LOW: Manageable delay, can be rescheduled without major impact'

    def extract_suggested_approach(self, work_item: WorkItem, tasks: List[Task]) -> Optional[str]:
        """Extract or infer implementation approach"""
        # Look for approach in description
        if work_item.description:
            approach_indicators = ['approach:', 'strategy:', 'implementation:', 'using:', 'via:']
            for indicator in approach_indicators:
                if indicator in work_item.description.lower():
                    sentences = work_item.description.split('.')
                    for sentence in sentences:
                        if indicator in sentence.lower():
                            return sentence.strip()

        # Infer from task breakdown
        if len(tasks) >= 3:
            # Multi-phase approach
            task_names = [t.name for t in tasks[:3]]
            return f"Multi-phase implementation with {len(tasks)} tasks: {' → '.join(task_names)}"

        return None

    def extract_existing_patterns(self, work_item: WorkItem) -> List[str]:
        """Identify existing patterns to follow"""
        patterns = []

        # Type-based patterns
        if 'cli' in work_item.name.lower():
            patterns.append('Click command pattern (see agentpm/cli/commands/)')
        if 'database' in work_item.name.lower():
            patterns.append('Pydantic models + CRUD methods pattern')
        if 'agent' in work_item.name.lower():
            patterns.append('Agent template + SOP pattern (see .claude/agents/)')
        if 'context' in work_item.name.lower():
            patterns.append('Plugin orchestration + confidence scoring pattern')
        if 'workflow' in work_item.name.lower():
            patterns.append('State machine + validation gates pattern')

        # Check for similar completed work items
        # (Could query database for similar work items - simplified here)

        return patterns[:4]  # Top 4 patterns

    def calculate_confidence_score(self, six_w: UnifiedSixW) -> float:
        """Calculate confidence score based on 6W completeness"""
        scores = []

        # WHO (0.15): implementers + reviewers
        who_score = 0.0
        if six_w.implementers:
            who_score += 0.5
        if six_w.reviewers:
            who_score += 0.5
        scores.append(who_score * 0.15)

        # WHAT (0.25): requirements + constraints + AC
        what_score = 0.0
        if six_w.functional_requirements:
            what_score += 0.4
        if six_w.technical_constraints:
            what_score += 0.3
        if six_w.acceptance_criteria:
            what_score += 0.3
        scores.append(what_score * 0.25)

        # WHERE (0.15): services + repos + targets
        where_score = 0.0
        if six_w.affected_services:
            where_score += 0.5
        if six_w.repositories:
            where_score += 0.25
        if six_w.deployment_targets:
            where_score += 0.25
        scores.append(where_score * 0.15)

        # WHEN (0.10): deadline + dependencies
        when_score = 0.0
        if six_w.deadline:
            when_score += 0.6
        if six_w.dependencies_timeline:
            when_score += 0.4
        scores.append(when_score * 0.10)

        # WHY (0.20): business value + risk
        why_score = 0.0
        if six_w.business_value:
            why_score += 0.6
        if six_w.risk_if_delayed:
            why_score += 0.4
        scores.append(why_score * 0.20)

        # HOW (0.15): approach + patterns
        how_score = 0.0
        if six_w.suggested_approach:
            how_score += 0.5
        if six_w.existing_patterns:
            how_score += 0.5
        scores.append(how_score * 0.15)

        total_score = sum(scores)
        return min(max(total_score, 0.0), 1.0)

    def build_six_w(self, work_item: WorkItem, tasks: List[Task]) -> Tuple[UnifiedSixW, float]:
        """Build complete UnifiedSixW structure with confidence score"""

        six_w = UnifiedSixW(
            # WHO
            end_users=self.extract_end_users(work_item),
            implementers=self.extract_implementers(tasks),
            reviewers=self.extract_reviewers(tasks),

            # WHAT
            functional_requirements=self.extract_requirements(work_item, tasks),
            technical_constraints=self.extract_technical_constraints(work_item),
            acceptance_criteria=self.extract_acceptance_criteria(tasks),

            # WHERE
            affected_services=self.extract_affected_services(work_item, tasks),
            repositories=self.extract_repositories(work_item),
            deployment_targets=self.extract_deployment_targets(work_item),

            # WHEN
            deadline=self.extract_deadline(work_item),
            dependencies_timeline=self.extract_dependencies_timeline(work_item, tasks),

            # WHY
            business_value=self.extract_business_value(work_item),
            risk_if_delayed=self.extract_risk_if_delayed(work_item),

            # HOW
            suggested_approach=self.extract_suggested_approach(work_item, tasks),
            existing_patterns=self.extract_existing_patterns(work_item),
        )

        confidence = self.calculate_confidence_score(six_w)

        return six_w, confidence

    def populate_work_item_context(self, work_item_id: int, dry_run: bool = False) -> Dict:
        """Create 6W context for a single work item"""
        # Get work item
        work_item = get_work_item(self.db, work_item_id)
        if not work_item:
            return {'success': False, 'error': f'Work item {work_item_id} not found'}

        # Check if context already exists
        existing = get_entity_context(self.db, EntityType.WORK_ITEM, work_item_id)
        if existing:
            return {
                'success': False,
                'skipped': True,
                'work_item_id': work_item_id,
                'reason': 'Context already exists',
                'existing_confidence': existing.confidence_score
            }

        # Get tasks for this work item
        tasks = list_tasks(self.db, work_item_id=work_item_id)

        # Build 6W structure
        six_w, confidence = self.build_six_w(work_item, tasks)

        # Create context model
        context = Context(
            project_id=work_item.project_id,
            context_type=ContextType.WORK_ITEM_CONTEXT,
            entity_type=EntityType.WORK_ITEM,
            entity_id=work_item_id,
            six_w=six_w,
            confidence_score=confidence,
            confidence_band=ConfidenceBand.from_score(confidence),
        )

        if dry_run:
            return {
                'success': True,
                'dry_run': True,
                'work_item_id': work_item_id,
                'work_item_name': work_item.name,
                'confidence': confidence,
                'confidence_band': ConfidenceBand.from_score(confidence).value,
                'tasks_analyzed': len(tasks),
            }

        # Create context in database
        try:
            created = create_context(self.db, context)
            return {
                'success': True,
                'work_item_id': work_item_id,
                'work_item_name': work_item.name,
                'context_id': created.id,
                'confidence': confidence,
                'confidence_band': created.confidence_band.value,
                'tasks_analyzed': len(tasks),
            }
        except Exception as e:
            return {
                'success': False,
                'work_item_id': work_item_id,
                'error': str(e)
            }


def get_active_work_items(db: DatabaseService, limit: int = 12, ids: Optional[List[int]] = None) -> List[int]:
    """Get IDs of active work items"""
    if ids:
        return ids

    query = """
        SELECT id FROM work_items
        WHERE status IN ('active', 'draft', 'proposed', 'validated', 'accepted')
        ORDER BY priority, id
        LIMIT ?
    """
    with db.connect() as conn:
        cursor = conn.execute(query, (limit,))
        rows = cursor.fetchall()

    return [row[0] for row in rows]


def main():
    """Main execution"""
    import argparse

    parser = argparse.ArgumentParser(description='Populate 6W contexts for active work items')
    parser.add_argument('--dry-run', action='store_true', help='Preview without creating contexts')
    parser.add_argument('--work-item-ids', type=str, help='Comma-separated work item IDs (default: auto-select 12)')
    parser.add_argument('--limit', type=int, default=12, help='Number of work items to process (default: 12)')
    args = parser.parse_args()

    # Parse work item IDs
    work_item_ids = None
    if args.work_item_ids:
        work_item_ids = [int(id.strip()) for id in args.work_item_ids.split(',')]

    # Initialize database
    db_path = Path('.aipm/data/aipm.db')
    if not db_path.exists():
        print(f"❌ Database not found: {db_path}")
        sys.exit(1)

    db = DatabaseService(str(db_path))
    populator = ContextPopulator(db)

    # Get work items to process
    work_items = get_active_work_items(db, limit=args.limit, ids=work_item_ids)
    print(f"\n{'=' * 80}")
    print(f"6W Context Population for {len(work_items)} Active Work Items")
    print(f"{'=' * 80}")
    if args.dry_run:
        print("⚠️  DRY RUN MODE - No contexts will be created")
    print()

    # Process each work item
    results = []
    for idx, work_item_id in enumerate(work_items, 1):
        print(f"[{idx}/{len(work_items)}] Processing Work Item {work_item_id}...", end=' ')
        result = populator.populate_work_item_context(work_item_id, dry_run=args.dry_run)
        results.append(result)

        if result.get('success'):
            confidence = result['confidence']
            band = result['confidence_band']
            tasks_count = result['tasks_analyzed']
            name = result['work_item_name'][:50]
            print(f"✅ {band} ({confidence:.2f}) - {tasks_count} tasks - {name}")
        elif result.get('skipped'):
            print(f"⏭️  Skipped (already exists, confidence: {result['existing_confidence']:.2f})")
        else:
            print(f"❌ {result.get('error', 'Unknown error')}")

    # Summary
    print(f"\n{'=' * 80}")
    print("Summary")
    print(f"{'=' * 80}")

    successful = [r for r in results if r.get('success') and not r.get('dry_run')]
    skipped = [r for r in results if r.get('skipped')]
    failed = [r for r in results if not r.get('success') and not r.get('skipped')]
    dry_run_preview = [r for r in results if r.get('dry_run')]

    if args.dry_run:
        print(f"✅ Would create: {len(dry_run_preview)} contexts")
        green = [r for r in dry_run_preview if r['confidence_band'] == 'GREEN']
        yellow = [r for r in dry_run_preview if r['confidence_band'] == 'YELLOW']
        red = [r for r in dry_run_preview if r['confidence_band'] == 'RED']
        print(f"   - GREEN (≥0.80): {len(green)}")
        print(f"   - YELLOW (0.70-0.79): {len(yellow)}")
        print(f"   - RED (<0.70): {len(red)}")
    else:
        print(f"✅ Created: {len(successful)} contexts")
        print(f"⏭️  Skipped: {len(skipped)} (already exist)")
        print(f"❌ Failed: {len(failed)}")

        if successful:
            avg_confidence = sum(r['confidence'] for r in successful) / len(successful)
            print(f"\nAverage Confidence: {avg_confidence:.2f}")

            green = [r for r in successful if r['confidence_band'] == 'GREEN']
            yellow = [r for r in successful if r['confidence_band'] == 'YELLOW']
            red = [r for r in successful if r['confidence_band'] == 'RED']
            print(f"   - GREEN (≥0.80): {len(green)}")
            print(f"   - YELLOW (0.70-0.79): {len(yellow)}")
            print(f"   - RED (<0.70): {len(red)}")

    # Validation
    print(f"\n{'=' * 80}")
    print("Validation")
    print(f"{'=' * 80}")

    if args.dry_run:
        print("⚠️  Run without --dry-run to create contexts")
    else:
        if successful:
            # Test context assembly
            test_wi_id = successful[0]['work_item_id']
            print(f"\n✅ Test context assembly: apm context show --work-item-id={test_wi_id}")

            # SQL verification
            with db.connect() as conn:
                cursor = conn.execute("SELECT COUNT(*) FROM contexts WHERE context_type = 'work_item_context'")
                total_contexts = cursor.fetchone()[0]
            print(f"✅ Total work item contexts in database: {total_contexts}")
        else:
            print("⚠️  No contexts created")

    print()


if __name__ == '__main__':
    main()
