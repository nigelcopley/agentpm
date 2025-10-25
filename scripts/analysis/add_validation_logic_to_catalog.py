#!/usr/bin/env python3
"""
Add validation logic to rules catalog.

This script analyzes the YAML rules catalog and adds appropriate validation_logic
fields based on rule types and patterns expected by the workflow service.
"""

import yaml
import re
from pathlib import Path
from typing import Dict, Any, List

def get_validation_logic_for_rule(rule: Dict[str, Any]) -> str:
    """Generate validation logic for a rule based on its type and config."""
    rule_id = rule.get('rule_id', '')
    name = rule.get('name', '')
    config = rule.get('config', {})
    enforcement_level = rule.get('enforcement_level', '')
    
    # Time-boxing rules (DP-001 to DP-011)
    if rule_id.startswith('DP-') and 'time-boxing' in name:
        if 'max_hours' in config and 'task_type' in config:
            task_type = config['task_type']
            max_hours = config['max_hours']
            return f"effort_hours > {max_hours} AND task_type == '{task_type}'"
        elif 'max_hours' in config:
            max_hours = config['max_hours']
            return f"effort_hours > {max_hours}"
    
    # Test coverage rules
    elif rule_id in ['DP-012', 'TEST-001'] or 'test-coverage' in name:
        if 'min_coverage' in config:
            threshold = config['min_coverage']
            return f"test_coverage < {threshold}"
        else:
            return "test_coverage < 90.0"
    
    # Required task types rules
    elif rule_id.startswith('WR-') and 'required-tasks' in name:
        return "missing_required_task_types"
    
    # Forbidden task types rules
    elif rule_id.startswith('WR-') and 'forbidden' in name:
        return "has_forbidden_task_types"
    
    # Code quality rules (mostly GUIDE level - no specific validation)
    elif rule_id.startswith('CQ-'):
        if 'naming' in name:
            return "naming_convention_violation"
        elif 'import' in name:
            return "import_violation"
        elif 'file' in name:
            return "file_structure_violation"
        else:
            return "code_quality_violation"
    
    # Documentation rules (mostly GUIDE level - no specific validation)
    elif rule_id.startswith('DOC-'):
        if 'docstring' in name:
            return "missing_docstring"
        elif 'readme' in name:
            return "missing_readme"
        else:
            return "documentation_violation"
    
    # Workflow rules
    elif rule_id.startswith('WF-'):
        if 'commit' in name:
            return "commit_frequency_violation"
        elif 'branch' in name:
            return "branch_protection_violation"
        else:
            return "workflow_violation"
    
    # Testing rules
    elif rule_id.startswith('TEST-'):
        if 'coverage' in name:
            return "test_coverage < 90.0"
        elif 'unit' in name:
            return "missing_unit_tests"
        elif 'integration' in name:
            return "missing_integration_tests"
        else:
            return "testing_violation"
    
    # Operations rules
    elif rule_id.startswith('OPS-'):
        if 'deployment' in name:
            return "deployment_violation"
        elif 'monitoring' in name:
            return "monitoring_violation"
        else:
            return "operations_violation"
    
    # Technology rules
    elif rule_id.startswith('TC-'):
        if 'framework' in name:
            return "framework_violation"
        elif 'pattern' in name:
            return "pattern_violation"
        else:
            return "technology_violation"
    
    # Governance rules
    elif rule_id.startswith('GOV-'):
        return "governance_violation"
    
    # Default fallback
    else:
        return "general_violation"

def add_validation_logic_to_catalog(catalog_path: Path) -> None:
    """Add validation logic to all rules in the catalog."""
    print(f"Loading catalog from {catalog_path}")
    
    with open(catalog_path) as f:
        catalog = yaml.safe_load(f)
    
    rules = catalog.get('rules', [])
    print(f"Processing {len(rules)} rules...")
    
    updated_count = 0
    for rule in rules:
        if 'validation_logic' not in rule or not rule['validation_logic']:
            validation_logic = get_validation_logic_for_rule(rule)
            rule['validation_logic'] = validation_logic
            updated_count += 1
            print(f"  Added validation logic to {rule['rule_id']}: {validation_logic}")
    
    print(f"\nUpdated {updated_count} rules with validation logic")
    
    # Write back to file
    with open(catalog_path, 'w') as f:
        yaml.dump(catalog, f, default_flow_style=False, sort_keys=False)
    
    print(f"Updated catalog saved to {catalog_path}")

def main():
    """Main function."""
    catalog_path = Path(__file__).parent.parent.parent / "agentpm" / "core" / "rules" / "config" / "rules_catalog.yaml"
    
    if not catalog_path.exists():
        print(f"Error: Catalog file not found at {catalog_path}")
        return 1
    
    try:
        add_validation_logic_to_catalog(catalog_path)
        print("\n✅ Successfully added validation logic to rules catalog")
        return 0
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    exit(main())
