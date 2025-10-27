# Jinja2 Template Architecture - Implementation Checklist

Comprehensive checklist for implementing the template architecture across all providers.

---

## Phase 1: Core Infrastructure (Week 1)

### 1.1 Context Models (2 days)

**File**: `agentpm/providers/base/context.py`

- [ ] Create `EnforcementLevel` enum
- [ ] Implement `RuleContext` model
  - [ ] Add validation for rule_id pattern (`^[A-Z]+-\d{3}$`)
  - [ ] Add enforcement level validation
  - [ ] Add priority range validation (0-100)
- [ ] Implement `AgentContext` model
  - [ ] Add validation for role pattern (`^[a-z0-9-]+$`)
  - [ ] Add tier validation (1, 2, or 3)
  - [ ] Add delegation relationship fields
- [ ] Implement `ProjectContext` model
  - [ ] Add path validation (must be absolute)
  - [ ] Add tech stack fields
- [ ] Implement `ProviderConfig` model
  - [ ] Add provider name pattern validation
  - [ ] Add version pattern validation
- [ ] Implement `TemplateContext` model
  - [ ] Add cross-field validation
  - [ ] Validate agent delegation relationships
  - [ ] Add JSON encoders for Path/datetime
- [ ] Implement `RenderResult` model
  - [ ] Add success/error tracking
  - [ ] Add warnings list
  - [ ] Add metadata dictionary
- [ ] Write unit tests for all models
  - [ ] Test validation errors
  - [ ] Test cross-field validation
  - [ ] Test JSON serialization

**Acceptance Criteria**:
- All models have complete Pydantic validation
- 100% test coverage on validation logic
- Documentation strings complete
- Type hints on all fields

---

### 1.2 Template Renderer (3 days)

**File**: `agentpm/providers/base/renderer.py`

- [ ] Implement `TemplateRenderer` class
  - [ ] Initialize Jinja2 environment
  - [ ] Configure auto-escaping
  - [ ] Set up strict undefined handling
  - [ ] Configure trim/lstrip settings
- [ ] Implement template loading
  - [ ] File system loader with multiple dirs
  - [ ] LRU cache for compiled templates
  - [ ] Template not found error handling
- [ ] Implement filter registration
  - [ ] Agent filters
  - [ ] Rule filters
  - [ ] Format filters
  - [ ] Security filters
- [ ] Implement test registration
  - [ ] `orchestrator` test (tier 3)
  - [ ] `specialist` test (tier 2)
  - [ ] `subagent` test (tier 1)
  - [ ] `blocking_rule` test
- [ ] Implement `render()` method
  - [ ] Context validation
  - [ ] Template compilation
  - [ ] Rendering execution
  - [ ] Output validation
  - [ ] Security checks
- [ ] Implement `render_string()` method
  - [ ] String template support
  - [ ] Error handling
- [ ] Implement validation helpers
  - [ ] `_validate_output()`
  - [ ] `_check_security()`
- [ ] Implement cache management
  - [ ] `clear_cache()` method
  - [ ] Cache hit/miss tracking
- [ ] Write comprehensive tests
  - [ ] Test basic rendering
  - [ ] Test filter application
  - [ ] Test macro usage
  - [ ] Test error handling
  - [ ] Test caching performance
  - [ ] Test security warnings

**Acceptance Criteria**:
- Renderer handles all error cases gracefully
- Caching provides 10x+ performance improvement
- Security warnings detect common patterns
- 95%+ test coverage

---

### 1.3 Custom Filters (2 days)

**Directory**: `agentpm/providers/templates/filters/`

#### Agent Filters (`agent_filters.py`)
- [ ] Implement `flatten_agents()`
  - [ ] Return comma-separated roles
  - [ ] Handle empty list
- [ ] Implement `filter_by_tier()`
  - [ ] Filter by tier level
  - [ ] Handle invalid tier
- [ ] Implement `group_by_type()`
  - [ ] Group by agent_type
  - [ ] Return dictionary
- [ ] Implement `sort_agents()`
  - [ ] Sort by any field
  - [ ] Support reverse order
- [ ] Write unit tests

