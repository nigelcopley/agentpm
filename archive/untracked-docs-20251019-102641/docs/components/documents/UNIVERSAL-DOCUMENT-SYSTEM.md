# Universal Document System - Project-Agnostic Design

**Date**: 2025-01-27  
**Status**: Final Design - Universal Document Organization  
**Context**: Project-agnostic document system for any type of project

---

## 🎯 **Core Principle: Universal Project-Agnostic Design**

The document system must work for **any type of project**:
- Web applications
- Mobile apps
- Desktop software
- APIs and microservices
- Data science projects
- Infrastructure projects
- Documentation projects
- Research projects
- Any other project type

**No project-specific assumptions** about systems, components, or technologies.

---

## 🏗️ **Universal Document Structure**

### **Top-Level Categories (4 Universal Categories)**

```
docs/
├── planning/           # Project planning and analysis
├── architecture/       # System design and technical specifications
├── guides/            # User and developer documentation
└── reference/         # API docs, troubleshooting, runbooks
```

### **Universal Subdirectories**

#### **Planning** (`docs/planning/`)
```
planning/
├── requirements/      # Functional and non-functional requirements
├── user-stories/      # User stories and use cases
├── analysis/          # Market research, competitive analysis
├── specifications/    # Technical specifications
├── ideas/             # Initial concepts and brainstorming
└── research/          # Research findings and investigations
```

#### **Architecture** (`docs/architecture/`)
```
architecture/
├── design/            # System design documents
├── patterns/          # Design patterns and best practices
├── integration/       # Integration plans and strategies
├── migration/         # Migration plans and guides
├── refactoring/       # Refactoring plans and guides
└── decisions/         # Architecture Decision Records (ADRs)
```

#### **Guides** (`docs/guides/`)
```
guides/
├── user/              # End-user documentation
├── developer/         # Developer documentation
├── admin/             # Administrator guides
├── getting-started/   # Quick start guides
├── tutorials/         # Step-by-step tutorials
└── troubleshooting/   # Problem resolution guides
```

#### **Reference** (`docs/reference/`)
```
reference/
├── api/               # API documentation
├── runbooks/          # Operational runbooks
├── test-plans/        # Test plans and strategies
├── deployment/        # Deployment procedures
└── other/             # Miscellaneous reference docs
```

---

## 🎯 **Universal Document Types**

### **Simplified Document Types (12 Core Types)**

```python
class DocumentType(str, Enum):
    # Planning category
    REQUIREMENTS = "requirements"           # → docs/planning/requirements/
    USER_STORY = "user_story"              # → docs/planning/user-stories/
    ANALYSIS = "analysis"                   # → docs/planning/analysis/
    SPECIFICATION = "specification"         # → docs/planning/specifications/
    IDEA = "idea"                          # → docs/planning/ideas/
    RESEARCH = "research"                   # → docs/planning/research/
    
    # Architecture category
    DESIGN = "design"                      # → docs/architecture/design/
    PATTERN = "pattern"                     # → docs/architecture/patterns/
    INTEGRATION = "integration"            # → docs/architecture/integration/
    MIGRATION = "migration"                # → docs/architecture/migration/
    REFACTORING = "refactoring"            # → docs/architecture/refactoring/
    ADR = "adr"                           # → docs/architecture/decisions/
    
    # Guides category
    USER_GUIDE = "user_guide"              # → docs/guides/user/
    DEVELOPER_GUIDE = "developer_guide"    # → docs/guides/developer/
    ADMIN_GUIDE = "admin_guide"            # → docs/guides/admin/
    GETTING_STARTED = "getting_started"    # → docs/guides/getting-started/
    TUTORIAL = "tutorial"                  # → docs/guides/tutorials/
    TROUBLESHOOTING = "troubleshooting"    # → docs/guides/troubleshooting/
    
    # Reference category
    API_DOC = "api_doc"                    # → docs/reference/api/
    RUNBOOK = "runbook"                    # → docs/reference/runbooks/
    TEST_PLAN = "test_plan"                # → docs/reference/test-plans/
    DEPLOYMENT = "deployment"              # → docs/reference/deployment/
    OTHER = "other"                        # → docs/reference/other/
```

---

## 🚀 **Universal Placement Rules**

