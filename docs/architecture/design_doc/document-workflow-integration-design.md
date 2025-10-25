# Document Workflow Integration Design

**Work Item**: #78 - Document Workflow Integration & AI Hooks  
**Task**: #468 - Design Document Workflow Integration  
**Status**: In Progress  
**Agent**: aipm-workflow-analyzer  

## Overview

This design integrates document management into the APM (Agent Project Manager) workflow validation system and creates AI agent hooks for automatic document recording. The integration ensures documents are properly tracked in work item and task validation, and AI agents can automatically record documents they create using the write tool.

## Architecture Components

### 1. Workflow Validation Integration

#### 1.1 Document Requirements in Quality Gates

**CI-007: Document Requirements** (New Quality Gate)
- **Requirement**: Required documents must be present before work item/task completion
- **Enforcement**: Block transitions to REVIEW/COMPLETED if required documents missing
- **Validator**: `DocumentRequirementsValidator`

**Document Requirements by Work Item Type:**
- **FEATURE**: Requires DESIGN + IMPLEMENTATION + TESTING + DOCUMENTATION tasks
  - Each task type has specific document requirements:
    - **DESIGN**: Architecture document, design specification
    - **IMPLEMENTATION**: Code documentation, API docs
    - **TESTING**: Test plan, test results
    - **DOCUMENTATION**: User guide, admin guide
- **ENHANCEMENT**: Requires DESIGN + IMPLEMENTATION + TESTING tasks
  - Similar document requirements as FEATURE
- **BUGFIX**: Requires ANALYSIS + BUGFIX + TESTING tasks
  - **ANALYSIS**: Root cause analysis document
  - **BUGFIX**: Fix documentation, changelog
  - **TESTING**: Test plan, regression test results
- **RESEARCH**: Requires RESEARCH + ANALYSIS + DOCUMENTATION tasks
  - **RESEARCH**: Research findings document
  - **ANALYSIS**: Analysis report
  - **DOCUMENTATION**: Research summary, recommendations

#### 1.2 Document Validation Rules

**Required Document Types by Task Type:**
```python
TASK_DOCUMENT_REQUIREMENTS = {
    TaskType.DESIGN: [
        DocumentType.ARCHITECTURE,
        DocumentType.DESIGN
    ],
    TaskType.IMPLEMENTATION: [
        DocumentType.API_DOC,
        DocumentType.TECHNICAL_SPECIFICATION
    ],
    TaskType.TESTING: [
        DocumentType.TEST_PLAN,
        DocumentType.TROUBLESHOOTING
    ],
    TaskType.DOCUMENTATION: [
        DocumentType.USER_GUIDE,
        DocumentType.ADMIN_GUIDE
    ],
    TaskType.ANALYSIS: [
        DocumentType.REQUIREMENTS,
        DocumentType.ANALYSIS
    ],
    TaskType.RESEARCH: [
        DocumentType.RESEARCH,
        DocumentType.ANALYSIS
    ]
}
```

**Validation Logic:**
1. Check if task has required document types
2. Validate document files exist and are accessible
3. Check document quality (size > 0, not empty)
4. Verify document is linked to correct entity

#### 1.3 Integration Points

**WorkflowService Integration:**
- Extend `_pre_validate_transition()` to include document validation
- Add `DocumentRequirementsValidator` to validation chain
- Update `ValidationResult` to include document-specific errors

**StateRequirements Integration:**
- Add document validation to state transition requirements
- Integrate with existing CI-001 through CI-006 gates
- Provide clear error messages and remediation guidance

### 2. AI Agent Document Hooks

#### 2.1 Post-Tool-Use Hook Enhancement

**Enhanced `post-tool-use.py` Hook:**
- Detect when AI agent uses `write` tool
- Automatically create document reference in database
- Link document to current work item/task context
- Extract document metadata (type, format, size)

