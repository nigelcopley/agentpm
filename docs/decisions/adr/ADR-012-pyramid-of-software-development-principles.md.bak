# ADR-012: Pyramid of Software Development Principles

**Status**: Accepted  
**Date**: 2025-10-13  
**Deciders**: APM (Agent Project Manager) Development Team  
**Work Item**: Principles Documentation Enhancement

---

## Context

APM (Agent Project Manager) was using a simplified hierarchy of software development principles:
- **YAGNI > KISS > DRY > SOLID**

However, this approach had several limitations:

1. **Principle Conflicts**: When principles conflicted, there was no clear guidance on which to prioritize
2. **Missing Foundation**: No explicit "Make it work" principle as the foundation
3. **Missing Predictability**: No "Principle of Least Surprise" for AI agent predictability
4. **Incomplete Hierarchy**: Missing important principles like consistency, clean code, and performance optimization
5. **AI Agent Needs**: AI agents require predictable, consistent behavior that wasn't explicitly addressed

## Decision

**We will adopt [Bartosz Krajka's Pyramid of Software Development Principles](https://bartoszkrajka.com/2019/10/21/the-pyramid-of-software-development-principles/) as our hierarchical framework for software development decisions.**

### The Pyramid (Bottom to Top)

1. **Make it Work** - FOUNDATION
2. **YAGNI (You Aren't Gonna Need It)** - SECOND
3. **Principle of Least Surprise** - THIRD
4. **KISS (Keep It Simple, Stupid)** - FOURTH
5. **Be Consistent** - FIFTH
6. **DRY (Don't Repeat Yourself)** - SIXTH
7. **Clean Code** - SEVENTH
8. **SOLID** - EIGHTH
9. **Design Patterns** - NINTH
10. **Agile Practices** - TENTH
11. **Boy Scout Rule** - ELEVENTH
12. **Make it Fast** - TWELFTH

### Foundation Principle

**You shouldn't undermine lower layers at the expense of higher layers. When principles conflict, choose the one lower on the pyramid.**

## Rationale

### Why This Pyramid Works for APM (Agent Project Manager)

1. **AI Agent Enablement**: The "Principle of Least Surprise" is crucial for AI agents who need predictable behavior
2. **Practical Hierarchy**: Provides clear guidance when principles conflict
3. **Foundation First**: "Make it work" ensures functional correctness before optimization
4. **Comprehensive Coverage**: Includes all important principles in logical order
5. **Evidence-Based**: Based on real-world experience and practical software development

### Key Benefits

1. **Conflict Resolution**: Clear hierarchy for resolving principle conflicts
2. **AI Agent Predictability**: Explicit focus on predictable behavior
3. **Foundation Principle**: Working code is the foundation for all other principles
4. **Comprehensive**: Covers all aspects from functionality to performance
5. **Practical**: Based on real-world software development experience

### Specific Applications to APM (Agent Project Manager)

#### Context Assembly Service
- **Make it work**: Context must be assembled correctly
- **YAGNI**: Don't add unnecessary context fields
- **Least surprise**: Context structure should be predictable
- **KISS**: Simple assembly pipeline
- **Consistent**: Same structure across all contexts
- **DRY**: Reuse assembly components

#### Plugin Architecture
- **Make it work**: Plugins must detect frameworks correctly
- **YAGNI**: Don't add speculative plugin features
- **Least surprise**: Plugin interface should be predictable
- **KISS**: Simple plugin interface
- **Consistent**: All plugins follow same pattern

#### Web Interface
- **Make it work**: Routes must return correct responses
- **YAGNI**: Don't add unnecessary UI features
- **Least surprise**: Consistent API patterns
- **KISS**: Simple template structure
- **Consistent**: Same patterns across all routes

## Consequences

### Positive

1. **Clear Decision Framework**: Developers and AI agents have clear guidance when principles conflict
2. **AI Agent Enablement**: Explicit focus on predictable behavior for AI agents
3. **Comprehensive Coverage**: All important principles are included in logical hierarchy
4. **Foundation First**: Ensures functional correctness before optimization
5. **Practical Guidance**: Based on real-world software development experience

### Negative

1. **Learning Curve**: Team needs to understand the new hierarchy
2. **Documentation Updates**: Need to update all principle-related documentation
3. **Decision Overhead**: More complex decision-making process initially

### Neutral

1. **No Breaking Changes**: This is a decision-making framework, not a code change
2. **Gradual Adoption**: Can be adopted incrementally across the codebase

## Implementation

### Documentation Updates

1. **✅ Updated** `/docs/principles/README.md` with complete pyramid
2. **✅ Updated** `/docs/principles/frameworks.md` with quick reference
3. **✅ Created** this ADR documenting the decision

### Team Adoption

1. **Training**: Team members should read the [original article](https://bartoszkrajka.com/2019/10/21/the-pyramid-of-software-development-principles/)
2. **Practice**: Apply the pyramid in code reviews and design decisions
3. **Examples**: Use APM (Agent Project Manager) code examples to illustrate each principle

### AI Agent Integration

1. **Context Assembly**: Ensure predictable context structure
2. **Error Messages**: Make error messages predictable and actionable
3. **API Design**: Maintain consistent API patterns
4. **Code Generation**: Follow the pyramid when generating code

## Evidence

### External Reference
- **[The Pyramid of Software Development Principles](https://bartoszkrajka.com/2019/10/21/the-pyramid-of-software-development-principles/)** by Bartosz Krajka
- Addresses the exact problem we faced: principle conflicts in software development
- Provides practical, hierarchical approach to resolving conflicts
- Based on real-world software development experience

### Internal Evidence
- **Principle Conflicts**: We regularly face conflicts between YAGNI, KISS, DRY, and SOLID
- **AI Agent Needs**: AI agents require predictable behavior for effective operation
- **Missing Foundation**: No explicit "Make it work" principle in our current hierarchy
- **Incomplete Coverage**: Missing important principles like consistency and clean code

## Alternatives Considered

### 1. Keep Current Hierarchy (YAGNI > KISS > DRY > SOLID)
**Rejected**: Too simplistic, doesn't address conflicts, missing important principles

### 2. Create Custom Hierarchy
**Rejected**: Would require extensive research and validation, external evidence is stronger

### 3. No Hierarchy (All Principles Equal)
**Rejected**: Provides no guidance when principles conflict, which is common in practice

### 4. Different External Hierarchy
**Rejected**: Bartosz's pyramid is well-reasoned, practical, and addresses our specific needs

## Related Decisions

- **ADR-001**: Provider Abstraction Architecture
- **ADR-002**: Context Compression Strategy
- **ADR-003**: Sub-Agent Communication Protocol
- **ADR-004**: Evidence Storage and Retrieval

## Review

This ADR should be reviewed when:
1. **New principles** are identified that don't fit the pyramid
2. **AI agent behavior** becomes unpredictable
3. **Team feedback** indicates the hierarchy isn't working in practice
4. **External evidence** suggests a better approach

---

**Last Updated**: 2025-10-13  
**Version**: 1.0.0  
**Next Review**: 2025-11-13