### **Type-Based Placement (No System Dependencies)**

```python
def get_document_path(document_type: DocumentType, title: str) -> str:
    """Generate document path based on type only (no system dependencies)."""
    
    # Universal type-to-directory mapping
    type_mapping = {
        # Planning category
        DocumentType.REQUIREMENTS: "planning/requirements",
        DocumentType.USER_STORY: "planning/user-stories",
        DocumentType.ANALYSIS: "planning/analysis",
        DocumentType.SPECIFICATION: "planning/specifications",
        DocumentType.IDEA: "planning/ideas",
        DocumentType.RESEARCH: "planning/research",
        
        # Architecture category
        DocumentType.DESIGN: "architecture/design",
        DocumentType.PATTERN: "architecture/patterns",
        DocumentType.INTEGRATION: "architecture/integration",
        DocumentType.MIGRATION: "architecture/migration",
        DocumentType.REFACTORING: "architecture/refactoring",
        DocumentType.ADR: "architecture/decisions",
        
        # Guides category
        DocumentType.USER_GUIDE: "guides/user",
        DocumentType.DEVELOPER_GUIDE: "guides/developer",
        DocumentType.ADMIN_GUIDE: "guides/admin",
        DocumentType.GETTING_STARTED: "guides/getting-started",
        DocumentType.TUTORIAL: "guides/tutorials",
        DocumentType.TROUBLESHOOTING: "guides/troubleshooting",
        
        # Reference category
        DocumentType.API_DOC: "reference/api",
        DocumentType.RUNBOOK: "reference/runbooks",
        DocumentType.TEST_PLAN: "reference/test-plans",
        DocumentType.DEPLOYMENT: "reference/deployment",
        DocumentType.OTHER: "reference/other",
    }
    
    directory = type_mapping.get(document_type, "reference/other")
    filename = _slugify(title) + ".md"
    return f"docs/{directory}/{filename}"

def _slugify(title: str) -> str:
    """Convert title to URL-safe filename."""
    import re
    slug = re.sub(r'[^\w\s-]', '', title.lower())
    slug = re.sub(r'[-\s]+', '-', slug)
    return slug.strip('-')
```

---

## 🏗️ **Universal Database Schema**

### **Document Reference Model (Project-Agnostic)**

```python
class DocumentReference(BaseModel):
    # Existing fields
    id: Optional[int] = None
    entity_type: EntityType
    entity_id: int
    file_path: str
    document_type: DocumentType
    title: Optional[str]
    description: Optional[str]
    file_size_bytes: Optional[int]
    content_hash: Optional[str]
    format: Optional[DocumentFormat]
    created_by: Optional[str]
    created_at: datetime
    updated_at: datetime
    
    # Universal fields (no project-specific assumptions)
    category: str  # planning, architecture, guides, reference
    tags: Optional[List[str]] = None  # JSON array for flexible categorization
    status: DocumentStatus = DocumentStatus.ACTIVE
    
    # Optional metadata (can be used by any project)
    component: Optional[str] = None  # Generic component name (e.g., "auth", "database", "api")
    phase: Optional[str] = None  # Generic phase (e.g., "discovery", "implementation", "deployment")
    priority: Optional[str] = None  # Generic priority (e.g., "high", "medium", "low")
    
    class Config:
        validate_assignment = True
        json_schema_extra = {
            "example": {
                "entity_type": "task",
                "entity_id": 240,
                "file_path": "docs/architecture/design/authentication-system-design.md",
                "document_type": "design",
                "title": "Authentication System Design",
                "description": "Design document for user authentication system",
                "category": "architecture",
                "component": "auth",
                "phase": "planning",
                "tags": ["security", "authentication", "user-management"],
                "format": "markdown",
                "created_by": "system-architect"
            }
        }
```

### **Universal Database Migration**

```sql
-- Add universal fields (no project-specific assumptions)
ALTER TABLE document_references ADD COLUMN category TEXT NOT NULL;
ALTER TABLE document_references ADD COLUMN tags TEXT;  -- JSON array
ALTER TABLE document_references ADD COLUMN status TEXT DEFAULT 'active';

-- Optional metadata fields (can be used by any project)
ALTER TABLE document_references ADD COLUMN component TEXT;
ALTER TABLE document_references ADD COLUMN phase TEXT;
ALTER TABLE document_references ADD COLUMN priority TEXT;

-- Create indexes for performance
CREATE INDEX idx_document_references_category ON document_references(category);
CREATE INDEX idx_document_references_component ON document_references(component);
CREATE INDEX idx_document_references_phase ON document_references(phase);
CREATE INDEX idx_document_references_category_component ON document_references(category, component);
```

