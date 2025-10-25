#!/usr/bin/env python3
"""Generate rules_catalog.yaml from complete-rules-reference.md.

Parses the markdown reference and creates structured YAML catalog
with preset mappings for all 245 rules.
"""

import re
import yaml
from pathlib import Path
from typing import List, Dict, Any


def parse_rules_from_markdown(md_path: Path) -> List[Dict[str, Any]]:
    """Parse all rules from markdown reference.
    
    Returns:
        List of rule dictionaries
    """
    with open(md_path) as f:
        content = f.read()
    
    # Pattern: **DP-001**: name | description | rationale
    pattern = r'\*\*([A-Z]{2,4}-\d{3})\*\*:\s+([a-z0-9-]+)(?:\s+✅\s+MVP)?\s+\|\s+([^|]+)\s+\|\s+(.+)'
    
    matches = re.findall(pattern, content, re.MULTILINE)
    
    rules = []
    for rule_id, name, description, rationale in matches:
        # Determine category from prefix
        category = rule_id.split('-')[0]
        
        # Determine preset inclusion (strategic selection)
        presets = determine_presets(rule_id, name, category)
        
        # Determine enforcement level
        enforcement = determine_enforcement(rule_id, name, category)
        
        # Extract config if mentioned
        config = extract_config(description, rationale)
        
        rule = {
            'rule_id': rule_id,
            'name': name,
            'description': description.strip(),
            'rationale': rationale.strip(),
            'category': category,
            'enforcement_level': enforcement,
            'presets': presets,
            'config': config,
            'enabled_by_default': True
        }
        
        rules.append(rule)
    
    return rules


def determine_presets(rule_id: str, name: str, category: str) -> List[str]:
    """Determine which presets include this rule.
    
    Strategy: Breadth over depth for early presets
    """
    presets = []
    
    # Enterprise gets everything
    presets.append('enterprise')
    
    # Professional gets most (exclude only very advanced)
    if not is_advanced_only(rule_id, name):
        presets.append('professional')
    
    # Standard gets balanced set
    if is_core_rule(rule_id, name, category):
        presets.append('standard')
    
    # Minimal gets one per category
    if is_minimal_essential(rule_id, name, category):
        presets.append('minimal')
    
    return presets


def is_minimal_essential(rule_id: str, name: str, category: str) -> bool:
    """Check if rule is minimal preset essential."""
    minimal_rules = {
        'DP-001', 'DP-012', 'DP-036',  # Dev principles: time, testing, security
        'WR-001', 'WR-002',            # Workflow: gates, required tasks
        'CQ-001', 'CQ-030',            # Code quality: naming, type safety
        'DOC-011', 'DOC-021',          # Docs: README, summaries
        'WF-001', 'WF-004',            # Git: commits, main protection
        'TC-001',                      # Tech: three-layer pattern
        'TEST-001', 'TEST-007',        # Testing: coverage, no flaky
        'OPS-001',                     # Ops: deployment automation
    }
    return rule_id in minimal_rules


def is_core_rule(rule_id: str, name: str, category: str) -> bool:
    """Check if rule is core for standard preset."""
    # All time-boxing
    if 'time-boxing' in name:
        return True
    
    # Core workflow (WR-001 to WR-010)
    if rule_id.startswith('WR-00'):
        return True
    
    # Essential dev principles
    if rule_id in ['DP-012', 'DP-030', 'DP-036', 'DP-046']:
        return True
    
    # Core code quality (CQ-001 to CQ-010)
    if rule_id.startswith('CQ-00') or rule_id.startswith('CQ-01'):
        return True
    
    # Essential docs
    if rule_id.startswith('DOC-00') or rule_id.startswith('DOC-01'):
        return True
    
    # Core testing
    if rule_id.startswith('TEST-00'):
        return True
    
    return False


def is_advanced_only(rule_id: str, name: str) -> bool:
    """Check if rule is enterprise-only."""
    # Governance rules (all advanced)
    if rule_id.startswith('GOV-'):
        return True
    
    # Advanced accessibility (keep basics)
    if rule_id.startswith('A11Y-') and int(rule_id.split('-')[1]) > 10:
        return True
    
    # Advanced ops (keep basics)
    if rule_id.startswith('OPS-') and int(rule_id.split('-')[1]) > 10:
        return True
    
    return False


