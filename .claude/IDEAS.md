# APM (Agent Project Manager) Ideas System

**Total Ideas**: 50
**Generated**: 2025-10-21 11:08:26

---

## Ideas Pipeline

APM (Agent Project Manager) uses a lightweight ideas system for capturing brainstorming:

1. **idea**: Initial capture
2. **research**: Investigation phase
3. **design**: Technical design
4. **accepted**: Ready for conversion
5. **converted**: Converted to work item
6. **rejected**: Not pursued

---

## Ideas by Status

### CONVERTED (3)

**Idea #44**: Implement idea next command to simplify idea workflow transitions

- **Votes**: 0
- **Source**: IdeaSource.USER
- **Description**: ## Problem
Current idea workflow has multiple states with manual transitions:
idea → research → desi...
- **Converted to**: WI-82

**Idea #43**: Simplify Workflow: Implement work-item next command to reduce complexity

- **Votes**: 0
- **Source**: IdeaSource.USER
- **Description**: ## Problem
Current workflow has 9 states with complex transitions:
PROPOSED → VALIDATED → ACCEPTED →...
- **Converted to**: WI-80

**Idea #42**: Issue: Test Suite Failures - 265 failed tests, 84 errors

- **Votes**: 0
- **Source**: IdeaSource.USER
- **Description**: ## Issue Analysis Complete

**Root Cause Identified**: The test is highlighting real issues with the...
- **Converted to**: WI-81

### DESIGN (1)

**Idea #46**: Migration System Refactoring - Eliminate schema.py Duplication

- **Votes**: 1
- **Source**: IdeaSource.USER
- **Description**: **Current Problem**: schema.py (871 lines) duplicates what migration_0018 does, with hardcoded CHECK...

### IDEA (44)

**Idea #45**: Test Suite Optimization - Reduce 43% Waste While Maintaining Coverage

- **Votes**: 1
- **Source**: IdeaSource.USER
- **Description**: **Analysis**: Comprehensive test suite analysis identified 43% over-engineering (1,926 tests → 1,100...

**Idea #41**: Standardize Plugin Glob Operations with IgnorePatternMatcher

- **Votes**: 1
- **Source**: IdeaSource.USER
- **Description**: **Problem**: 11/16 plugins use raw glob() without ignore filtering, causing false positives from tes...

**Idea #50**: Test idea from Claude integration

- **Votes**: 0
- **Source**: IdeaSource.USER

**Idea #49**: MCP: APM Orchestrator to retrofit subagent capability into any LLM client

- **Votes**: 0
- **Source**: IdeaSource.AI_SUGGESTION
- **Description**: ## Purpose
Create an MCP-based 'APM Orchestrator' that chains tools and role-specialised agent calls...

**Idea #48**: Issue: CLI 'skills' import error prevents help listing

- **Votes**: 0
- **Source**: IdeaSource.USER

**Idea #39**: Fix DatabaseService test fixture pattern across all test files

- **Votes**: 0
- **Source**: IdeaSource.USER

**Idea #38**: Test Mock Object Attribute Mismatch

- **Votes**: 0
- **Source**: IdeaSource.AI_SUGGESTION
- **Description**: Tests in test_sop_injector.py were failing because mock agent objects were setting sop_file_path att...

**Idea #37**: Temporal Context DateTime Conversion Issue

- **Votes**: 0
- **Source**: IdeaSource.AI_SUGGESTION
- **Description**: The temporal loader was failing because it was trying to call .isoformat() on session_date values th...

**Idea #36**: Test Database Schema Issues - Missing Migration Tables

- **Votes**: 0
- **Source**: IdeaSource.AI_SUGGESTION
- **Description**: Tests were failing because temporary test databases weren't applying all necessary migrations. The t...

**Idea #35**: Quick Win: Token Estimation Utilities

- **Votes**: 0
- **Source**: IdeaSource.AI_SUGGESTION
- **Description**: Implement immediate token estimation utilities based on Zen's patterns. Add simple character-to-toke...

### RESEARCH (2)

**Idea #47**: Provider Integration: Full Cursor support

- **Votes**: 0
- **Source**: IdeaSource.AI_SUGGESTION
- **Description**: Investigate and implement full provider integration with Cursor editor, including auth, API usage, s...

**Idea #40**: Analysis: WI-65 Comprehensive Review

- **Votes**: 0
- **Source**: IdeaSource.USER

---

## Top Voted Ideas

- **Migration System Refactoring - Eliminate schema.py Duplication** (1 votes) - IdeaStatus.DESIGN
- **Test Suite Optimization - Reduce 43% Waste While Maintaining Coverage** (1 votes) - IdeaStatus.IDEA
- **Standardize Plugin Glob Operations with IgnorePatternMatcher** (1 votes) - IdeaStatus.IDEA
- **Test idea from Claude integration** (0 votes) - IdeaStatus.IDEA
- **MCP: APM Orchestrator to retrofit subagent capability into any LLM client** (0 votes) - IdeaStatus.IDEA