---

## 🎯 **Universal Quality Gates**

### **CI-007: Universal Document Placement**

```python
class UniversalDocumentValidator:
    def validate(self, document: DocumentReference) -> ValidationResult:
        """Validate document is in correct location based on type."""
        
        expected_path = get_document_path(document.document_type, document.title or "untitled")
        
        if document.file_path != expected_path:
            return ValidationResult(
                valid=False,
                error=f"Document should be at {expected_path}, not {document.file_path}",
                guidance=f"Move document to: {expected_path}"
            )
        
        return ValidationResult(valid=True)
```

### **CI-008: Universal Document Completeness**

```python
class UniversalDocumentCompletenessValidator:
    def validate(self, document: DocumentReference) -> ValidationResult:
        """Validate document has required fields for its type."""
        
        required_fields = {
            DocumentType.REQUIREMENTS: ['title', 'description'],
            DocumentType.DESIGN: ['title', 'description'],
            DocumentType.USER_GUIDE: ['title'],
            DocumentType.API_DOC: ['title', 'description'],
            DocumentType.ADR: ['title', 'description'],
        }
        
        required = required_fields.get(document.document_type, ['title'])
        missing = [field for field in required if not getattr(document, field)]
        
        if missing:
            return ValidationResult(
                valid=False,
                error=f"Missing required fields for {document.document_type}: {', '.join(missing)}"
            )
        
        return ValidationResult(valid=True)
```

---

## 🤖 **Universal Agent Guidance**

### **Smart Document Creation (Project-Agnostic)**

```python
class UniversalDocumentGuidance:
    def suggest_document_placement(self, document_type: DocumentType, title: str) -> str:
        """Suggest correct document placement for any project type."""
        return get_document_path(document_type, title)
    
    def get_category_appropriate_document_types(self, category: str) -> List[DocumentType]:
        """Get document types appropriate for a specific category."""
        
        category_document_types = {
            "planning": [
                DocumentType.REQUIREMENTS,
                DocumentType.USER_STORY,
                DocumentType.ANALYSIS,
                DocumentType.SPECIFICATION,
                DocumentType.IDEA,
                DocumentType.RESEARCH,
            ],
            "architecture": [
                DocumentType.DESIGN,
                DocumentType.PATTERN,
                DocumentType.INTEGRATION,
                DocumentType.MIGRATION,
                DocumentType.REFACTORING,
                DocumentType.ADR,
            ],
            "guides": [
                DocumentType.USER_GUIDE,
                DocumentType.DEVELOPER_GUIDE,
                DocumentType.ADMIN_GUIDE,
                DocumentType.GETTING_STARTED,
                DocumentType.TUTORIAL,
                DocumentType.TROUBLESHOOTING,
            ],
            "reference": [
                DocumentType.API_DOC,
                DocumentType.RUNBOOK,
                DocumentType.TEST_PLAN,
                DocumentType.DEPLOYMENT,
                DocumentType.OTHER,
            ],
        }
        
        return category_document_types.get(category, [])
    
    def suggest_metadata(self, document_type: DocumentType, content: str) -> Dict[str, Any]:
        """Suggest optional metadata based on document content."""
        suggestions = {}
        
        # Suggest component based on content analysis
        if "auth" in content.lower():
            suggestions["component"] = "auth"
        elif "database" in content.lower():
            suggestions["component"] = "database"
        elif "api" in content.lower():
            suggestions["component"] = "api"
        
        # Suggest tags based on content
        tags = []
        if "security" in content.lower():
            tags.append("security")
        if "performance" in content.lower():
            tags.append("performance")
        if "testing" in content.lower():
            tags.append("testing")
        
        if tags:
            suggestions["tags"] = tags
        
        return suggestions
```

---

## 📊 **Universal Benefits**

