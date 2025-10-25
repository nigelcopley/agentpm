# Document Segmentation Strategy - Handling Multiple Types Within Categories

**Date**: 2025-01-27  
**Status**: Segmentation Strategy - Practical Implementation  
**Context**: How to handle multiple document types within the same category

---

## 🎯 **The Segmentation Problem**

### **Real-World Scenarios**

**Requirements Category:**
```
docs/planning/requirements/
├── functional-requirements.md
├── non-functional-requirements.md
├── security-requirements.md
├── performance-requirements.md
├── user-requirements.md
├── system-requirements.md
└── business-requirements.md
```

**Workflows Category:**
```
docs/processes/workflows/
├── user-onboarding-workflow.md
├── deployment-workflow.md
├── code-review-workflow.md
├── incident-response-workflow.md
├── feature-request-workflow.md
└── bug-triage-workflow.md
```

**Architecture Category:**
```
docs/architecture/design/
├── system-architecture.md
├── database-design.md
├── api-design.md
├── security-architecture.md
├── performance-architecture.md
└── scalability-design.md
```

---

## 🚀 **Segmentation Strategies**

### **Strategy 1: Subcategory-Based Segmentation**

Create subcategories within each main category:

```
docs/
├── planning/
│   ├── requirements/
│   │   ├── functional/          # Functional requirements
│   │   ├── non-functional/      # Non-functional requirements
│   │   ├── security/            # Security requirements
│   │   ├── performance/         # Performance requirements
│   │   └── business/            # Business requirements
│   ├── analysis/
│   │   ├── market-research/     # Market research
│   │   ├── competitive/         # Competitive analysis
│   │   ├── feasibility/         # Feasibility studies
│   │   └── stakeholder/         # Stakeholder analysis
│   └── specifications/
│       ├── technical/           # Technical specifications
│       ├── functional/          # Functional specifications
│       └── interface/           # Interface specifications
├── processes/
│   ├── workflows/
│   │   ├── business/            # Business workflows
│   │   ├── technical/           # Technical workflows
│   │   ├── deployment/          # Deployment workflows
│   │   └── incident-response/   # Incident response workflows
│   └── procedures/
│       ├── development/         # Development procedures
│       ├── testing/             # Testing procedures
│       ├── deployment/          # Deployment procedures
│       └── maintenance/         # Maintenance procedures
└── architecture/
    ├── design/
    │   ├── system/              # System design
    │   ├── database/            # Database design
    │   ├── api/                 # API design
    │   ├── security/            # Security design
    │   └── performance/         # Performance design
    └── patterns/
        ├── design-patterns/     # Design patterns
        ├── architectural-patterns/ # Architectural patterns
        └── anti-patterns/       # Anti-patterns
```

### **Strategy 2: Metadata-Driven Segmentation**

Use metadata fields to segment within flat directories:

```
docs/
├── planning/requirements/       # Flat directory
│   ├── user-authentication-requirements.md
│   ├── payment-processing-requirements.md
│   ├── reporting-requirements.md
│   └── security-requirements.md
├── processes/workflows/         # Flat directory
│   ├── user-onboarding-workflow.md
│   ├── deployment-workflow.md
│   └── incident-response-workflow.md
└── architecture/design/         # Flat directory
    ├── system-architecture.md
    ├── database-design.md
    └── api-design.md
```

**Database Metadata:**
```python
# Requirements segmentation
{
    "document_type": "requirements",
    "category": "planning",
    "subcategory": "functional",  # functional, non-functional, security, performance, business
    "component": "auth",          # auth, payment, reporting, etc.
    "tags": ["security", "authentication", "user-management"]
}

# Workflow segmentation
{
    "document_type": "workflow",
    "category": "processes",
    "subcategory": "business",    # business, technical, deployment, incident-response
    "component": "onboarding",    # onboarding, deployment, code-review, etc.
    "tags": ["user-management", "automation"]
}
```

### **Strategy 3: Hybrid Approach (Recommended)**

Combine subcategories for major segments with metadata for fine-grained segmentation:

```
docs/
├── planning/
│   ├── requirements/
│   │   ├── functional/          # Major segment: functional requirements
│   │   ├── non-functional/      # Major segment: non-functional requirements
│   │   └── security/            # Major segment: security requirements
│   └── analysis/
│       ├── market-research/     # Major segment: market research
│       ├── competitive/         # Major segment: competitive analysis
│       └── feasibility/         # Major segment: feasibility studies
├── processes/
│   ├── workflows/
│   │   ├── business/            # Major segment: business workflows
│   │   ├── technical/           # Major segment: technical workflows
│   │   └── deployment/          # Major segment: deployment workflows
│   └── procedures/
│       ├── development/         # Major segment: development procedures
│       ├── testing/             # Major segment: testing procedures
│       └── deployment/          # Major segment: deployment procedures
└── architecture/
    ├── design/
    │   ├── system/              # Major segment: system design
    │   ├── database/            # Major segment: database design
    │   └── api/                 # Major segment: API design
    └── patterns/
        ├── design-patterns/     # Major segment: design patterns
        └── architectural-patterns/ # Major segment: architectural patterns
```

