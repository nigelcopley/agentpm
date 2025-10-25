#!/usr/bin/env python3
"""
Update category names from initials to full names in rules catalog.
"""

import yaml
from pathlib import Path

# Mapping from initials to full names
CATEGORY_MAPPING = {
    'DP': 'Development Principles',
    'CQ': 'Code Quality',
    'DOC': 'Documentation Standards',
    'WR': 'Workflow Rules',
    'TEST': 'Testing Standards',
    'WF': 'Workflow & Process',
    'TC': 'Technology Constraints',
    'OPS': 'Operations Standards',
    'GOV': 'Governance'
}

def update_category_names(catalog_path: Path) -> None:
    """Update category names from initials to full names."""
    print(f"Loading catalog from {catalog_path}")
    
    with open(catalog_path) as f:
        catalog = yaml.safe_load(f)
    
    rules = catalog.get('rules', [])
    print(f"Processing {len(rules)} rules...")
    
    updated_count = 0
    for rule in rules:
        current_category = rule.get('category', '')
        if current_category in CATEGORY_MAPPING:
            new_category = CATEGORY_MAPPING[current_category]
            rule['category'] = new_category
            updated_count += 1
            print(f"  Updated {rule['rule_id']}: {current_category} → {new_category}")
    
    print(f"\nUpdated {updated_count} rules with full category names")
    
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
        update_category_names(catalog_path)
        print("\n✅ Successfully updated category names to full names")
        return 0
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    exit(main())
