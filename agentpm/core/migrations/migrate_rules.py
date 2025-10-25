#!/usr/bin/env python3
"""
V1 Rules Migration Script

Migrates all _RULES/*.md files to V2 database rules table.

**Work Item**: WI-40 (V2 Consolidation)
**Task**: #214 (Implementation, 4h)

**Input**: /Users/nigelcopley/.project_manager/_RULES/ (15 files)
**Output**: rules table populated with 245+ structured entries

**Usage**:
    python migrate_rules.py --project-id 1 --rules-dir /path/to/_RULES
    python migrate_rules.py --project-id 1  # Uses default path
    python migrate_rules.py --help

**Features**:
- Parses all _RULES/*.md files for structured rules
- Extracts rule ID, name, description, enforcement level
- Maps to categories (CI, GR, DEV, CQ, TEST, DG, OP, WF, ARCH)
- Bulk insert with transaction safety and rollback
- Validates completeness and reports statistics

**Design**: v2-consolidation-architecture.md Section 4.3
"""

import argparse
import re
import sqlite3
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional


@dataclass
class Rule:
    """Parsed rule from _RULES markdown files"""
    rule_id: str
    name: str
    description: str
    category: str
    enforcement_level: str
    validation_logic: Optional[str] = None
    error_message: Optional[str] = None
    config: Optional[str] = None