**Hook Logic:**
```python
def handle_write_tool_usage(tool_call):
    """Handle write tool usage and create document reference"""
    if tool_call.tool_name == "write":
        # Extract file path and content
        file_path = tool_call.arguments.get("file_path")
        content = tool_call.arguments.get("contents")
        
        # Get current context (work item/task)
        current_context = get_current_work_context()
        
        # Create document reference
        document = DocumentReference(
            entity_type=current_context.entity_type,
            entity_id=current_context.entity_id,
            file_path=file_path,
            document_type=detect_document_type(file_path),
            title=generate_title_from_path(file_path),
            format=detect_format(file_path),
            created_by="ai_agent",
            file_size_bytes=len(content.encode('utf-8'))
        )
        
        # Save to database
        create_document_reference(db_service, document)
        
        # Provide feedback to agent
        print(f"📄 Document recorded: {file_path}")
```

#### 2.2 Document Detection and Classification

**Automatic Document Type Detection:**
- **Architecture**: `arch/`, `architecture/`, `system-design/`
- **Design**: `design/`, `designs/`, `mockup/`, `wireframe/`
- **API Docs**: `api/`, `api-docs/`, `swagger/`, `openapi/`
- **User Guide**: `user-guide/`, `manual/`, `tutorial/`
- **Test Plan**: `test-plan/`, `testing/`, `qa/`
- **Requirements**: `requirements/`, `reqs/`, `specs/`
- **Research**: `research/`, `analysis/`, `findings/`

**Format Detection:**
- **Markdown**: `.md`, `.markdown`
- **HTML**: `.html`, `.htm`
- **PDF**: `.pdf`
- **Text**: `.txt`
- **JSON**: `.json`
- **YAML**: `.yaml`, `.yml`

#### 2.3 Context-Aware Document Linking

**Current Context Detection:**
- Extract work item/task ID from session context
- Use active work item/task from database
- Fallback to project-level documents if no active context

**Entity Linking:**
- Link to current work item if in work item context
- Link to current task if in task context
- Link to project if in project context
- Link to idea if in idea context

### 3. Quality Gate Enforcement

#### 3.1 Document Quality Validation

**File Existence Validation:**
- Check if document file exists on filesystem
- Validate file is readable and accessible
- Check file size > 0 bytes

**Content Quality Validation:**
- Check for placeholder text (TODO, TBD, FIXME)
- Validate minimum content length
- Check for proper formatting

**Metadata Validation:**
- Ensure document has title
- Validate document type is appropriate
- Check format matches file extension

#### 3.2 Workflow Integration

**State Transition Validation:**
- **VALIDATED → ACCEPTED**: Check required documents exist
- **ACCEPTED → IN_PROGRESS**: Validate document requirements met
- **IN_PROGRESS → REVIEW**: Check all required documents present
- **REVIEW → COMPLETED**: Validate document quality and completeness

**Error Messages and Remediation:**
```python
class DocumentValidationError(ValidationError):
    def __init__(self, missing_docs, entity_type, entity_id):
        self.missing_docs = missing_docs
        self.entity_type = entity_type
        self.entity_id = entity_id
        
    def get_remediation_commands(self):
        commands = []
        for doc_type in self.missing_docs:
            commands.append(
                f"apm document add --entity-type={self.entity_type} "
                f"--entity-id={self.entity_id} --type={doc_type.value}"
            )
        return commands
```

### 4. Implementation Plan

#### 4.1 Phase 1: Core Integration (Task #469)
1. **Extend WorkflowService**
   - Add document validation to `_pre_validate_transition()`
   - Create `DocumentRequirementsValidator` class
   - Update validation result handling

2. **Create Document Validation Rules**
   - Implement `TASK_DOCUMENT_REQUIREMENTS` mapping
   - Create document existence and quality checks
   - Add document metadata validation

3. **Update State Requirements**
   - Integrate document validation with existing CI gates
   - Add document-specific error messages
   - Provide remediation guidance

#### 4.2 Phase 2: AI Agent Hooks (Task #470)
1. **Enhance Post-Tool-Use Hook**
   - Add write tool detection logic
   - Implement automatic document recording
   - Create context-aware entity linking

2. **Document Detection System**
   - Implement automatic document type detection
   - Create format detection logic
   - Add title generation from file paths