#### Rule Filters (`rule_filters.py`)
- [ ] Implement `filter_rules()`
  - [ ] Filter by category
  - [ ] Filter by enforcement level
  - [ ] Support multiple filters
- [ ] Implement `group_rules()`
  - [ ] Group by category
  - [ ] Return dictionary
- [ ] Implement `format_rule()`
  - [ ] Markdown format
  - [ ] TOML format
  - [ ] JSON format
- [ ] Write unit tests

#### Format Filters (`format_filters.py`)
- [ ] Implement `to_toml()`
  - [ ] Use toml library if available
  - [ ] Fallback to key=value format
- [ ] Implement `to_json()`
  - [ ] Support indentation
  - [ ] Handle datetime/Path
- [ ] Implement `to_yaml()`
  - [ ] Use yaml library if available
  - [ ] Fallback to JSON
- [ ] Implement `markdown_table()`
  - [ ] Generate table headers
  - [ ] Format rows
  - [ ] Handle empty data
- [ ] Write unit tests

#### Security Filters (`escape_filters.py`)
- [ ] Implement `escape_shell()`
  - [ ] Use shlex.quote()
  - [ ] Handle all shell metacharacters
- [ ] Implement `escape_toml()`
  - [ ] Escape backslashes
  - [ ] Escape quotes
- [ ] Implement `sanitize_path()`
  - [ ] Remove .. and .
  - [ ] Prevent traversal attacks
- [ ] Implement `escape_markdown()`
  - [ ] Escape special characters
- [ ] Write security tests

**Acceptance Criteria**:
- All filters handle edge cases
- Security filters prevent common attacks
- 100% test coverage
- Performance benchmarks pass

---

### 1.4 Common Macros (2 days)

**Directory**: `agentpm/providers/templates/common/macros/`

#### Agent Macros (`agents.j2`)
- [ ] Implement `agent_header()` macro
  - [ ] Display name, role, tier
  - [ ] Status indicator
- [ ] Implement `agent_delegation()` macro
  - [ ] Reports to
  - [ ] Delegates to list
- [ ] Implement `agent_capabilities()` macro
  - [ ] Capability list
  - [ ] Handle empty
- [ ] Implement `agent_triggers()` macro
  - [ ] Activation triggers list
  - [ ] Default trigger
- [ ] Implement `agent_block()` macro
  - [ ] Complete agent section
  - [ ] Optional SOP inclusion
- [ ] Test all macros

#### Rule Macros (`rules.j2`)
- [ ] Implement `rule_block()` macro
  - [ ] Rule header
  - [ ] Description
  - [ ] Configuration JSON
- [ ] Implement `rules_by_category()` macro
  - [ ] Group rules
  - [ ] Category headers
- [ ] Implement `blocking_rules()` macro
  - [ ] Filter BLOCK rules
  - [ ] Priority order
- [ ] Implement `rules_table()` macro
  - [ ] Markdown table format
  - [ ] Configurable columns
- [ ] Test all macros

#### Formatting Macros (`formatting.j2`)
- [ ] Implement `metadata_section()` macro
  - [ ] Key-value pairs
  - [ ] Title customization
- [ ] Implement `code_block()` macro
  - [ ] Language syntax highlighting
  - [ ] Content formatting
- [ ] Implement `collapsible()` macro
  - [ ] Details/summary HTML
  - [ ] Open/closed state
- [ ] Implement `timestamp()` macro
  - [ ] ISO format
  - [ ] Human-readable format
- [ ] Test all macros

**Acceptance Criteria**:
- Macros produce consistent output
- Handle all edge cases
- Well-documented with examples
- Integration tests pass

---

## Phase 2: Provider Templates (Week 2)

### 2.1 Claude Code Templates (2 days)

**Directory**: `agentpm/providers/anthropic/templates/`

- [ ] Create `claude_md.j2` (main CLAUDE.md)
  - [ ] Extend base template
  - [ ] Import agent/rule macros
  - [ ] Agent sections by tier
  - [ ] Rules sections by category
  - [ ] Quick commands section
- [ ] Create `agent.j2` (individual agents)
  - [ ] YAML frontmatter
  - [ ] Agent block with SOP
  - [ ] Project rules section
  - [ ] Metadata footer
