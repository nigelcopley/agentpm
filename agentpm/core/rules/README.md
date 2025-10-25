# Rules Management System

Governance rules system with interactive questionnaire, intelligent preset selection, and YAML catalog management.

## Overview

The Rules Management System provides:
- **Interactive Questionnaire**: 18-question configuration during `apm init`
- **Intelligent Preset Selection**: 4 presets (minimal/standard/professional/enterprise)
- **YAML Catalog**: 245 governance rules with preset mappings
- **Database Persistence**: Rules stored for AI agent enforcement

## Architecture

```
QuestionnaireService (18 questions)
    ↓ answers
PresetSelector (3-axis scoring)
    ↓ preset name
RuleGenerationService (orchestrator)
    ↓ load request
DefaultRulesLoader (YAML catalog)
    ↓ Rule models
Database (rules table)
```

## Components

### 1. QuestionnaireService

Interactive CLI questionnaire for project configuration.

**Location**: `agentpm/core/rules/questionnaire.py`

**Usage**:

```python
from rich.console import Console
from agentpm.core.rules import QuestionnaireService

console = Console()
service = QuestionnaireService(console)

# Interactive mode
answers = service.run()

# Auto-defaults (--yes flag)
answers = service.run(use_defaults=True)

# Resume partial
partial = {"project_type": "api", "primary_language": "python"}
answers = service.run(resume_from=partial)
```

**Questions** (18 total):
1. **Q1-Q3**: Project basics (type, language, stage)
2. **Q4-Q6**: Tech stack (backend, frontend, database) - conditional
3. **Q7-Q9**: Development practices (coverage, review, time-boxing)
4. **Q10-Q12**: Process (approach, architecture, deployment)
5. **Q13-Q18**: 6W Context (team, purpose, users, timeline, constraints, rationale)

### 2. PresetSelector

Intelligent preset recommendation based on project characteristics.

**Location**: `agentpm/core/rules/preset_selector.py`

**Algorithm**:
```
Score = (Scale + Maturity + Governance) / 3

Scale (0-100): Team size (solo=0, enterprise=100)
Maturity (0-100): Dev stage (prototype=0, enterprise=100)  
Governance (0-100): Compliance detection (keywords → 100)

Mapping:
  <25: minimal (15 rules)
  25-54: standard (71 rules)
  55-79: professional (220 rules)
  80+: enterprise (245 rules)
```

**Usage**:

```python
from agentpm.core.rules import PresetSelector

selector = PresetSelector()

# Auto-select
answers = {"team_size": "small", "development_stage": "mvp"}
preset = selector.select(answers)  # → "standard"

# With explanation
reason = selector.get_recommendation_reason(answers)
print(reason)
# Output:
# Recommended: STANDARD
#   Scale: 25/100 (team size: small)
#   Maturity: 33/100 (stage: mvp)
#   Governance: 33/100
#   → Composite: 30/100
```

### 3. RuleGenerationService

Orchestrates preset selection and rule loading.

**Location**: `agentpm/core/rules/generator.py`

**Usage**:

```python
from agentpm.core.database.service import DatabaseService
from agentpm.core.rules import RuleGenerationService

db = DatabaseService("project.db")
generator = RuleGenerationService(db)

# From questionnaire answers
answers = questionnaire.run()
rules = generator.generate(answers, project_id=1)

# Explicit preset
rules = generator.generate_with_preset(project_id=1, preset="professional")

# Get recommendation
rec = generator.get_recommendation(answers)
print(f"Recommended: {rec['preset']} ({rec['rule_count']} rules)")
print(f"Reason: {rec['reason']}")
```

### 4. DefaultRulesLoader

Loads rules from YAML catalog or hardcoded defaults.

**Location**: `agentpm/core/rules/loader.py`

**Usage**:

```python
from agentpm.core.database.service import DatabaseService
from agentpm.core.rules import DefaultRulesLoader

db = DatabaseService("project.db")
loader = DefaultRulesLoader(db)

# Load from YAML catalog (recommended)
rules = loader.load_from_catalog(project_id=1, preset="standard")  # 71 rules

# Load hardcoded defaults (backward compatibility)
rules = loader.load_defaults(project_id=1)  # 25 rules

# Preset metadata
info = loader.get_preset_info("minimal")
print(f"{info['name']}: {info['rule_count']} rules")

# All presets
presets = loader.get_all_presets()
for name, info in presets.items():
    print(f"  {name}: {info['rule_count']} rules")
```