3. **Context Integration**
   - Extract current work context from session
   - Implement entity linking logic
   - Add fallback mechanisms

#### 4.3 Phase 3: Testing and Documentation (Tasks #471, #472)
1. **Comprehensive Testing**
   - Unit tests for document validation
   - Integration tests for workflow enforcement
   - Hook testing for AI agent integration

2. **Documentation**
   - User guide for document workflow integration
   - Developer guide for extending document validation
   - Hook documentation for AI agent integration

### 5. Technical Specifications

#### 5.1 Database Schema Extensions

**No schema changes required** - existing `document_references` table supports all requirements.

#### 5.2 API Extensions

**New Validation Methods:**
```python
class DocumentRequirementsValidator:
    def validate_document_requirements(self, entity_type, entity_id, task_type) -> ValidationResult
    def check_required_documents(self, entity_type, entity_id, required_types) -> List[DocumentReference]
    def validate_document_quality(self, document) -> ValidationResult
```

**Enhanced Hook Interface:**
```python
def handle_tool_usage(tool_call: ToolCall, context: WorkContext) -> None:
    """Enhanced hook interface for tool usage handling"""
    if tool_call.tool_name == "write":
        record_document_creation(tool_call, context)
```

#### 5.3 Configuration

**Document Requirements Configuration:**
```yaml
# agentpm/config/document_requirements.yaml
task_document_requirements:
  design:
    required_types: [architecture, design]
    optional_types: [specification]
  implementation:
    required_types: [api_doc, technical_specification]
    optional_types: [user_guide]
  testing:
    required_types: [test_plan]
    optional_types: [troubleshooting]
  documentation:
    required_types: [user_guide, admin_guide]
    optional_types: [api_doc]
```

### 6. Success Metrics

#### 6.1 Functional Metrics
- **Document Coverage**: 100% of required documents tracked
- **AI Agent Integration**: 100% of write tool usage recorded
- **Validation Accuracy**: 95% accurate document type detection
- **Workflow Compliance**: 100% adherence to document requirements

#### 6.2 Quality Metrics
- **Error Reduction**: 90% reduction in missing document issues
- **Workflow Efficiency**: 50% faster document task completion
- **Agent Productivity**: 75% reduction in manual document tracking

#### 6.3 User Experience Metrics
- **Automation Rate**: 95% of documents automatically recorded
- **Error Clarity**: 100% actionable error messages
- **Remediation Success**: 90% successful remediation on first attempt

### 7. Risk Mitigation

#### 7.1 Technical Risks
- **Performance Impact**: Document validation adds ~50ms to transitions
  - *Mitigation*: Cache document existence checks, async validation
- **Hook Reliability**: AI agent hooks may fail silently
  - *Mitigation*: Comprehensive error handling, fallback mechanisms
- **Context Detection**: May incorrectly link documents
  - *Mitigation*: Multiple context detection strategies, manual override

#### 7.2 User Experience Risks
- **Validation Overhead**: Too many document requirements
  - *Mitigation*: Configurable requirements, optional vs required
- **AI Agent Confusion**: Hooks may interfere with agent workflow
  - *Mitigation*: Silent operation, clear feedback, opt-out mechanism

### 8. Future Enhancements

#### 8.1 Advanced Features
- **Document Templates**: Auto-generate document templates
- **Content Validation**: AI-powered content quality assessment
- **Document Relationships**: Link related documents
- **Version Control**: Track document versions and changes

#### 8.2 Integration Opportunities
- **Git Integration**: Auto-detect document changes
- **CI/CD Integration**: Validate documents in build pipeline
- **External Tools**: Integrate with documentation platforms
- **Analytics**: Document usage and quality metrics

## Conclusion

This design provides comprehensive document workflow integration that:
1. **Enforces document requirements** through quality gates
2. **Automatically records documents** created by AI agents
3. **Validates document quality** and completeness
4. **Provides clear guidance** for remediation
5. **Maintains workflow efficiency** with minimal overhead

The implementation follows APM (Agent Project Manager) patterns and integrates seamlessly with existing workflow validation and hook systems.