class RulesParser:
    """Parse _RULES markdown files to extract structured rules"""

    # Rule ID patterns (CI-001, GR-001, DEV-001, etc.)
    RULE_PATTERN = re.compile(r'\*\*([A-Z]+-\d+):\s*(.+?)\*\*')

    # Category mapping
    CATEGORIES = {
        'CI': 'compliance_integration',
        'GR': 'general_rules',
        'DEV': 'development_principles',
        'CQ': 'code_quality',
        'TEST': 'testing',
        'TES': 'testing',
        'DG': 'data_governance',
        'OP': 'operational',
        'WF': 'workflow',
        'ARCH': 'architecture',
        'DOC': 'documentation'
    }

    # Enforcement level detection (from rule content)
    ENFORCEMENT_KEYWORDS = {
        'BLOCK': ['MUST', 'MANDATORY', 'REQUIRED', 'NEVER', 'CRITICAL'],
        'LIMIT': ['SHOULD', 'RECOMMENDED', 'PREFERRED', 'ENCOURAGED'],
        'GUIDE': ['CONSIDER', 'SUGGEST', 'GUIDANCE', 'BEST PRACTICE'],
        'ENHANCE': ['OPTIONAL', 'ENHANCEMENT', 'IMPROVEMENT']
    }

    def __init__(self, rules_dir: Path):
        self.rules_dir = rules_dir
        self.rules: List[Rule] = []
        self.global_seen_ids: set = set()  # Track globally to prevent cross-file duplicates

    def parse_all_files(self) -> List[Rule]:
        """Parse all _RULES/*.md files"""
        print(f"📂 Scanning {self.rules_dir}...")

        md_files = sorted(self.rules_dir.glob("*.md"))
        if not md_files:
            print(f"❌ No markdown files found in {self.rules_dir}")
            return []

        print(f"   Found {len(md_files)} markdown files")

        for md_file in md_files:
            if md_file.name in ['README.md', 'RULES_COVERAGE_MATRIX.md', 'QUICK_REFERENCE.md']:
                continue  # Skip meta files
            self._parse_file(md_file)

        print(f"✅ Parsed {len(self.rules)} rules from {len(md_files)} files")
        return self.rules

    def _parse_file(self, file_path: Path) -> None:
        """Parse single markdown file for rules"""
        print(f"   Parsing {file_path.name}...", end='')

        content = file_path.read_text(encoding='utf-8')
        matches = self.RULE_PATTERN.findall(content)

        if not matches:
            print(" (no structured rules)")
            return

        # Track seen rule IDs to avoid duplicates within same file
        seen_ids = set()
        count = 0
        for rule_id, name in matches:
            # Skip duplicates (take first occurrence globally)
            if rule_id in seen_ids or rule_id in self.global_seen_ids:
                continue
            seen_ids.add(rule_id)
            self.global_seen_ids.add(rule_id)

            rule = self._extract_rule_details(rule_id, name, content)
            if rule:
                self.rules.append(rule)
                count += 1

        print(f" {count} rules")

    def _extract_rule_details(self, rule_id: str, name: str, content: str) -> Optional[Rule]:
        """Extract detailed rule information from content"""
        # Determine category from prefix
        prefix = rule_id.split('-')[0]
        category = self.CATEGORIES.get(prefix, 'other')

        # Find rule section in content
        rule_section = self._find_rule_section(rule_id, content)
        if not rule_section:
            # Simple rule without detailed section
            return Rule(
                rule_id=rule_id,
                name=name.strip(),
                description=name.strip(),
                category=category,
                enforcement_level=self._detect_enforcement_level(name)
            )

        # Extract description from rule section
        description = self._extract_description(rule_section)

        # Extract validation logic (if present)
        validation_logic = self._extract_validation_logic(rule_section)

        # Extract error message (if present)
        error_message = self._extract_error_message(rule_section)

        # Extract configuration (YAML blocks)
        config = self._extract_config(rule_section)

        return Rule(
            rule_id=rule_id,
            name=name.strip(),
            description=description,
            category=category,
            enforcement_level=self._detect_enforcement_level(rule_section),
            validation_logic=validation_logic,
            error_message=error_message,
            config=config
        )

    def _find_rule_section(self, rule_id: str, content: str) -> Optional[str]:
        """Find the section of content for a specific rule"""
        # Find rule header
        pattern = re.escape(f"**{rule_id}:")
        match = re.search(pattern, content)
        if not match:
            return None

        # Extract from rule header to next rule or section
        start = match.start()
        next_rule = re.search(r'\*\*[A-Z]+-\d+:', content[start + 10:])
        next_section = re.search(r'^##+ ', content[start + 10:], re.MULTILINE)

        end = None
        if next_rule and next_section:
            end = start + 10 + min(next_rule.start(), next_section.start())
        elif next_rule:
            end = start + 10 + next_rule.start()
        elif next_section:
            end = start + 10 + next_section.start()

        return content[start:end] if end else content[start:]

    def _extract_description(self, rule_section: str) -> str:
        """Extract description from rule section"""
        # Remove rule header
        lines = rule_section.split('\n')
        desc_lines = []

        in_description = False
        for line in lines[1:]:  # Skip rule header
            stripped = line.strip()

            # Stop at YAML block or subsections
            if stripped.startswith('```') or stripped.startswith('##'):
                break

            # Skip empty lines at start
            if not in_description and not stripped:
                continue

            in_description = True
            if stripped:
                desc_lines.append(stripped)

        return ' '.join(desc_lines)[:500]  # Limit to 500 chars

    def _extract_validation_logic(self, rule_section: str) -> Optional[str]:
        """Extract validation logic from rule section"""
        # Look for validation patterns
        patterns = [
            r'validation_method:\s*"([^"]+)"',
            r'validation:\s*"([^"]+)"',
            r'enforcement:\s*"([^"]+)"'
        ]

        for pattern in patterns:
            match = re.search(pattern, rule_section)
            if match:
                return match.group(1)

        return None

    def _extract_error_message(self, rule_section: str) -> Optional[str]:
        """Extract error message from rule section"""
        # Look for error message patterns
        patterns = [
            r'failure_action:\s*"([^"]+)"',
            r'error_message:\s*"([^"]+)"',
            r'Fix:\s+(.+?)(?:\n|$)'
        ]

        for pattern in patterns:
            match = re.search(pattern, rule_section)
            if match:
                return match.group(1)[:200]  # Limit to 200 chars

        return None

    def _extract_config(self, rule_section: str) -> Optional[str]:
        """Extract YAML configuration block from rule section"""
        # Find YAML blocks
        yaml_match = re.search(r'```yaml\n(.*?)\n```', rule_section, re.DOTALL)
        if yaml_match:
            return yaml_match.group(1)[:1000]  # Limit to 1000 chars

        return None

    def _detect_enforcement_level(self, text: str) -> str:
        """Detect enforcement level from rule text"""
        text_upper = text.upper()

        # Check each enforcement level
        for level, keywords in self.ENFORCEMENT_KEYWORDS.items():
            for keyword in keywords:
                if keyword in text_upper:
                    return level

        # Default to GUIDE
        return 'GUIDE'

    def get_statistics(self) -> Dict[str, int]:
        """Get parsing statistics"""
        stats = {
            'total': len(self.rules),
            'by_category': {},
            'by_enforcement': {}
        }

        for rule in self.rules:
            # Count by category
            stats['by_category'][rule.category] = stats['by_category'].get(rule.category, 0) + 1

            # Count by enforcement
            stats['by_enforcement'][rule.enforcement_level] = stats['by_enforcement'].get(rule.enforcement_level, 0) + 1

        return stats