### **1. Project-Agnostic Design**
- **No Assumptions**: Works for web apps, mobile apps, APIs, data science, infrastructure
- **Universal Categories**: Planning, architecture, guides, reference apply to any project
- **Flexible Metadata**: Optional component, phase, priority fields for any project

### **2. Simple and Predictable**
- **4 Top-Level Categories**: Easy to understand and navigate
- **Type-Based Placement**: Document type determines location automatically
- **No Complex Rules**: Simple, consistent placement rules

### **3. Flexible Categorization**
- **Tags**: Flexible tagging for complex categorization needs
- **Optional Metadata**: Component, phase, priority for project-specific needs
- **Rich Queries**: Database queries for complex filtering

### **4. Industry Standard**
- **Common Patterns**: Follows industry conventions for documentation
- **Familiar Structure**: Developers know where to find documents
- **Scalable**: Easy to extend for specific project needs

---

## 🚀 **Universal CLI Commands**

### **Project-Agnostic Document Management**

```bash
# Create document (works for any project type)
apm document create --type=requirements --title="User Authentication Requirements"
# → Creates: docs/planning/requirements/user-authentication-requirements.md

apm document create --type=design --title="Authentication System Design"
# → Creates: docs/architecture/design/authentication-system-design.md

apm document create --type=api_doc --title="Authentication API Reference"
# → Creates: docs/reference/api/authentication-api-reference.md

# Category-based document listing
apm document list --category=planning
apm document list --category=architecture
apm document list --category=guides
apm document list --category=reference

# Type-based document listing
apm document list --type=requirements
apm document list --type=design
apm document list --type=api_doc

# Flexible metadata queries
apm document list --component=auth
apm document list --phase=planning
apm document list --tags=security

# Smart search
apm document search "authentication"
apm document search "API" --category=reference
apm document search "security" --tags=security
```

---

## 🎯 **Universal Implementation Strategy**

### **Phase 1: Database Schema Enhancement (Week 1, Days 1-2)**
1. **Add universal fields**: `category`, `tags`, `status`, `component`, `phase`, `priority`
2. **Update DocumentType enum**: Simplify to 12 universal types
3. **Create universal placement rules**: Type → directory mapping

### **Phase 2: Directory Structure Creation (Week 1, Days 3-4)**
1. **Create universal directories**: planning/, architecture/, guides/, reference/
2. **Create subdirectories**: Type-specific subdirectories
3. **Migrate existing documents**: Move to universal structure

### **Phase 3: Quality Gates Integration (Week 1, Days 5-7)**
1. **CI-007**: Universal document placement validation
2. **CI-008**: Universal document completeness validation
3. **Enhanced CLI commands**: Universal document management

### **Phase 4: Agent Integration (Week 2)**
1. **Universal guidance**: Suggest document placement for any project type
2. **Metadata suggestions**: Suggest optional metadata based on content
3. **Quality assurance**: Monitor compliance with universal structure

---

## 🎯 **Universal Success Metrics**

### **Quantitative Metrics**
- **Document Placement Accuracy**: >95% of documents in correct universal location
- **Agent Compliance**: >90% of agents use universal document placement
- **Discoverability**: <10 seconds to find any document by type
- **Project Compatibility**: Works for 100% of project types

### **Qualitative Metrics**
- **Universal Applicability**: Works for any project type
- **Simple Navigation**: Easy to understand and navigate
- **Flexible Categorization**: Tags and metadata for complex needs
- **Industry Standard**: Follows common documentation patterns

---

## 🎯 **Conclusion**

The **Universal Document System** provides:

- **Project-Agnostic Design**: Works for any type of project
- **Simple Structure**: 4 universal categories with type-based placement
- **Flexible Metadata**: Optional component, phase, priority, tags for any project
- **Industry Standard**: Follows common documentation patterns
- **Quality Gates**: Universal validation and agent guidance

**Key Innovation**: Use universal document types and categories that work for any project type, with optional metadata fields for project-specific needs.

This approach creates a **truly universal document system** that serves any project type while maintaining simplicity and predictability.

---

**Version**: 1.0  
**Last Updated**: 2025-01-27  
**Status**: Final Design - Universal Document System  
**Next Step**: Begin Phase 1 - Database Schema Enhancement with Universal Fields
