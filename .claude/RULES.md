# APM (Agent Project Manager) Governance Rules

**Active Rules**: 75
**Categories**: 5
**Generated**: 2025-10-21 11:12:29

---

## Rule Categories

### Code Quality

**Rules in category**: 19

#### LIMIT Level (2 rules)

**CQ-009**: naming-max-length

Names ≤50 characters

---

**CQ-014**: file-max-imports

Max 20 imports per file

---

#### GUIDE Level (17 rules)

**CQ-001**: naming-convention

Language-specific naming (snake_case, camelCase)

---

**CQ-002**: naming-descriptive

Names describe purpose

---

**CQ-003**: naming-no-abbreviations

Avoid cryptic abbreviations

---

**CQ-004**: naming-boolean-prefix

Booleans: is_/has_/can_

---

**CQ-005**: naming-class-nouns

Classes are nouns

---

**CQ-006**: naming-function-verbs

Functions are verbs

---

**CQ-007**: naming-constants-upper

Constants in UPPER_SNAKE_CASE

---

**CQ-008**: naming-private-underscore

Private methods start with _

---

**CQ-010**: naming-no-single-letter

No single-letter names (except i, j, k in loops)

---

**CQ-011**: file-one-class-per-file

One class per file (Java/TS style)

---

**CQ-012**: file-module-init

Proper __init__.py exports (Python)

---

**CQ-013**: file-test-colocation

Tests in tests-BAK/ directory

---

**CQ-015**: file-no-circular-imports

No circular imports

---

**CQ-016**: file-explicit-exports

Explicit __all__ in modules

---

**CQ-017**: file-directory-structure

Domain-based directories (not by type)

---

**CQ-018**: file-config-separate

Config in dedicated files

---

**CQ-019**: file-no-unused-imports

Remove unused imports

---

### Development Principles

**Rules in category**: 14

#### BLOCK Level (12 rules)

**DP-001**: time-boxing-implementation

IMPLEMENTATION tasks ≤4h

---

**DP-002**: time-boxing-testing

TESTING tasks ≤6h

---

**DP-003**: time-boxing-design

DESIGN tasks ≤8h

---

**DP-004**: time-boxing-documentation

DOCUMENTATION tasks ≤4h

---

**DP-005**: time-boxing-deployment

DEPLOYMENT tasks ≤2h

---

**DP-006**: time-boxing-analysis

ANALYSIS tasks ≤8h

---

**DP-007**: time-boxing-research

RESEARCH tasks ≤12h

---

**DP-008**: time-boxing-refactoring

REFACTORING tasks ≤6h

---

**DP-009**: time-boxing-bugfix

BUGFIX tasks ≤4h

---

**DP-010**: time-boxing-hotfix

HOTFIX tasks ≤2h

---

**DP-011**: time-boxing-planning

PLANNING tasks ≤8h

---

**DP-036**: security-no-hardcoded-secrets

No secrets in code

---

#### GUIDE Level (2 rules)

**DP-030**: code-no-dict-str-any

No Dict[str, Any] in public APIs

---

**DP-046**: perf-api-response-time

API responses <200ms (p95)

---

### Documentation Standards

**Rules in category**: 19

#### LIMIT Level (1 rules)

**DOC-011**: doc-readme-required

README.md at project root

---

#### GUIDE Level (16 rules)

**DOC-001**: doc-module-docstring

Every module has docstring

---

**DOC-002**: doc-class-docstring

Every public class has docstring

---

**DOC-003**: doc-function-docstring

Every public function has docstring

---

**DOC-004**: doc-parameter-description

Document all parameters

---

**DOC-005**: doc-return-description

Document return values

---

**DOC-006**: doc-exception-documentation

Document raised exceptions

---

**DOC-007**: doc-example-in-docstring

Include usage examples

---

**DOC-010**: doc-complexity-explanation

Complex code needs explanation

---

**DOC-012**: doc-setup-instructions

Setup instructions in README

---

**DOC-013**: doc-api-documentation

API endpoints documented

---

**DOC-014**: doc-architecture-overview

Architecture documented

---

**DOC-015**: doc-changelog-maintained

CHANGELOG.md updated

---

**DOC-016**: doc-contributing-guide

CONTRIBUTING.md for open source

---

**DOC-017**: doc-decision-records

ADRs for significant decisions

---

**DOC-018**: doc-deployment-guide

Deployment instructions

---

**DOC-019**: doc-troubleshooting

Common issues documented

---

#### ENHANCE Level (2 rules)

**DOC-008**: doc-google-style

Use Google-style docstrings (Python)

---

**DOC-009**: doc-jsdoc-style

Use JSDoc (JavaScript/TypeScript)

---

### Testing Standards

**Rules in category**: 14

#### BLOCK Level (4 rules)

**TEST-021**: test-critical-paths-coverage

Critical paths coverage requirement

---

**TEST-022**: test-user-facing-coverage

User-facing code coverage requirement

---

**TEST-023**: test-data-layer-coverage

Data layer coverage requirement

---

**TEST-024**: test-security-coverage

Security code coverage requirement

---

#### LIMIT Level (2 rules)

**TEST-002**: test-unit-required

Unit tests-BAK for all logic

---

**TEST-003**: test-integration-required

Integration tests-BAK for APIs

---

#### GUIDE Level (8 rules)

**TEST-004**: test-e2e-critical-paths

E2E for critical user flows

---

**TEST-005**: test-fast-suite

Test suite <5min

---

**TEST-006**: test-parallel-execution

Tests run in parallel

---

**TEST-007**: test-no-flaky-tests

No flaky tests-BAK allowed

---

**TEST-008**: test-seed-data

Use fixtures/factories for test data

---

**TEST-009**: test-teardown-cleanup

Tests clean up after themselves

---

**TEST-025**: test-utilities-coverage

Utilities code coverage requirement

---

**TEST-026**: test-framework-integration-coverage

Framework integration coverage requirement

---

### Workflow Rules

**Rules in category**: 9

#### BLOCK Level (5 rules)

**WR-001**: workflow-quality-gates

Work items validated before tasks start

---

**WR-002**: required-tasks-feature

FEATURE needs DESIGN+IMPL+TEST+DOC

---

**WR-003**: required-tasks-bugfix

BUGFIX needs ANALYSIS+FIX+TEST

---

**WR-008**: required-tasks-refactoring

REFACTORING needs ANALYSIS+IMPL+TEST

---

**WR-009**: required-tasks-research

RESEARCH needs ANALYSIS+DOC

---

#### LIMIT Level (1 rules)

**WR-007**: workflow-deployment-required

Deployment tasks for releases

---

#### GUIDE Level (2 rules)

**WR-004**: workflow-code-review

Code review required

---

**WR-006**: workflow-test-first

Tests before implementation (TDD)

---

#### ENHANCE Level (1 rules)

**WR-005**: workflow-development-approach

Documents TDD/BDD/DDD

---