- [ ] Create `settings.j2` (.claude/settings.json)
  - [ ] JSON structure
  - [ ] Provider configuration
  - [ ] Feature flags
- [ ] Create hook templates
  - [ ] `pre_tool_use.j2`
  - [ ] `session_start.j2`
- [ ] Test all templates
  - [ ] Unit tests with sample context
  - [ ] Validate JSON syntax
  - [ ] Check markdown formatting

**Acceptance Criteria**:
- Templates generate valid Claude Code configs
- All macros work correctly
- Filters applied properly
- Output validated

---

### 2.2 Cursor Templates (2 days)

**Directory**: `agentpm/providers/cursor/templates/`

- [ ] Create `cursorrules.j2` (.cursorrules)
  - [ ] Project context section
  - [ ] Blocking rules prominent
  - [ ] Recommended practices
  - [ ] Agent roster
- [ ] Create `cursorignore.j2` (.cursorignore)
  - [ ] Standard ignore patterns
  - [ ] Project-specific patterns
- [ ] Create mode templates
  - [ ] `agent_mode.j2`
  - [ ] `composer_mode.j2`
- [ ] Create rule templates
  - [ ] `python_impl.mdc.j2`
  - [ ] `testing.mdc.j2`
  - [ ] `database.mdc.j2`
- [ ] Test all templates
  - [ ] Integration tests
  - [ ] Cursor compatibility check
  - [ ] Markdown format validation

**Acceptance Criteria**:
- Templates generate valid Cursor configs
- MDC format correct
- All rules render properly
- Agent information complete

---

### 2.3 OpenAI Codex Templates (2 days)

**Directory**: `agentpm/providers/openai/templates/`

- [ ] Create `agents_md.j2` (agents reference)
  - [ ] Agent list format
  - [ ] Capability descriptions
- [ ] Create `config.toml.j2` (main config)
  - [ ] Project section
  - [ ] Tech stack section
  - [ ] Agents array
  - [ ] Rules sections by category
  - [ ] Use escape_toml filter
- [ ] Test all templates
  - [ ] TOML syntax validation
  - [ ] Escaping verification
  - [ ] Integration tests

**Acceptance Criteria**:
- Templates generate valid TOML
- All values properly escaped
- No injection vulnerabilities
- Parse with TOML parser successfully

---

## Phase 3: Provider Integration (Week 3)

### 3.1 Base Provider Class (2 days)

**File**: `agentpm/providers/base/provider.py`

- [ ] Implement `BaseProvider` ABC
  - [ ] Abstract `install()` method
  - [ ] Abstract `uninstall()` method
  - [ ] Abstract `update()` method
  - [ ] Abstract `verify()` method
  - [ ] Abstract `render_configs()` method
- [ ] Implement `_load_project_context()`
  - [ ] Query database for project
  - [ ] Load agents
  - [ ] Load rules
  - [ ] Build TemplateContext
- [ ] Implement common utilities
  - [ ] File writing helper
  - [ ] Database recording helper
- [ ] Write tests
  - [ ] Test context loading
  - [ ] Test error handling
  - [ ] Mock database interactions

**Acceptance Criteria**:
- Base class provides solid foundation
- Context loading handles all cases
- Error handling comprehensive
- Tests cover all methods

---

### 3.2 Update CursorProvider (2 days)

**File**: `agentpm/providers/cursor/provider.py`

- [ ] Refactor to use TemplateRenderer
  - [ ] Remove old template code
  - [ ] Use `render_configs()`
  - [ ] Apply new context models
- [ ] Update `install()` method
  - [ ] Load context
  - [ ] Render all templates
  - [ ] Write files
  - [ ] Record installation
- [ ] Update `verify()` method
  - [ ] Check all expected files
  - [ ] Validate content
- [ ] Update tests
  - [ ] Test with new renderer
  - [ ] Verify all templates render
  - [ ] Check file outputs

**Acceptance Criteria**:
- CursorProvider fully migrated
- All existing functionality preserved
- New template system integrated
- Tests pass

---

### 3.3 Create ClaudeCodeProvider (2 days)

**File**: `agentpm/providers/anthropic/provider.py`