**Enhanced Metadata:**
```python
class DocumentReference(BaseModel):
    # ... existing fields ...
    
    # Segmentation fields
    category: str                    # planning, architecture, guides, etc.
    subcategory: Optional[str] = None # functional, non-functional, business, technical, etc.
    component: Optional[str] = None   # auth, payment, database, api, etc.
    domain: Optional[str] = None      # security, performance, scalability, etc.
    tags: Optional[List[str]] = None  # Flexible tagging
    
    # Examples:
    # Requirements: category="planning", subcategory="functional", component="auth"
    # Workflow: category="processes", subcategory="business", component="onboarding"
    # Design: category="architecture", subcategory="system", component="database"
```

---

## 🎯 **Segmentation Rules**

### **When to Use Subcategories vs Metadata**

#### **Use Subcategories When:**
- **Clear Major Segments**: Distinct types that are commonly separated
- **High Volume**: Many documents of each type
- **Different Audiences**: Different stakeholders for each segment
- **Different Lifecycles**: Different review/approval processes

**Examples:**
- `requirements/functional/` vs `requirements/non-functional/`
- `workflows/business/` vs `workflows/technical/`
- `design/system/` vs `design/database/`

#### **Use Metadata When:**
- **Fine-Grained Segmentation**: Many small segments
- **Cross-Cutting Concerns**: Same document type across multiple domains
- **Flexible Filtering**: Need to filter by multiple dimensions
- **Dynamic Segmentation**: Segments change frequently

**Examples:**
- Component-based: `auth`, `payment`, `reporting`
- Domain-based: `security`, `performance`, `scalability`
- Tag-based: `user-management`, `automation`, `compliance`

---

## 🚀 **Implementation Strategy**

### **Phase 1: Identify Major Segments**

Analyze each category to identify natural major segments:

```python
SEGMENTATION_RULES = {
    "planning": {
        "requirements": ["functional", "non-functional", "security", "performance", "business"],
        "analysis": ["market-research", "competitive", "feasibility", "stakeholder"],
        "specifications": ["technical", "functional", "interface"]
    },
    "processes": {
        "workflows": ["business", "technical", "deployment", "incident-response"],
        "procedures": ["development", "testing", "deployment", "maintenance"],
        "standards": ["coding", "documentation", "security", "performance"]
    },
    "architecture": {
        "design": ["system", "database", "api", "security", "performance"],
        "patterns": ["design-patterns", "architectural-patterns", "anti-patterns"],
        "integration": ["api-integration", "data-integration", "service-integration"]
    },
    "guides": {
        "user": ["getting-started", "advanced", "troubleshooting"],
        "developer": ["setup", "development", "testing", "deployment"],
        "admin": ["installation", "configuration", "maintenance", "troubleshooting"]
    },
    "reference": {
        "api": ["rest", "graphql", "websocket", "grpc"],
        "runbooks": ["deployment", "incident-response", "maintenance", "backup"],
        "configuration": ["environment", "database", "services", "security"]
    }
}
```

### **Phase 2: Enhanced Document Types**

Add subcategory-aware document types:

```python
class DocumentType(str, Enum):
    # Requirements with subcategories
    FUNCTIONAL_REQUIREMENTS = "functional_requirements"     # → docs/planning/requirements/functional/
    NON_FUNCTIONAL_REQUIREMENTS = "non_functional_requirements" # → docs/planning/requirements/non-functional/
    SECURITY_REQUIREMENTS = "security_requirements"         # → docs/planning/requirements/security/
    PERFORMANCE_REQUIREMENTS = "performance_requirements"   # → docs/planning/requirements/performance/
    BUSINESS_REQUIREMENTS = "business_requirements"         # → docs/planning/requirements/business/
    
    # Workflows with subcategories
    BUSINESS_WORKFLOW = "business_workflow"                 # → docs/processes/workflows/business/
    TECHNICAL_WORKFLOW = "technical_workflow"               # → docs/processes/workflows/technical/
    DEPLOYMENT_WORKFLOW = "deployment_workflow"             # → docs/processes/workflows/deployment/
    INCIDENT_RESPONSE_WORKFLOW = "incident_response_workflow" # → docs/processes/workflows/incident-response/
    
    # Design with subcategories
    SYSTEM_DESIGN = "system_design"                         # → docs/architecture/design/system/
    DATABASE_DESIGN = "database_design"                     # → docs/architecture/design/database/
    API_DESIGN = "api_design"                               # → docs/architecture/design/api/
    SECURITY_DESIGN = "security_design"                     # → docs/architecture/design/security/
    PERFORMANCE_DESIGN = "performance_design"               # → docs/architecture/design/performance/
    
    # ... other types
```

