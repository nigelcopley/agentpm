# APM (Agent Project Manager) Frameworks Reference

**Purpose**: Quick reference for all frameworks and principles implemented in APM (Agent Project Manager)  
**Format**: Categorized definitions with practical examples

---

## **🎯 The Pyramid of Software Development Principles**

*Based on [Bartosz Krajka's Pyramid](https://bartoszkrajka.com/2019/10/21/the-pyramid-of-software-development-principles/)*

**Foundation**: You shouldn't undermine lower layers at the expense of higher layers. When principles conflict, choose the one lower on the pyramid.

### **1. Make it Work** - FOUNDATION
**Definition**: Code must work correctly before any other principle applies  
**Application**: All other principles are secondary to functional correctness  
**Example**: Fix bugs before refactoring, ensure tests pass before optimization

### **2. YAGNI (You Aren't Gonna Need It)** - SECOND
**Definition**: Don't build features for imagined future needs  
**Application**: Delete code that isn't actively used  
**Example**: Remove unused imports, don't create abstractions until needed

### **3. Principle of Least Surprise** - THIRD
**Definition**: Code should behave as expected by other developers/agents  
**Application**: Predictable APIs, consistent naming, expected behavior  
**Example**: Context assembly should always return the same structure

### **4. KISS (Keep It Simple, Stupid)** - FOURTH
**Definition**: Always choose the simplest solution that works  
**Application**: Start simple, add complexity only when proven necessary  
**Example**: Use Python standard library before external packages

### **5. Be Consistent** - FIFTH
**Definition**: Maintain consistency across the codebase  
**Application**: Use same patterns, naming conventions, and structures  
**Example**: All services follow DatabaseService pattern

### **6. DRY (Don't Repeat Yourself)** - SIXTH
**Definition**: Reuse existing code and eliminate duplication  
**Application**: Search existing code BEFORE implementing  
**Example**: Use DatabaseService pattern for all services

### **7. Clean Code** - SEVENTH
**Definition**: Write meaningful names, short methods, clear structure  
**Application**: Code should be self-documenting and easy to read  
**Example**: Descriptive variable names, short focused methods

### **8. SOLID** - EIGHTH
**Definition**: Apply when it doesn't violate higher principles  
**Application**: Single responsibility per service, no premature abstractions  
**Example**: ContextAssemblyService has single responsibility

### **9. Design Patterns** - NINTH
**Definition**: Add complexity only where you've identified common issues  
**Application**: Use patterns to solve real problems, not speculative ones  
**Example**: Factory pattern for plugin creation

### **10. Agile Practices** - TENTH
**Definition**: Add complexity for predicted future needs  
**Application**: Adaptive software with speculative abstractions  
**Example**: Plugin system for future frameworks

### **11. Boy Scout Rule** - ELEVENTH
**Definition**: Clean up code when you encounter it, but not at the expense of higher principles  
**Application**: Leave code better than you found it, but only if it's quick  
**Example**: Fix obvious issues during development

### **12. Make it Fast** - TWELFTH
**Definition**: Optimize for performance after everything else is working  
**Application**: Measure first, optimize second  
**Example**: Profile before optimizing, cache frequently accessed data

---

## **🏗️ Architecture Patterns**

### **Three-Layer Architecture**
**Definition**: Models → Services → Routes separation  
**Application**: Clear separation of concerns, testable at each layer  
**Example**: DatabaseService → ProjectMethods → ProjectRoutes

### **Service Coordinator Pattern**
**Definition**: Main service coordinator with method delegation  
**Application**: Consistent interface across services, lazy loading  
**Example**: DatabaseService is the gold standard pattern

### **Plugin Architecture**
**Definition**: Framework-agnostic core with plugin intelligence  
**Application**: Extensible without core changes, framework detection  
**Example**: PythonPlugin, DjangoPlugin, ReactPlugin

---

## **📋 Project Management Frameworks**

### **LEAN Philosophy**
**Definition**: Eliminate waste, MVP focus, just-enough planning  
**Best For**: Startups, rapid validation, uncertain requirements  
**AI Behavior**: Prioritize Micro-MVP, defer nice-to-haves

### **AGILE Philosophy**
**Definition**: Iterative delivery, time-boxed, working software over docs  
**Best For**: Software products, evolving requirements  
**AI Behavior**: Time-box tasks (4h), prioritize working code

### **PMBOK Philosophy**
**Definition**: Structured, comprehensive, formal processes and gates  
**Best For**: Enterprise, regulated industries, fixed requirements  
**AI Behavior**: Create comprehensive specs, formal ADRs, full planning

### **AIPM_HYBRID Philosophy** (Default)
**Definition**: Agile time-boxing + PMBOK dependencies + Lean waste elimination  
**Best For**: Complex projects, AI-assisted development, balance needed  
**AI Behavior**: Structure + pragmatism, validate each phase

---

## **🧠 Context & Intelligence Frameworks**

### **6W Framework (UnifiedSixW)**
**Definition**: WHO, WHAT, WHERE, WHEN, WHY, HOW with hierarchical scaling  
**Application**: Consistent structure across Project/WorkItem/Task levels  
**Example**: Project (@cto, @team) → WorkItem (@tech-lead) → Task (@alice)

### **Confidence Scoring**
**Definition**: (6w * 0.35) + (facts * 0.25) + (amalg * 0.25) + (fresh * 0.15)  
**Bands**: RED (<0.5), YELLOW (0.5-0.8), GREEN (>0.8)  
**Application**: Quality assessment for AI agent enablement

### **Plugin Intelligence**
**Definition**: Framework-specific facts and code amalgamations  
**Application**: 3-phase detection (files → imports → structure)  
**Example**: Django detection via manage.py, settings.py, models.py

---

## **✅ Quality & Governance Frameworks**

### **Time-Boxing (STRICT)**
**Definition**: Enforced limits on task duration  
**Limits**: IMPLEMENTATION (4h), DESIGN (8h), TESTING (6h), DOCUMENTATION (6h)  
**Application**: Prevents overengineering, maintains focus

### **Quality Gates**
**Definition**: State transitions with validation requirements  
**Gates**: proposed → validated → accepted → in_progress → review → completed  
**Application**: Prevents agents from skipping essential steps

### **Agent-First Design**
**Definition**: Every component must enable effective agent operation  
**Requirements**: Clear outputs, automatic context, actionable errors  
**Application**: Structured responses, quality indicators, guidance

---

## **🔒 Security Principles**

### **Input Validation**
**Definition**: Validate all user inputs at boundaries  
**Application**: Prevent injection attacks, use Click validators  
**Example**: Sanitize CLI inputs, validate file paths

### **Command Security**
**Definition**: Secure command execution and file operations  
**Application**: Whitelist approach, timeout protection  
**Example**: Secure file operations with permission checks

---

## **📊 Data Patterns**

### **Three-Layer Database Architecture**
**Definition**: Models → Adapters → Methods separation  
**Application**: Type safety, clear separation of concerns  
**Example**: Pydantic models, database adapters, business logic methods

### **Context Data Flow**
**Definition**: Project → Work Item → Task → Agent hierarchical flow  
**Application**: Task overrides Work Item overrides Project  
**Example**: Merged context with most specific level winning

---

## **🌐 Web Interface Patterns**

### **Three-Layer Web Architecture**
**Definition**: Routes → Services → Database integration  
**Application**: Consistent with APM (Agent Project Manager) architecture  
**Example**: Flask routes, service coordinators, database service

### **Template Patterns**
**Definition**: Consistent UI components and layouts  
**Application**: Reusable components, standardized forms  
**Example**: Base template, component templates, error pages

---

## **🚀 Implementation Examples**

### **Creating a New Service**
```python
class NewService(CoreServiceInterface):
    def __init__(self, db_service: DatabaseService):
        self.db = db_service
    
    def operation(self, data) -> ServiceResult:
        # Follow DatabaseService pattern
        pass
```

### **Adding 6W Context**
```python
six_w = UnifiedSixW(
    implementers=['@alice', '@bob'],
    functional_requirements=['User authentication'],
    affected_services=['auth-service'],
    business_value='Improved user experience'
)
```

### **Calculating Confidence**
```python
score = ConfidenceScorer.calculate_confidence(
    six_w=six_w,
    plugin_facts=plugin_facts,
    amalgamations=amalgamations,
    freshness_days=5
)
```

---

## **📚 Quick Reference**

### **Essential Commands**
```bash
apm init "Project" --pm-philosophy=lean
apm work-item create "Feature" --type feature
apm task create "Task" --type implementation --effort 4
apm context show --task-id=5
```

### **Key Directories**
```
agentpm/core/          # Core services
agentpm/cli/           # CLI commands
docs/principles/       # This documentation
tests/                 # Test suites
```

### **Critical Rules**
- **Never skip quality gates** - system enforces them
- **IMPLEMENTATION tasks max 4h** - enforced strictly
- **Use Rich for all CLI output** - no plain print statements
- **Validate all inputs** - security requirement
- **Test everything** - >90% coverage required

---

**Last Updated**: 2025-10-13  
**Version**: 1.0.0