## YAML Catalog

**Location**: `agentpm/core/rules/config/rules_catalog.yaml`

**Structure**:
```yaml
version: "1.0.0"
total_rules: 245

presets:
  minimal: {rule_count: 15, ...}
  standard: {rule_count: 71, ...}
  professional: {rule_count: 220, ...}
  enterprise: {rule_count: 245, ...}

rules:
  - rule_id: DP-001
    name: time-boxing-implementation
    description: IMPLEMENTATION tasks ≤4h
    category: DP
    enforcement_level: BLOCK
    presets: [enterprise, professional, standard, minimal]
    config: {max_hours: 4.0}
    enabled_by_default: true
```

**Categories** (9 total):
- **DP**: Development Principles (55 rules)
- **WR**: Workflow Rules (35 rules)
- **CQ**: Code Quality (40 rules)
- **DOC**: Documentation (25 rules)
- **WF**: Workflow & Process (20 rules)
- **TC**: Technology Constraints (15 rules)
- **OPS**: Operations (20 rules)
- **GOV**: Governance (15 rules)
- **TEST**: Testing Requirements (20 rules)

## Preset Comparison

| Preset | Rules | Target User | Philosophy |
|--------|-------|-------------|------------|
| **Minimal** | 15 | Solo dev, prototype | Breadth over depth - one per category |
| **Standard** | 71 | Small team, MVP | Balanced - 2-3 per category |
| **Professional** | 220 | Production team | Deep security/testing/quality |
| **Enterprise** | 245 | Large org, compliance | Complete governance |

## Integration with `apm init`

**Flow**:

```python
# In apm init command
from agentpm.core.rules import QuestionnaireService, RuleGenerationService

# 1. Run questionnaire
console = Console()
q_service = QuestionnaireService(console)
answers = q_service.run(use_defaults=args.yes)

# 2. Generate rules
generator = RuleGenerationService(db)
rules = generator.generate(answers, project_id=project.id)

# 3. Rules now in database, ready for enforcement
console.print(f"✅ Loaded {len(rules)} governance rules")
```

## Testing

**Test Suite**: 87 tests across 6 files
- **test_rules.py**: Database layer (20 tests)
- **test_loader.py**: YAML catalog loading (21 tests)
- **test_preset_selector.py**: Scoring algorithm (19 tests)
- **test_generator.py**: Rule generation (14 tests)
- **test_questionnaire.py**: Questionnaire defaults (10 tests)
- **test_integration.py**: End-to-end flows (13 tests)

**Coverage**:
- rules.py methods: 100% ⭐
- generator.py: 100% ⭐
- preset_selector.py: 100% ⭐
- loader.py: 98% ⭐

**Run Tests**:
```bash
# All rules tests
pytest tests/core/rules/ tests/core/database/test_rules.py -v

# With coverage
pytest tests/core/rules/ --cov=agentpm/core/rules --cov-report=html
```

## Development

### Adding New Rules

1. **Edit Reference**: Update `docs/components/rules/complete-rules-reference.md`
2. **Regenerate Catalog**: Run `python scripts/generate_rules_catalog.py`
3. **Test**: Verify YAML validates and loads correctly

### Changing Preset Composition

Edit preset logic in `scripts/generate_rules_catalog.py`:
- `is_minimal_essential()`: Rules for minimal preset
- `is_core_rule()`: Rules for standard preset
- `is_advanced_only()`: Enterprise-only rules

### Adjusting Scoring Algorithm

Edit `agentpm/core/rules/preset_selector.py`:
- `_score_scale()`: Team size scoring
- `_score_maturity()`: Development stage scoring
- `_score_governance()`: Compliance detection
- `_score_to_preset()`: Threshold mapping

## API Reference

See inline docstrings in each module for detailed API documentation.

---

**Status**: Production-ready ✅  
**Test Coverage**: 95%+ on testable code  
**Total LOC**: ~1,700 (implementation + tests)  
**Work Item**: WI-0009 (Rules Management & Interactive Questionnaire)