### **Phase 3: Enhanced Placement Rules**

```python
def get_document_path(document_type: DocumentType, title: str, subcategory: str = None) -> str:
    """Generate document path with subcategory support."""
    
    # Base type mapping
    base_mapping = {
        DocumentType.FUNCTIONAL_REQUIREMENTS: "planning/requirements/functional",
        DocumentType.NON_FUNCTIONAL_REQUIREMENTS: "planning/requirements/non-functional",
        DocumentType.SECURITY_REQUIREMENTS: "planning/requirements/security",
        DocumentType.BUSINESS_WORKFLOW: "processes/workflows/business",
        DocumentType.TECHNICAL_WORKFLOW: "processes/workflows/technical",
        DocumentType.SYSTEM_DESIGN: "architecture/design/system",
        DocumentType.DATABASE_DESIGN: "architecture/design/database",
        # ... other mappings
    }
    
    # Get base directory
    directory = base_mapping.get(document_type, "reference/other")
    
    # Add subcategory if provided and not already in path
    if subcategory and subcategory not in directory:
        directory = f"{directory}/{subcategory}"
    
    filename = _slugify(title) + ".md"
    return f"docs/{directory}/{filename}"
```

---

## 📊 **Benefits of Segmentation Strategy**

### **1. Clear Organization**
- **Major Segments**: Clear separation of different document types
- **Logical Grouping**: Related documents grouped together
- **Easy Navigation**: Predictable directory structure

### **2. Flexible Filtering**
- **Subcategory Filtering**: Filter by major segments
- **Component Filtering**: Filter by specific components
- **Domain Filtering**: Filter by cross-cutting concerns
- **Tag Filtering**: Flexible, multi-dimensional filtering

### **3. Scalable Structure**
- **Growth Support**: Easy to add new segments
- **Project Adaptation**: Can be customized per project
- **Maintenance**: Clear boundaries for maintenance

### **4. Rich Queries**
```bash
# Subcategory-based queries
apm document list --category=planning --subcategory=functional
apm document list --category=processes --subcategory=business

# Component-based queries
apm document list --component=auth
apm document list --component=database

# Domain-based queries
apm document list --domain=security
apm document list --domain=performance

# Complex queries
apm document list --category=planning --subcategory=functional --component=auth
apm document search "authentication" --domain=security --subcategory=functional
```

---

## 🎯 **Recommendation: Hybrid Approach**

### **Use Subcategories for Major Segments**
- **Requirements**: functional, non-functional, security, performance, business
- **Workflows**: business, technical, deployment, incident-response
- **Design**: system, database, api, security, performance
- **Procedures**: development, testing, deployment, maintenance

### **Use Metadata for Fine-Grained Segmentation**
- **Component**: auth, payment, database, api, reporting
- **Domain**: security, performance, scalability, compliance
- **Tags**: user-management, automation, integration, monitoring

### **Benefits**
- **Clear Structure**: Major segments have dedicated directories
- **Flexible Filtering**: Metadata enables complex queries
- **Scalable**: Easy to add new segments and metadata
- **Maintainable**: Clear boundaries and predictable structure

---

## 🎯 **Conclusion**

The **Hybrid Segmentation Strategy** provides:

- **Subcategories**: For major, distinct segments with dedicated directories
- **Metadata**: For fine-grained segmentation and flexible filtering
- **Clear Organization**: Predictable directory structure
- **Rich Queries**: Multi-dimensional filtering capabilities
- **Scalable Design**: Easy to extend and customize

**Key Innovation**: Combine subcategory-based directories for major segments with metadata-driven filtering for fine-grained segmentation, providing both clear organization and flexible querying capabilities.

This approach handles the practical reality of multiple document types within categories while maintaining a clean, scalable structure.

---

**Version**: 1.0  
**Last Updated**: 2025-01-27  
**Status**: Segmentation Strategy - Ready for Implementation  
**Next Step**: Implement hybrid segmentation in database schema and placement rules
