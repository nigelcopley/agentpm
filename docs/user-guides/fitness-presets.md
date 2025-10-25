# Fitness Test Presets - User Guide

## Overview

Fitness test presets allow you to quickly apply predefined policy configurations tailored for different use cases and quality standards.

## Available Presets

### 1. strict - Strict Quality Standards
**Best for**: Enterprise applications, production systems, high-stakes projects

**Quality Standards**:
- Maximum complexity: 5 (very strict)
- Maximum file size: 250 lines
- Minimum maintainability: 75
- Circular dependencies: Not allowed
- Policies enabled: ALL (11 policies)

**Use when**:
- Building mission-critical systems
- Maintaining high-quality codebases
- Enterprise compliance required
- Long-term maintainability is priority

```bash
apm detect fitness --preset strict
```

---

### 2. balanced - Balanced Standards (DEFAULT)
**Best for**: Most projects, general development, new projects

**Quality Standards**:
- Maximum complexity: 10 (moderate)
- Maximum file size: 500 lines
- Minimum maintainability: 65
- Circular dependencies: Not allowed
- Policies enabled: 7 core policies

**Use when**:
- Starting new projects
- General application development
- Team has mixed experience levels
- Balancing quality with velocity

```bash
apm detect fitness --preset balanced
# or simply:
apm detect fitness
```

---

### 3. lenient - Lenient Standards
**Best for**: Legacy codebases, rapid prototyping, POCs

**Quality Standards**:
- Maximum complexity: 20 (relaxed)
- Maximum file size: 1000 lines
- Minimum maintainability: 40
- Circular dependencies: Allowed
- Policies enabled: 2 essential policies only

**Use when**:
- Working with legacy code
- Rapid prototyping phase
- Proof of concepts
- Gradually improving code quality

```bash
apm detect fitness --preset lenient
```

---

### 4. startup - Startup Velocity
**Best for**: Early-stage startups, MVPs, fast iteration

**Quality Standards**:
- Maximum complexity: 15
- Maximum file size: 750 lines
- Minimum maintainability: 50
- Circular dependencies: Allowed
- Policies enabled: 3 policies

**Use when**:
- Building MVPs quickly
- Fast iteration is critical
- Testing market fit
- Early-stage development

```bash
apm detect fitness --preset startup
```

---

### 5. security_focused - Security Focused
**Best for**: Security-critical applications, compliance-heavy projects

**Quality Standards**:
- Maximum complexity: 8 (reduces attack surface)
- Maximum file size: 400 lines
- Minimum maintainability: 70
- Circular dependencies: Not allowed
- Policies enabled: 4 security-relevant policies

**Use when**:
- Building security-critical systems
- Compliance requirements (SOC2, HIPAA, etc.)
- Financial applications
- Authentication/authorization systems

```bash
apm detect fitness --preset security_focused
```

---

## Quick Reference

| Preset | Max Complexity | Max File LOC | Min Maintainability | Circular Deps | Policies |
|--------|----------------|--------------|---------------------|---------------|----------|
| strict | 5 | 250 | 75 | ❌ | 11 |
| balanced | 10 | 500 | 65 | ❌ | 7 |
| lenient | 20 | 1000 | 40 | ✅ | 2 |
| startup | 15 | 750 | 50 | ✅ | 3 |
| security_focused | 8 | 400 | 70 | ❌ | 4 |

## Usage Examples

### List Available Presets
```bash
apm detect fitness --list-presets
```

### Run with Specific Preset
```bash
# Use strict quality standards
apm detect fitness --preset strict

# Use lenient standards for legacy code
apm detect fitness --preset lenient

# Security-focused testing
apm detect fitness --preset security_focused
```

### Combine with Other Options
```bash
# Run strict preset and fail on errors (CI/CD)
apm detect fitness --preset strict --fail-on-error

# Run balanced preset and show only errors
apm detect fitness --preset balanced --errors-only

# Run startup preset with suggestions
apm detect fitness --preset startup --show-suggestions

# Export results to JSON
apm detect fitness --preset strict --format json --output results.json
```

## Choosing the Right Preset

### Decision Tree

```
Are you building a security-critical system?
├─ YES → Use "security_focused"
└─ NO
   │
   Is this a legacy codebase or POC?
   ├─ YES → Use "lenient"
   └─ NO
      │
      Is this an early-stage startup/MVP?
      ├─ YES → Use "startup"
      └─ NO
         │
         Is this an enterprise/production system?
         ├─ YES → Use "strict"
         └─ NO → Use "balanced" (default)
```

### By Project Phase

| Phase | Recommended Preset | Rationale |
|-------|-------------------|-----------|
| POC/Prototype | lenient or startup | Speed over quality |
| MVP Development | startup or balanced | Balance speed and quality |
| Active Development | balanced | Standard quality gates |
| Pre-Production | strict | Ensure production readiness |
| Production | strict or security_focused | Maximum quality/security |
| Legacy Maintenance | lenient → balanced | Gradual improvement |

## CI/CD Integration

### GitHub Actions Example
```yaml
- name: Run Fitness Tests
  run: apm detect fitness --preset strict --fail-on-error --format json --output fitness-report.json
```

### GitLab CI Example
```yaml
fitness_tests:
  script:
    - apm detect fitness --preset strict --fail-on-error
  artifacts:
    reports:
      codequality: fitness-report.json
```

### Pre-commit Hook Example
```bash
#!/bin/bash
# .git/hooks/pre-commit

# Run fitness tests with balanced preset
apm detect fitness --preset balanced --errors-only

if [ $? -ne 0 ]; then
    echo "Fitness tests failed. Use --preset lenient if needed."
    exit 1
fi
```

## Customizing Presets

While built-in presets cannot be modified, you can:

1. **Clone and customize** (future feature):
   ```bash
   apm preset clone strict my-strict --max-complexity 7
   ```

2. **Create custom presets** (future feature):
   ```bash
   apm preset create my-preset --max-complexity 8 --max-file-loc 400
   ```

3. **Override individual policies** (future feature):
   ```bash
   apm detect fitness --preset strict --disable NO_LAYERING_VIOLATIONS
   ```

## Migration Guide

### From No Preset → With Preset

**Before**:
```bash
apm detect fitness
```

**After** (explicit preset):
```bash
apm detect fitness --preset balanced  # Same as before
apm detect fitness --preset strict    # Stricter quality standards
```

### Gradual Quality Improvement

Start with lenient, move to balanced, then strict:

```bash
# Week 1-4: Assess current state
apm detect fitness --preset lenient

# Week 5-8: Fix critical issues, move to balanced
apm detect fitness --preset balanced

# Week 9+: Aim for strict quality
apm detect fitness --preset strict
```

## FAQ

**Q: Which preset should I use for a new project?**
A: Start with `balanced` for general projects, or `startup` if speed is critical.

**Q: Can I modify built-in presets?**
A: No, but you can create custom presets (future feature).

**Q: What happens if I don't specify a preset?**
A: The default policies are used (similar to `balanced`).

**Q: Can I use presets in CI/CD?**
A: Yes! Use `--preset strict --fail-on-error` for quality gates.

**Q: How do I know which policies are enabled in a preset?**
A: Run `apm detect fitness --list-presets` for details.

**Q: Can I gradually improve code quality?**
A: Yes! Start with `lenient`, fix issues, move to `balanced`, then `strict`.

## Additional Resources

- [Fitness Testing Guide](./fitness-testing.md)
- [Policy Reference](../reference/fitness-policies.md)
- [CLI Reference](../reference/cli-commands.md)

---

**Version**: 1.0.0
**Last Updated**: 2025-10-24