- [ ] Implement `ClaudeCodeProvider`
  - [ ] Extend `BaseProvider`
  - [ ] Set template directory
  - [ ] Initialize renderer
- [ ] Implement `install()` method
  - [ ] Create .claude directory
  - [ ] Render CLAUDE.md
  - [ ] Render agent files
  - [ ] Render settings.json
  - [ ] Render hooks
- [ ] Implement `render_configs()` method
  - [ ] Map templates to outputs
  - [ ] Handle errors
- [ ] Implement other methods
  - [ ] `uninstall()`
  - [ ] `update()`
  - [ ] `verify()`
- [ ] Write comprehensive tests
  - [ ] Test installation
  - [ ] Test rendering
  - [ ] Test verification
  - [ ] Integration tests

**Acceptance Criteria**:
- Provider fully functional
- All Claude Code files generated correctly
- Hooks work properly
- Tests comprehensive

---

### 3.4 Create CodexProvider (2 days)

**File**: `agentpm/providers/openai/provider.py`

- [ ] Implement `CodexProvider`
  - [ ] Extend `BaseProvider`
  - [ ] Set template directory
  - [ ] Initialize renderer
- [ ] Implement `install()` method
  - [ ] Render config.toml
  - [ ] Render agents.md
  - [ ] Write files
- [ ] Implement `render_configs()` method
  - [ ] TOML rendering
  - [ ] Markdown rendering
- [ ] Implement other methods
  - [ ] `uninstall()`
  - [ ] `update()`
  - [ ] `verify()`
- [ ] Write tests
  - [ ] TOML validation
  - [ ] Integration tests

**Acceptance Criteria**:
- Provider fully functional
- TOML syntax valid
- All escaping correct
- Tests comprehensive

---

## Phase 4: Testing & Documentation (Week 4)

### 4.1 Unit Tests (2 days)

- [ ] Filter tests
  - [ ] `test_agent_filters.py`
  - [ ] `test_rule_filters.py`
  - [ ] `test_format_filters.py`
  - [ ] `test_escape_filters.py`
- [ ] Context model tests
  - [ ] `test_context_models.py`
  - [ ] Test all validations
  - [ ] Test edge cases
- [ ] Renderer tests
  - [ ] `test_renderer.py`
  - [ ] Test caching
  - [ ] Test error handling
  - [ ] Test security checks
- [ ] Achieve 95%+ coverage

**Acceptance Criteria**:
- All unit tests pass
- Coverage >95%
- Tests run fast (<30s total)
- No flaky tests

---

### 4.2 Integration Tests (2 days)

- [ ] Template rendering tests
  - [ ] `test_template_rendering.py`
  - [ ] Test all providers
  - [ ] Test macro usage
  - [ ] Test filter chains
- [ ] Provider tests
  - [ ] `test_cursor_provider.py`
  - [ ] `test_claude_provider.py`
  - [ ] `test_codex_provider.py`
  - [ ] Test full lifecycle
- [ ] End-to-end tests
  - [ ] `test_e2e_installation.py`
  - [ ] Real database
  - [ ] Real file system
  - [ ] Verify outputs

**Acceptance Criteria**:
- All integration tests pass
- Real-world scenarios covered
- Performance acceptable
- No race conditions

---

### 4.3 Documentation (2 days)

- [ ] Update architecture docs
  - [ ] Link to template design
  - [ ] Update provider docs
- [ ] Create user guide
  - [ ] How to use templates
  - [ ] How to add providers
  - [ ] How to customize
- [ ] Create API reference
  - [ ] Context models
  - [ ] Renderer API
  - [ ] Filter reference
  - [ ] Macro reference
- [ ] Add code examples
  - [ ] Example contexts
  - [ ] Example templates
  - [ ] Example providers
- [ ] Update CHANGELOG

**Acceptance Criteria**:
- Documentation complete
- Examples work
- API reference accurate
- User guide helpful

---

### 4.4 Performance Testing (1 day)

- [ ] Benchmark template rendering
  - [ ] First render time
  - [ ] Cached render time
  - [ ] Memory usage
- [ ] Benchmark context building
  - [ ] Database query time
  - [ ] Validation time
