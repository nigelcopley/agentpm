# APM Branding Tests - Quick Reference

**Task**: #947 | **Status**: ✅ COMPLETE | **Tests**: 44/44 PASSING

---

## Quick Commands

```bash
# Run all branding tests
pytest tests/branding/ -v

# Run with coverage
pytest tests/branding/ --cov=agentpm/cli --cov-report=html

# Generate branding report
pytest tests/branding/test_apm_codebase_scan.py::TestBrandingMetrics::test_generate_branding_report -v -s

# Run specific test file
pytest tests/branding/test_apm_branding.py -v
```

---

## Test Files

| File | Tests | Purpose |
|------|-------|---------|
| `test_apm_branding.py` | 21 | Core CLI branding validation |
| `test_apm_codebase_scan.py` | 11 | Codebase scanning & metrics |
| `test_branding_fixtures.py` | 12 | Fixture-based validation |
| **Total** | **44** | **Complete branding suite** |

---

## Current Status

```
✅ Tests Passing: 44/44 (100%)
📊 Branding Score: 0/100 (13 AIPM references found)
🎯 Target Score: 90/100 (≤1 reference)
📈 Coverage: 36.52% (CLI-focused)
```

---

## Top 3 Issues to Fix

1. **Dashboard Title** (`status.py:105`)
   - Change: "APM (Agent Project Manager) Project Dashboard" → "APM Project Dashboard"

2. **Search Command** (`search.py`)
   - Change: "APM (Agent Project Manager) entities" → "APM entities"

3. **Skills Help** (`skills.py`)
   - Change: "APM (Agent Project Manager) Skills" → "APM Skills"

---

## Expected Branding

| Element | Value |
|---------|-------|
| Product Name | APM |
| Full Name | Agent Project Manager |
| CLI Command | `apm` |
| Domain | apm.run |
| Tagline | Multi-Agent Project Management for Your Terminal |

---

## Test Categories

- ✅ **CLI Branding** (6 tests) - Version, help, commands
- ✅ **Configuration** (2 tests) - prog_name, docstrings
- ✅ **Output** (1 test) - No APM (Agent Project Manager) in output
- ✅ **Documentation** (2 tests) - Help text consistency
- ✅ **Negative** (3 tests) - Find remaining AIPM refs
- ✅ **Consistency** (3 tests) - Emoji, tagline, commands
- ✅ **Edge Cases** (3 tests) - Errors, invalid commands
- 📊 **Scanning** (11 tests) - Codebase analysis
- ✅ **Fixtures** (12 tests) - Terminology validation

---

## File Structure

```
tests/branding/
├── __init__.py              # Module initialization
├── conftest.py              # Fixtures and markers
├── test_apm_branding.py     # Core CLI tests (21)
├── test_apm_codebase_scan.py # Scanning tests (11)
├── test_branding_fixtures.py # Fixture tests (12)
├── README.md                # Full documentation
└── QUICK-REFERENCE.md       # This file
```

---

## Next Steps

1. Fix top 3 user-facing issues
2. Re-run branding report
3. Track score improvement
4. Add to CI/CD pipeline

---

**Last Updated**: 2025-10-25
