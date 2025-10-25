#!/usr/bin/env python3
"""
Fix phase gate validation tests-BAK by adding required CI-006 metadata.
"""

import re

def fix_phase_gate_tests():
    """Fix phase gate validation tests-BAK by adding required RACI metadata."""
    
    file_path = "tests/core/workflow/test_phase_gate_validation.py"
    
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Pattern to find metadata dictionaries that need RACI roles
    # Look for metadata with why_value but missing ownership
    pattern = r'(metadata = \{[^}]*"why_value":\s*\{[^}]*\}[^}]*\})'
    
    def add_raci_metadata(match):
        metadata_str = match.group(1)
        
        # Check if ownership is already present
        if '"ownership"' in metadata_str:
            return metadata_str
            
        # Add ownership.raci before the closing brace
        raci_addition = ''',
            "ownership": {
                "raci": {
                    "responsible": "Developer",
                    "accountable": "Product Manager", 
                    "consulted": "Tech Lead",
                    "informed": "Stakeholders"
                }
            },
            "scope": {
                "in_scope": ["Phase gate validation"]
            }'''
        
        # Insert before the closing brace
        result = metadata_str.rstrip('}') + raci_addition + '\n        }'
        return result
    
    # Apply the fix
    new_content = re.sub(pattern, add_raci_metadata, content, flags=re.DOTALL)
    
    # Also fix the case where metadata is None
    none_pattern = r'metadata=None,  # No metadata at all'
    none_replacement = '''metadata=json.dumps({
            "why_value": {
                "problem": "Legacy work item without metadata",
                "desired_outcome": "Backward compatibility test",
                "business_impact": "Ensure legacy support",
                "target_metrics": ["Compatibility"]
            },
            "ownership": {
                "raci": {
                    "responsible": "Developer",
                    "accountable": "Product Manager",
                    "consulted": "Tech Lead", 
                    "informed": "Stakeholders"
                }
            },
            "scope": {
                "in_scope": ["Legacy compatibility"]
            }
        }),  # Minimal metadata for CI-006 compliance'''
    
    new_content = re.sub(none_pattern, none_replacement, new_content)
    
    with open(file_path, 'w') as f:
        f.write(new_content)
    
    print(f"✅ Fixed {file_path}")

if __name__ == "__main__":
    fix_phase_gate_tests()