- [ ] Optimize hot paths
  - [ ] Cache effectiveness
  - [ ] Filter performance
- [ ] Document results

**Acceptance Criteria**:
- Rendering <100ms (cached)
- Context building <200ms
- Memory usage reasonable
- No performance regressions

---

## Phase 5: Deployment (Week 5)

### 5.1 CLI Integration (2 days)

- [ ] Update `apm provider install` command
  - [ ] Use new providers
  - [ ] Show progress
  - [ ] Handle errors gracefully
- [ ] Update `apm provider verify` command
  - [ ] Use new verification
  - [ ] Detailed output
- [ ] Update `apm provider update` command
  - [ ] Re-render templates
  - [ ] Preserve custom changes (warning)
- [ ] Add `apm provider test` command
  - [ ] Test template rendering
  - [ ] Validate outputs
- [ ] Update CLI tests

**Acceptance Criteria**:
- CLI commands work seamlessly
- Error messages helpful
- Progress indicators clear
- Tests pass

---

### 5.2 Database Migrations (1 day)

- [ ] Create migration for provider metadata
  - [ ] Template version tracking
  - [ ] Render timestamps
- [ ] Update provider_installations table
  - [ ] Add template_version column
  - [ ] Add last_rendered column
- [ ] Migrate existing data
  - [ ] Backfill versions
- [ ] Test migrations
  - [ ] Upgrade/downgrade
  - [ ] Data integrity

**Acceptance Criteria**:
- Migrations run cleanly
- No data loss
- Rollback works
- Tests pass

---

### 5.3 Release Preparation (2 days)

- [ ] Update version numbers
  - [ ] pyproject.toml
  - [ ] Provider versions
- [ ] Update CHANGELOG
  - [ ] New features
  - [ ] Breaking changes
  - [ ] Migration guide
- [ ] Run full test suite
  - [ ] All tests pass
  - [ ] Coverage >95%
- [ ] Build documentation
  - [ ] Generate API docs
  - [ ] Build user guide
- [ ] Create release branch
  - [ ] Tag version
  - [ ] Push to remote

**Acceptance Criteria**:
- All tests pass
- Documentation built
- Version tagged
- Ready for release

---

## Verification Checklist

### Code Quality
- [ ] All code follows style guide (Black, Ruff)
- [ ] Type hints on all functions
- [ ] Docstrings on all public APIs
- [ ] No linter warnings
- [ ] No security vulnerabilities

### Testing
- [ ] Unit test coverage >95%
- [ ] Integration tests pass
- [ ] E2E tests pass
- [ ] Performance benchmarks acceptable
- [ ] No flaky tests

### Documentation
- [ ] Architecture docs complete
- [ ] User guide written
- [ ] API reference accurate
- [ ] Examples work
- [ ] CHANGELOG updated

### Security
- [ ] No hardcoded secrets
- [ ] Escaping functions tested
- [ ] Injection attacks prevented
- [ ] Security warnings functional

### Performance
- [ ] Template rendering <100ms (cached)
- [ ] Context building <200ms
- [ ] Memory usage reasonable
- [ ] Caching effective

---

## Risk Mitigation

### Risk 1: Performance Regression
**Mitigation**:
- Benchmark before/after
- Use caching extensively
- Profile hot paths
- Optimize incrementally

### Risk 2: Breaking Changes
**Mitigation**:
- Maintain backward compatibility
- Provide migration guide
- Deprecate gradually
- Test existing providers

### Risk 3: Security Vulnerabilities
**Mitigation**:
- Security reviews
- Escape all outputs
- Validate all inputs
- Automated security tests

### Risk 4: Complex Template Debugging
**Mitigation**:
- Detailed error messages
- Template linting
- Example templates
- Debugging guide

---

## Success Metrics

- [ ] All 3 providers using template architecture
- [ ] Template rendering <100ms (cached)
- [ ] Test coverage >95%
- [ ] Zero security vulnerabilities
- [ ] Documentation complete
- [ ] User feedback positive
- [ ] Performance improved vs old system
- [ ] Code complexity reduced

---

**Version**: 1.0.0
**Last Updated**: 2025-10-27
**Estimated Completion**: 5 weeks
**Team Size**: 1-2 developers