class RulesMigrator:
    """Migrate parsed rules to V2 database"""

    def __init__(self, db_path: Path, project_id: int):
        self.db_path = db_path
        self.project_id = project_id

    def migrate(self, rules: List[Rule], dry_run: bool = False) -> bool:
        """Migrate rules to database with transaction safety"""
        if not rules:
            print("❌ No rules to migrate")
            return False

        print(f"\n📊 Migration Summary:")
        print(f"   Database: {self.db_path}")
        print(f"   Project ID: {self.project_id}")
        print(f"   Rules to migrate: {len(rules)}")

        if dry_run:
            print("\n🔍 DRY RUN - No changes will be made")
            self._preview_migration(rules)
            return True

        # Connect to database
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            # Start transaction
            cursor.execute("BEGIN TRANSACTION")

            # Check if project exists
            cursor.execute("SELECT id FROM projects WHERE id = ?", (self.project_id,))
            if not cursor.fetchone():
                print(f"❌ Project {self.project_id} does not exist")
                conn.close()
                return False

            # Clear existing rules for this project (fresh migration)
            cursor.execute("DELETE FROM rules WHERE project_id = ?", (self.project_id,))
            deleted = cursor.rowcount
            if deleted > 0:
                print(f"   Cleared {deleted} existing rules")

            # Insert rules
            inserted = 0
            for rule in rules:
                cursor.execute("""
                    INSERT INTO rules (
                        project_id, rule_id, name, description, category,
                        enforcement_level, validation_logic, error_message, config, enabled
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 1)
                """, (
                    self.project_id,
                    rule.rule_id,
                    rule.name,
                    rule.description,
                    rule.category,
                    rule.enforcement_level,
                    rule.validation_logic,
                    rule.error_message,
                    rule.config
                ))
                inserted += 1

            # Commit transaction
            conn.commit()
            print(f"✅ Inserted {inserted} rules successfully")

            # Verify migration
            cursor.execute("SELECT COUNT(*) FROM rules WHERE project_id = ?", (self.project_id,))
            final_count = cursor.fetchone()[0]
            print(f"✅ Verified {final_count} rules in database")

            conn.close()
            return True

        except sqlite3.Error as e:
            print(f"❌ Database error: {e}")
            if 'conn' in locals():
                conn.rollback()
                conn.close()
            return False
        except Exception as e:
            print(f"❌ Migration error: {e}")
            if 'conn' in locals():
                conn.rollback()
                conn.close()
            return False

    def _preview_migration(self, rules: List[Rule]) -> None:
        """Preview migration without making changes"""
        print("\n📋 Sample Rules (first 10):")
        for i, rule in enumerate(rules[:10], 1):
            print(f"\n   {i}. {rule.rule_id}: {rule.name}")
            print(f"      Category: {rule.category}")
            print(f"      Enforcement: {rule.enforcement_level}")
            print(f"      Description: {rule.description[:80]}...")

        if len(rules) > 10:
            print(f"\n   ... and {len(rules) - 10} more rules")


def main():
    """Main migration script"""
    parser = argparse.ArgumentParser(
        description="Migrate V1 _RULES to V2 database",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Migrate with default paths
  python migrate_rules.py --project-id 1

  # Specify custom rules directory
  python migrate_rules.py --project-id 1 --rules-dir /path/to/_RULES

  # Dry run (preview without changes)
  python migrate_rules.py --project-id 1 --dry-run

  # Specify custom database
  python migrate_rules.py --project-id 1 --db-path /path/to/project.db
        """
    )

    parser.add_argument(
        '--project-id',
        type=int,
        required=True,
        help='Project ID in V2 database'
    )
    parser.add_argument(
        '--rules-dir',
        type=Path,
        default=Path('/Users/nigelcopley/.project_manager/_RULES'),
        help='Path to _RULES directory (default: /Users/nigelcopley/.project_manager/_RULES)'
    )
    parser.add_argument(
        '--db-path',
        type=Path,
        default=None,
        help='Path to V2 database (default: current directory/.aipm/data/aipm.db)'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Preview migration without making changes'
    )

    args = parser.parse_args()

    # Validate rules directory
    if not args.rules_dir.exists():
        print(f"❌ Rules directory not found: {args.rules_dir}")
        return 1

    # Determine database path
    if args.db_path is None:
        db_path = Path.cwd() / '.aipm' / 'data' / 'aipm.db'
    else:
        db_path = args.db_path

    if not db_path.exists() and not args.dry_run:
        print(f"❌ Database not found: {db_path}")
        print("   Run 'apm init' to create the database first")
        return 1

    print("🚀 V1 Rules Migration to V2 Database")
    print("=" * 60)

    # Parse rules
    parser = RulesParser(args.rules_dir)
    rules = parser.parse_all_files()

    if not rules:
        print("❌ No rules found to migrate")
        return 1

    # Show statistics
    stats = parser.get_statistics()
    print(f"\n📈 Parsing Statistics:")
    print(f"   Total rules: {stats['total']}")
    print(f"\n   By Category:")
    for category, count in sorted(stats['by_category'].items()):
        print(f"      {category}: {count}")
    print(f"\n   By Enforcement:")
    for level, count in sorted(stats['by_enforcement'].items()):
        print(f"      {level}: {count}")

    # Migrate rules
    migrator = RulesMigrator(db_path, args.project_id)
    success = migrator.migrate(rules, dry_run=args.dry_run)

    if success:
        print("\n✅ Migration completed successfully!")
        return 0
    else:
        print("\n❌ Migration failed")
        return 1


if __name__ == '__main__':
    sys.exit(main())