def determine_enforcement(rule_id: str, name: str, category: str) -> str:
    """Determine enforcement level."""
    # BLOCK (hard constraints)
    block_keywords = ['time-boxing', 'required-tasks', 'quality-gates', 'no-hardcoded', 'test-coverage', 'no-main-commits']
    if any(kw in name for kw in block_keywords):
        return 'BLOCK'
    
    # LIMIT (soft constraints)
    limit_keywords = ['max-', 'min-', '-required', '-limit', 'review-sla']
    if any(kw in name for kw in limit_keywords):
        return 'LIMIT'
    
    # ENHANCE (context/guidance, no enforcement)
    enhance_keywords = ['pattern', 'style', 'approach', 'philosophy']
    if any(kw in name for kw in enhance_keywords):
        return 'ENHANCE'
    
    # GUIDE (suggestions)
    return 'GUIDE'


def extract_config(description: str, rationale: str) -> Dict[str, Any]:
    """Extract configuration from description."""
    config = {}
    
    # Extract hours
    hours_match = re.search(r'≤(\d+)h', description)
    if hours_match:
        config['max_hours'] = float(hours_match.group(1))
    
    # Extract coverage percentage
    coverage_match = re.search(r'(\d+)%', description)
    if coverage_match and 'coverage' in description.lower():
        config['min_coverage'] = float(coverage_match.group(1))
    
    # Extract line limits
    lines_match = re.search(r'≤(\d+) lines', description)
    if lines_match:
        config['max_lines'] = int(lines_match.group(1))
    
    # Extract complexity
    complexity_match = re.search(r'≤(\d+)', description)
    if complexity_match and 'complexity' in description.lower():
        config['max_complexity'] = int(complexity_match.group(1))
    
    return config


def generate_yaml_catalog(rules: List[Dict], output_path: Path):
    """Generate complete YAML catalog."""
    
    # Calculate preset counts
    preset_counts = {
        'minimal': sum(1 for r in rules if 'minimal' in r['presets']),
        'standard': sum(1 for r in rules if 'standard' in r['presets']),
        'professional': sum(1 for r in rules if 'professional' in r['presets']),
        'enterprise': len(rules)
    }
    
    catalog = {
        'version': '1.0.0',
        'last_updated': '2025-10-07',
        'total_rules': len(rules),
        
        'presets': {
            'minimal': {
                'name': 'Minimal',
                'description': 'Solo developer, prototype, learning AIPM - breadth over depth',
                'rule_count': preset_counts['minimal'],
                'philosophy': 'Touch every category lightly, don\'t overwhelm'
            },
            'standard': {
                'name': 'Standard',
                'description': 'Small team, MVP stage, startup - balanced coverage',
                'rule_count': preset_counts['standard'],
                'philosophy': '2-3 essential rules per category'
            },
            'professional': {
                'name': 'Professional',
                'description': 'Established team, production system - deep critical areas',
                'rule_count': preset_counts['professional'],
                'philosophy': 'Comprehensive security, testing, quality standards'
            },
            'enterprise': {
                'name': 'Enterprise',
                'description': 'Large organization, compliance-heavy - complete governance',
                'rule_count': preset_counts['enterprise'],
                'philosophy': 'All rules enabled, maximum governance'
            }
        },
        
        'rules': rules
    }
    
    # Write YAML
    with open(output_path, 'w') as f:
        yaml.safe_dump(catalog, f, default_flow_style=False, sort_keys=False, allow_unicode=True, width=120)
    
    print(f"✅ Generated {output_path}")
    print(f"   Total rules: {len(rules)}")
    print(f"   Minimal preset: {preset_counts['minimal']} rules")
    print(f"   Standard preset: {preset_counts['standard']} rules")
    print(f"   Professional preset: {preset_counts['professional']} rules")
    print(f"   Enterprise preset: {preset_counts['enterprise']} rules")


if __name__ == '__main__':
    ref_doc = Path("docs/components/rules/complete-rules-reference.md")
    output = Path("agentpm/core/rules/config/rules_catalog.yaml")
    
    print(f"📖 Parsing rules from {ref_doc}...")
    rules = parse_rules_from_markdown(ref_doc)
    
    print(f"📝 Generating YAML catalog to {output}...")
    generate_yaml_catalog(rules, output)
    
    print("\n✅ Rules catalog generated successfully!")
    
    # Show category breakdown
    by_category = {}
    for rule in rules:
        cat = rule['category']
        by_category[cat] = by_category.get(cat, 0) + 1
    
    print("\n📊 Rules by category:")
    for cat, count in sorted(by_category.items()):
        print(f"   {cat}: {count} rules")
