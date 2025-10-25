"""
Type Enumerations

Defines categorical types for work items, development philosophy,
entity types, context types, resource types, confidence bands, and enforcement levels.
"""

from enum import Enum


class WorkItemType(str, Enum):
    """
    Work item categorization (strategic deliverables).

    Work items represent substantial work that breaks down into multiple tasks.
    All significant work flows through work items.

    Types:
    - FEATURE: Build new capability/system
    - ENHANCEMENT: Improve existing capability
    - BUGFIX: Fix substantial defect (epic-level bug)
    - RESEARCH: Investigation/spike (gather information)
    - PLANNING: Architecture/design/roadmap (make decisions)
    - REFACTORING: Large-scale code improvement (no feature change)
    - INFRASTRUCTURE: DevOps/platform work (CI/CD, deployment, tooling)
    - MAINTENANCE: Continuous upkeep/operational backlog
    - MONITORING: Continuous observability and alert response backlog
    - DOCUMENTATION: Living documentation backlog
    - SECURITY: Continuous security and compliance backlog
    - FIX_BUGS_ISSUES: Auto-aggregated bug/issue backlog (continuous)
    """
    FEATURE = "feature"
    ENHANCEMENT = "enhancement"
    BUGFIX = "bugfix"
    RESEARCH = "research"
    ANALYSIS = "analysis"
    PLANNING = "planning"
    REFACTORING = "refactoring"
    INFRASTRUCTURE = "infrastructure"
    MAINTENANCE = "maintenance"
    MONITORING = "monitoring"
    DOCUMENTATION = "documentation"
    SECURITY = "security"
    FIX_BUGS_ISSUES = "fix_bugs_issues"

    @classmethod
    def choices(cls) -> list[str]:
        """Get all enum values for CLI/form dropdowns."""
        return [item.value for item in cls]

    @classmethod
    def from_string(cls, value: str):
        """Safe conversion from string with helpful error message."""
        try:
            return cls(value)
        except ValueError:
            valid = ", ".join(cls.choices())
            raise ValueError(f"Invalid {cls.__name__}: '{value}'. Valid: {valid}")

    @classmethod
    def labels(cls) -> dict[str, str]:
        """Human-readable labels for UI display."""
        return {
            cls.FEATURE.value: "Feature - Build new capability",
            cls.ENHANCEMENT.value: "Enhancement - Improve existing capability",
            cls.BUGFIX.value: "Bug Fix - Fix substantial defect",
            cls.RESEARCH.value: "Research - Investigation/spike",
            cls.ANALYSIS.value: "Analysis - Analyze and document",
            cls.PLANNING.value: "Planning - Architecture/design",
            cls.REFACTORING.value: "Refactoring - Code improvement",
            cls.INFRASTRUCTURE.value: "Infrastructure - DevOps/platform work",
            cls.MAINTENANCE.value: "Maintenance - Continuous upkeep backlog",
            cls.MONITORING.value: "Monitoring - Observability/SLA backlog",
            cls.DOCUMENTATION.value: "Documentation - Living documentation backlog",
            cls.SECURITY.value: "Security - Continuous security backlog",
            cls.FIX_BUGS_ISSUES.value: "Fix Bugs/Issues - Auto-aggregated bug backlog",
        }

    @classmethod
    def continuous_types(cls) -> set['WorkItemType']:
        """Return work item types that are treated as continuous backlogs."""
        return {
            cls.MAINTENANCE,
            cls.MONITORING,
            cls.DOCUMENTATION,
            cls.SECURITY,
            cls.FIX_BUGS_ISSUES,
        }

    @classmethod
    def is_continuous_type(cls, work_item_type: 'WorkItemType') -> bool:
        """Check whether work item type represents a continuous backlog."""
        return work_item_type in cls.continuous_types()


class TaskType(str, Enum):
    """
    Task type determines validation requirements and quality gates.

    Each type has different requirements for state transitions:
    - DESIGN: Requires design docs, diagrams, review
    - IMPLEMENTATION: Requires code, tests, review
    - TESTING: Requires test cases, coverage, passing tests
    - BUGFIX: Requires reproduction steps, fix verification
    - REFACTORING: Requires before/after comparison, tests still pass
    - DOCUMENTATION: Requires completeness check, review
    - DEPLOYMENT: Requires deployment plan, verification, rollback plan
    - REVIEW: Requires review criteria, feedback documentation
    - ANALYSIS: Requires findings, conclusions, recommendations
    - SIMPLE: Minimal requirements (< 1 hour tasks)
    """
    DESIGN = "design"                  # Design/planning activity
    IMPLEMENTATION = "implementation"  # Write code
    TESTING = "testing"                # Write tests
    BUGFIX = "bugfix"                  # Fix small bug
    REFACTORING = "refactoring"        # Improve code
    DOCUMENTATION = "documentation"    # Write docs
    DEPLOYMENT = "deployment"          # Deploy/release
    REVIEW = "review"                  # Code review activity
    ANALYSIS = "analysis"              # Investigation/research
    RESEARCH = "research"              # Spike/proof of concept
    MAINTENANCE = "maintenance"        # Ongoing support
    OPTIMIZATION = "optimization"      # Performance/security optimization
    INTEGRATION = "integration"        # Integrate systems/components
    TRAINING = "training"              # Learning/training activity
    MEETING = "meeting"                # Meetings/discussions
    PLANNING = "planning"              # Task/project planning
    DEPENDENCY = "dependency"          # Manage dependencies
    BLOCKER = "blocker"                # Resolve blockers/issues
    SIMPLE = "simple"                  # Quick task (< 1 hour)
    OTHER = "other"                    # Miscellaneous tasks

    @classmethod
    def choices(cls) -> list[str]:
        """Get all enum values for CLI/form dropdowns."""
        return [item.value for item in cls]

    @classmethod
    def from_string(cls, value: str):
        """Safe conversion from string with helpful error message."""
        try:
            return cls(value)
        except ValueError:
            valid = ", ".join(cls.choices())
            raise ValueError(f"Invalid {cls.__name__}: '{value}'. Valid: {valid}")

    @classmethod
    def labels(cls) -> dict[str, str]:
        """Human-readable labels for UI display."""
        return {
            cls.DESIGN.value: "Design - Design/planning activity",
            cls.IMPLEMENTATION.value: "Implementation - Write code",
            cls.TESTING.value: "Testing - Write tests",
            cls.BUGFIX.value: "Bug Fix - Fix small bug",
            cls.REFACTORING.value: "Refactoring - Improve code",
            cls.DOCUMENTATION.value: "Documentation - Write docs",
            cls.DEPLOYMENT.value: "Deployment - Deploy/release",
            cls.REVIEW.value: "Review - Code review activity",
            cls.ANALYSIS.value: "Analysis - Investigation/research",
            cls.RESEARCH.value: "Research - Spike/proof of concept",
            cls.MAINTENANCE.value: "Maintenance - Ongoing support",
            cls.OPTIMIZATION.value: "Optimization - Performance/security",
            cls.INTEGRATION.value: "Integration - Integrate systems",
            cls.TRAINING.value: "Training - Learning activity",
            cls.MEETING.value: "Meeting - Meetings/discussions",
            cls.PLANNING.value: "Planning - Task/project planning",
            cls.DEPENDENCY.value: "Dependency - Manage dependencies",
            cls.BLOCKER.value: "Blocker - Resolve blockers",
            cls.SIMPLE.value: "Simple - Quick task",
            cls.OTHER.value: "Other - Miscellaneous tasks",
        }


class DevelopmentPhilosophy(str, Enum):
    """
    Development philosophy options for Rules system.

    Defines the approach and principles guiding development.
    Used in Rule model config, not as a Project field.

    Example Rule:
        Rule(
            rule_id="DEV-PHILOSOPHY",
            name="Follow Professional Standards",
            enforcement_level=EnforcementLevel.GUIDE,
            config={"philosophy": DevelopmentPhilosophy.PROFESSIONAL_STANDARDS}
        )
    """
    KISS_FIRST = "kiss_first"
    YAGNI = "yagni"
    DRY = "dry"
    SOLID = "solid"
    BEHAVIOUR_DRIVEN = "behaviour_driven"
    DESIGN_DRIVEN = "design_driven"
    TEST_DRIVEN = "test_driven"
    AGILE = "agile"
    PROFESSIONAL_STANDARDS = "professional_standards"
    CONTEXT_AWARE = "context_aware"
    DOMAIN_DRIVEN = "domain_driven"
    DATA_DRIVEN = "data_driven"
    DATA_AWARE = "data_aware"

    @classmethod
    def choices(cls) -> list[str]:
        """Get all enum values for CLI/form dropdowns."""
        return [item.value for item in cls]

    @classmethod
    def from_string(cls, value: str):
        """Safe conversion from string with helpful error message."""
        try:
            return cls(value)
        except ValueError:
            valid = ", ".join(cls.choices())
            raise ValueError(f"Invalid {cls.__name__}: '{value}'. Valid: {valid}")


class ProjectManagementPhilosophy(str, Enum):
    """
    Project management approach for guiding AI agent planning and execution.

    Constrains how AI agents plan work, create documentation, and make decisions.
    Critical for preventing overengineering and maintaining focus.

    LEAN: Eliminate waste, MVP focus, just-enough planning/docs
      Principles:
        - Build smallest thing that could work
        - Validate before expanding
        - Documentation: Only what's essential
        - Planning: Just-in-time, not comprehensive upfront
      Best for: Startups, rapid validation, uncertain requirements
      AI behavior: Prioritize Micro-MVP, defer nice-to-haves
      Example: "Fix session hooks (2 weeks) before building full platform"

    AGILE: Iterative delivery, time-boxed, working software over comprehensive docs
      Principles:
        - Deliver working increments every 2 weeks
        - Respond to change over following plan
        - Documentation: User stories, acceptance criteria only
        - Planning: Sprint-based, adjust each iteration
      Best for: Software products, evolving requirements
      AI behavior: Time-box tasks (4h), prioritize working code
      Example: "8-week MVP with bi-weekly demos and feedback"

    PMBOK: Structured, comprehensive, formal processes and gates
      Principles:
        - Plan thoroughly before execution
        - Manage dependencies and critical path
        - Documentation: Complete specifications upfront
        - Planning: All phases defined before starting
      Best for: Enterprise, regulated industries, fixed requirements
      AI behavior: Create comprehensive specs, formal ADRs, full planning
      Example: "20-week plan with all 11 ADRs before implementation"

    AIPM_HYBRID: AIPM's default (Agile time-boxing + PMBOK dependencies + Lean waste elimination)
      Principles:
        - Phased delivery with validation gates (Lean)
        - Time-boxed tasks (Agile: 4h implementation, 6h testing)
        - Dependency management (PMBOK: critical path, scheduling)
        - Evidence-based decisions (AIPM: decisions linked to evidence)
      Best for: Complex projects, AI-assisted development, balance needed
      AI behavior: Structure + pragmatism, validate each phase
      Example: "8-week MVP, 5 core ADRs, validation at weeks 2, 4, 6, 8"

    Usage:
      # Set on project initialization
      apm init "My Project" --pm-philosophy=lean

      # Or update existing project
      apm project update --pm-philosophy=lean

      # AI agents read this in context
      # Adjust behavior accordingly
      # Prevents overengineering by providing constraints
    """
    LEAN = "lean"              # Eliminate waste, MVP first, validate fast
    AGILE = "agile"            # Iterative, time-boxed, working software
    PMBOK = "pmbok"            # Structured, comprehensive, formal
    AIPM_HYBRID = "aipm_hybrid"  # Default: Best of all three (balanced)

    @classmethod
    def choices(cls) -> list[str]:
        """Get all enum values for CLI/form dropdowns."""
        return [item.value for item in cls]

    @classmethod
    def from_string(cls, value: str):
        """Safe conversion from string with helpful error message."""
        try:
            return cls(value)
        except ValueError:
            valid = ", ".join(cls.choices())
            raise ValueError(f"Invalid {cls.__name__}: '{value}'. Valid: {valid}")


class EntityType(str, Enum):
    """
    Entity type for polymorphic relationships.

    Used in Context model to identify which entity the context belongs to.
    Also used for search scope and search adapters.
    """
    PROJECT = "project"
    WORK_ITEM = "work_item"
    TASK = "task"
    IDEA = "idea"  # NEW: Ideas integration
    DOCUMENT = "document"  # NEW: Document references (WI-133)
    DOCUMENT_REFERENCE = "document_reference"  # NEW: Document reference (alias)
    SUMMARY = "summary"  # NEW: Summaries
    EVIDENCE = "evidence"  # NEW: Evidence sources
    SESSION = "session"  # NEW: Sessions
    LEARNING = "learning"  # NEW: Learnings (future use)

    @classmethod
    def choices(cls) -> list[str]:
        """Get all enum values for CLI/form dropdowns."""
        return [item.value for item in cls]

    @classmethod
    def from_string(cls, value: str):
        """Safe conversion from string with helpful error message."""
        try:
            return cls(value)
        except ValueError:
            valid = ", ".join(cls.choices())
            raise ValueError(f"Invalid {cls.__name__}: '{value}'. Valid: {valid}")


class ContextType(str, Enum):
    """
    Context categorization.

    Unified context system supports both resource files and entity contexts.
    """
    # Resource file contexts
    RESOURCE_FILE = "resource_file"

    # Entity contexts (linked to specific entities)
    PROJECT_CONTEXT = "project_context"
    WORK_ITEM_CONTEXT = "work_item_context"
    TASK_CONTEXT = "task_context"
    RULES_CONTEXT = "rules_context"  # Questionnaire answers and configuration
    
    # NEW: Rich Context Types
    BUSINESS_PILLARS_CONTEXT = "business_pillars_context"
    MARKET_RESEARCH_CONTEXT = "market_research_context"
    COMPETITIVE_ANALYSIS_CONTEXT = "competitive_analysis_context"
    QUALITY_GATES_CONTEXT = "quality_gates_context"
    STAKEHOLDER_CONTEXT = "stakeholder_context"
    TECHNICAL_CONTEXT = "technical_context"
    IMPLEMENTATION_CONTEXT = "implementation_context"
    
    # NEW: Ideas Integration
    IDEA_CONTEXT = "idea_context"
    IDEA_TO_WORK_ITEM_MAPPING = "idea_to_work_item_mapping"

    @classmethod
    def choices(cls) -> list[str]:
        """Get all enum values for CLI/form dropdowns."""
        return [item.value for item in cls]

    @classmethod
    def from_string(cls, value: str):
        """Safe conversion from string with helpful error message."""
        try:
            return cls(value)
        except ValueError:
            valid = ", ".join(cls.choices())
            raise ValueError(f"Invalid {cls.__name__}: '{value}'. Valid: {valid}")

    @classmethod
    def labels(cls) -> dict[str, str]:
        """Human-readable labels for UI display."""
        return {
            cls.RESOURCE_FILE.value: "Resource File",
            cls.PROJECT_CONTEXT.value: "Project Context",
            cls.WORK_ITEM_CONTEXT.value: "Work Item Context",
            cls.TASK_CONTEXT.value: "Task Context",
            cls.RULES_CONTEXT.value: "Rules/Configuration Context",
            cls.BUSINESS_PILLARS_CONTEXT.value: "Business Pillars Context",
            cls.MARKET_RESEARCH_CONTEXT.value: "Market Research Context",
            cls.COMPETITIVE_ANALYSIS_CONTEXT.value: "Competitive Analysis Context",
            cls.QUALITY_GATES_CONTEXT.value: "Quality Gates Context",
            cls.STAKEHOLDER_CONTEXT.value: "Stakeholder Context",
            cls.TECHNICAL_CONTEXT.value: "Technical Context",
            cls.IMPLEMENTATION_CONTEXT.value: "Implementation Context",
            cls.IDEA_CONTEXT.value: "Idea Context",
            cls.IDEA_TO_WORK_ITEM_MAPPING.value: "Idea to Work Item Mapping",
        }


class ResourceType(str, Enum):
    """
    Resource file categorization.

    Used when context_type is RESOURCE_FILE.
    """
    SOP = "sop"
    CODE = "code"
    SPECIFICATION = "specification"
    DOCUMENTATION = "documentation"

    @classmethod
    def choices(cls) -> list[str]:
        """Get all enum values for CLI/form dropdowns."""
        return [item.value for item in cls]

    @classmethod
    def from_string(cls, value: str):
        """Safe conversion from string with helpful error message."""
        try:
            return cls(value)
        except ValueError:
            valid = ", ".join(cls.choices())
            raise ValueError(f"Invalid {cls.__name__}: '{value}'. Valid: {valid}")


class ConfidenceBand(str, Enum):
    """
    Confidence scoring bands for context quality.

    RED: < 0.5 (insufficient context, agent cannot operate)
    YELLOW: 0.5-0.8 (adequate context, agent can operate with limitations)
    GREEN: > 0.8 (high-quality context, agent fully enabled)
    """
    RED = "RED"
    YELLOW = "YELLOW"
    GREEN = "GREEN"

    @classmethod
    def from_score(cls, score: float) -> 'ConfidenceBand':
        """
        Convert confidence score to band.

        Args:
            score: Confidence score (0.0-1.0)

        Returns:
            Appropriate confidence band
        """
        if score < 0.5:
            return cls.RED
        elif score < 0.8:
            return cls.YELLOW
        else:
            return cls.GREEN

    @classmethod
    def choices(cls) -> list[str]:
        """Get all enum values for CLI/form dropdowns."""
        return [item.value for item in cls]

    @classmethod
    def from_string(cls, value: str):
        """Safe conversion from string with helpful error message."""
        try:
            return cls(value)
        except ValueError:
            valid = ", ".join(cls.choices())
            raise ValueError(f"Invalid {cls.__name__}: '{value}'. Valid: {valid}")


class EnforcementLevel(str, Enum):
    """
    Rule enforcement levels.

    Defines how strictly rules are enforced:
    - BLOCK: Hard stop, operation fails
    - LIMIT: Soft limit, warning issued
    - GUIDE: Suggestion, no enforcement
    - ENHANCE: Quality improvement suggestion
    """
    BLOCK = "BLOCK"
    LIMIT = "LIMIT"
    GUIDE = "GUIDE"
    ENHANCE = "ENHANCE"

    @classmethod
    def choices(cls) -> list[str]:
        """Get all enum values for CLI/form dropdowns."""
        return [item.value for item in cls]

    @classmethod
    def from_string(cls, value: str):
        """Safe conversion from string with helpful error message."""
        try:
            return cls(value)
        except ValueError:
            valid = ", ".join(cls.choices())
            raise ValueError(f"Invalid {cls.__name__}: '{value}'. Valid: {valid}")


class ProjectType(str, Enum):
    """
    Project categorization for context and agent selection.

    GREENFIELD: New project from scratch
    BROWNFIELD: Existing codebase modernization
    MAINTENANCE: Ongoing support and updates
    RESEARCH: Experimental/spike project
    """
    GREENFIELD = "greenfield"
    BROWNFIELD = "brownfield"
    MAINTENANCE = "maintenance"
    RESEARCH = "research"

    @classmethod
    def choices(cls) -> list[str]:
        """Get all enum values for CLI/form dropdowns."""
        return [item.value for item in cls]

    @classmethod
    def from_string(cls, value: str):
        """Safe conversion from string with helpful error message."""
        try:
            return cls(value)
        except ValueError:
            valid = ", ".join(cls.choices())
            raise ValueError(f"Invalid {cls.__name__}: '{value}'. Valid: {valid}")


class ApplicationProjectType(str, Enum):
    """
    Application project type categorization for development context and agent selection.
    
    These types determine which development patterns, testing strategies, and
    deployment approaches are most appropriate for the project.
    """
    # Web Applications
    WEB_APP_FULLSTACK = "web_app_fullstack"
    WEB_APP_FRONTEND = "web_app_frontend"
    WEB_APP_BACKEND = "web_app_backend"
    
    # API Services
    API_REST = "api_rest"
    API_GRAPHQL = "api_graphql"
    API_MICROSERVICE = "api_microservice"
    API_GATEWAY = "api_gateway"
    
    # Command Line Tools
    CLI_TOOL = "cli_tool"
    CLI_UTILITY = "cli_utility"
    CLI_SCRIPT = "cli_script"
    
    # Libraries and Packages
    LIBRARY_PYTHON = "library_python"
    LIBRARY_NODE = "library_node"
    LIBRARY_RUST = "library_rust"
    LIBRARY_GENERIC = "library_generic"
    
    # Desktop Applications
    DESKTOP_ELECTRON = "desktop_electron"
    DESKTOP_NATIVE = "desktop_native"
    DESKTOP_CROSS_PLATFORM = "desktop_cross_platform"
    
    # Mobile Applications
    MOBILE_NATIVE = "mobile_native"
    MOBILE_CROSS_PLATFORM = "mobile_cross_platform"
    MOBILE_HYBRID = "mobile_hybrid"
    
    # Data Science and ML
    DATA_SCIENCE = "data_science"
    ML_MODEL = "ml_model"
    ML_PIPELINE = "ml_pipeline"
    DATA_PIPELINE = "data_pipeline"
    
    # Infrastructure and DevOps
    INFRASTRUCTURE = "infrastructure"
    DEVOPS_TOOL = "devops_tool"
    MONITORING = "monitoring"
    
    # Game Development
    GAME_2D = "game_2d"
    GAME_3D = "game_3d"
    GAME_MOBILE = "game_mobile"
    
    # IoT and Embedded
    IOT_DEVICE = "iot_device"
    EMBEDDED_SYSTEM = "embedded_system"
    
    # Blockchain and Web3
    BLOCKCHAIN_DAPP = "blockchain_dapp"
    SMART_CONTRACT = "smart_contract"
    WEB3_TOOL = "web3_tool"
    
    # Other
    PLUGIN_EXTENSION = "plugin_extension"
    AUTOMATION_SCRIPT = "automation_script"
    RESEARCH_PROTOTYPE = "research_prototype"

    @classmethod
    def choices(cls) -> list[str]:
        """Get all enum values for CLI/form dropdowns."""
        return [item.value for item in cls]

    @classmethod
    def from_string(cls, value: str):
        """Safe conversion from string with helpful error message."""
        try:
            return cls(value)
        except ValueError:
            valid = ", ".join(cls.choices())
            raise ValueError(f"Invalid {cls.__name__}: '{value}'. Valid: {valid}")
    
    @classmethod
    def get_display_name(cls, value: str) -> str:
        """Get human-readable display name for the project type."""
        display_names = {
            # Web Applications
            "web_app_fullstack": "Full-stack Web Application",
            "web_app_frontend": "Frontend Web Application",
            "web_app_backend": "Backend Web Application",
            
            # API Services
            "api_rest": "RESTful API Service",
            "api_graphql": "GraphQL API Service",
            "api_microservice": "Microservice API",
            "api_gateway": "API Gateway",
            
            # Command Line Tools
            "cli_tool": "Command-line Tool",
            "cli_utility": "CLI Utility",
            "cli_script": "CLI Script",
            
            # Libraries and Packages
            "library_python": "Python Library/Package",
            "library_node": "Node.js Library/Package",
            "library_rust": "Rust Library/Crate",
            "library_generic": "Generic Library/Package",
            
            # Desktop Applications
            "desktop_electron": "Electron Desktop App",
            "desktop_native": "Native Desktop Application",
            "desktop_cross_platform": "Cross-platform Desktop App",
            
            # Mobile Applications
            "mobile_native": "Native Mobile App",
            "mobile_cross_platform": "Cross-platform Mobile App",
            "mobile_hybrid": "Hybrid Mobile App",
            
            # Data Science and ML
            "data_science": "Data Science Project",
            "ml_model": "Machine Learning Model",
            "ml_pipeline": "ML Pipeline/Workflow",
            "data_pipeline": "Data Pipeline/ETL",
            
            # Infrastructure and DevOps
            "infrastructure": "Infrastructure as Code",
            "devops_tool": "DevOps Tool",
            "monitoring": "Monitoring/Observability Tool",
            
            # Game Development
            "game_2d": "2D Game",
            "game_3d": "3D Game",
            "game_mobile": "Mobile Game",
            
            # IoT and Embedded
            "iot_device": "IoT Device Application",
            "embedded_system": "Embedded System",
            
            # Blockchain and Web3
            "blockchain_dapp": "Blockchain dApp",
            "smart_contract": "Smart Contract",
            "web3_tool": "Web3 Tool",
            
            # Other
            "plugin_extension": "Plugin/Extension",
            "automation_script": "Automation Script",
            "research_prototype": "Research Prototype",
        }
        return display_names.get(value, value.replace("_", " ").title())
    
    @classmethod
    def get_description(cls, value: str) -> str:
        """Get detailed description for the project type."""
        descriptions = {
            # Web Applications
            "web_app_fullstack": "Complete web application with both frontend and backend components",
            "web_app_frontend": "Client-side web application (React, Vue, Angular, etc.)",
            "web_app_backend": "Server-side web application (Django, Flask, Express, etc.)",
            
            # API Services
            "api_rest": "RESTful API service following REST principles",
            "api_graphql": "GraphQL API service with flexible querying",
            "api_microservice": "Microservice architecture component",
            "api_gateway": "API gateway for routing and managing API requests",
            
            # Command Line Tools
            "cli_tool": "Interactive command-line tool with multiple commands",
            "cli_utility": "Simple command-line utility for specific tasks",
            "cli_script": "Automated script for batch processing",
            
            # Libraries and Packages
            "library_python": "Python package for distribution via PyPI",
            "library_node": "Node.js package for distribution via npm",
            "library_rust": "Rust crate for distribution via crates.io",
            "library_generic": "Reusable library in any language",
            
            # Desktop Applications
            "desktop_electron": "Desktop app built with Electron (web technologies)",
            "desktop_native": "Native desktop application (platform-specific)",
            "desktop_cross_platform": "Cross-platform desktop app (Qt, GTK, etc.)",
            
            # Mobile Applications
            "mobile_native": "Native mobile app (Swift/Kotlin, Objective-C/Java)",
            "mobile_cross_platform": "Cross-platform mobile app (React Native, Flutter)",
            "mobile_hybrid": "Hybrid mobile app (Cordova, Ionic)",
            
            # Data Science and ML
            "data_science": "Data analysis, visualisation, and scientific computing project",
            "ml_model": "Machine learning model training and inference",
            "ml_pipeline": "End-to-end ML workflow and pipeline",
            "data_pipeline": "Data processing, ETL, and transformation pipeline",
            
            # Infrastructure and DevOps
            "infrastructure": "Infrastructure provisioning and configuration",
            "devops_tool": "Development operations automation tool",
            "monitoring": "Application and infrastructure monitoring solution",
            
            # Game Development
            "game_2d": "2D game (Unity, Godot, custom engine)",
            "game_3d": "3D game (Unreal, Unity, custom engine)",
            "game_mobile": "Mobile game (iOS/Android)",
            
            # IoT and Embedded
            "iot_device": "Internet of Things device application",
            "embedded_system": "Embedded system firmware/software",
            
            # Blockchain and Web3
            "blockchain_dapp": "Decentralised application on blockchain",
            "smart_contract": "Blockchain smart contract",
            "web3_tool": "Web3 development tool or utility",
            
            # Other
            "plugin_extension": "Plugin or extension for existing software",
            "automation_script": "Script for automating repetitive tasks",
            "research_prototype": "Experimental or research prototype",
        }
        return descriptions.get(value, "Custom project type")


class Phase(str, Enum):
    """
    Project lifecycle phases for work item tracking.

    D1: Discovery (market research, requirements gathering)
    P1: Planning (architecture, design, task decomposition)
    I1: Implementation (coding, building)
    R1: Review (testing, QA, validation)
    O1: Operations (deployment, go-live, monitoring)
    E1: Evolution (iteration, improvements, technical debt)
    """
    D1_DISCOVERY = "D1_discovery"
    P1_PLAN = "P1_plan"
    I1_IMPLEMENTATION = "I1_implementation"
    R1_REVIEW = "R1_review"
    O1_OPERATIONS = "O1_operations"
    E1_EVOLUTION = "E1_evolution"

    @classmethod
    def choices(cls) -> list[str]:
        """Get all enum values for CLI/form dropdowns."""
        return [item.value for item in cls]

    @classmethod
    def from_string(cls, value: str):
        """Safe conversion from string with helpful error message."""
        try:
            return cls(value)
        except ValueError:
            valid = ", ".join(cls.choices())
            raise ValueError(f"Invalid {cls.__name__}: '{value}'. Valid: {valid}")


class SourceType(str, Enum):
    """
    Evidence source categorization for traceability.

    Used in evidence_sources table to classify research sources.
    """
    DOCUMENTATION = "documentation"
    RESEARCH = "research"
    STACKOVERFLOW = "stackoverflow"
    GITHUB = "github"
    INTERNAL_DOC = "internal_doc"
    MEETING_NOTES = "meeting_notes"
    EXPERT_OPINION = "expert_opinion"

    @classmethod
    def choices(cls) -> list[str]:
        """Get all enum values for CLI/form dropdowns."""
        return [item.value for item in cls]

    @classmethod
    def from_string(cls, value: str):
        """Safe conversion from string with helpful error message."""
        try:
            return cls(value)
        except ValueError:
            valid = ", ".join(cls.choices())
            raise ValueError(f"Invalid {cls.__name__}: '{value}'. Valid: {valid}")


class EventType(str, Enum):
    """
    Event categorization for audit trail.

    Used in events table to track workflow and agent actions.
    """
    WORKFLOW_TRANSITION = "workflow_transition"
    AGENT_ACTION = "agent_action"
    GATE_EXECUTION = "gate_execution"
    CONTEXT_REFRESH = "context_refresh"
    DEPENDENCY_ADDED = "dependency_added"
    BLOCKER_CREATED = "blocker_created"
    BLOCKER_RESOLVED = "blocker_resolved"
    WORK_ITEM_CREATED = "work_item_created"
    TASK_CREATED = "task_created"

    @classmethod
    def choices(cls) -> list[str]:
        """Get all enum values for CLI/form dropdowns."""
        return [item.value for item in cls]

    @classmethod
    def from_string(cls, value: str):
        """Safe conversion from string with helpful error message."""
        try:
            return cls(value)
        except ValueError:
            valid = ", ".join(cls.choices())
            raise ValueError(f"Invalid {cls.__name__}: '{value}'. Valid: {valid}")


class EventCategory(str, Enum):
    """
    Event category for grouping related events.

    Used in events table to categorize events for filtering and analysis.
    """
    WORKFLOW = "workflow"
    AGENT = "agent"
    GATE = "gate"
    CONTEXT = "context"
    DEPENDENCY = "dependency"
    BLOCKER = "blocker"
    ENTITY = "entity"
    SYSTEM = "system"

    @classmethod
    def choices(cls) -> list[str]:
        """Get all enum values for CLI/form dropdowns."""
        return [item.value for item in cls]

    @classmethod
    def from_string(cls, value: str):
        """Safe conversion from string with helpful error message."""
        try:
            return cls(value)
        except ValueError:
            valid = ", ".join(cls.choices())
            raise ValueError(f"Invalid {cls.__name__}: '{value}'. Valid: {valid}")


class EventSeverity(str, Enum):
    """
    Event severity for prioritization and alerting.

    Used in events table to indicate importance level.
    """
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

    @classmethod
    def choices(cls) -> list[str]:
        """Get all enum values for CLI/form dropdowns."""
        return [item.value for item in cls]

    @classmethod
    def from_string(cls, value: str):
        """Safe conversion from string with helpful error message."""
        try:
            return cls(value)
        except ValueError:
            valid = ", ".join(cls.choices())
            raise ValueError(f"Invalid {cls.__name__}: '{value}'. Valid: {valid}")


class DocumentCategory(str, Enum):
    """
    Top-level document categories for Universal Documentation System.

    Path Structure: docs/{category}/{document_type}/{filename}

    8 universal categories that work for any project type:
    - AIPM: planning, architecture, guides, reference, processes, governance, operations, communication
    - E-commerce: Same 8 categories (products→planning, checkout→architecture, etc.)
    - Mobile apps: Same 8 categories (auth→architecture, onboarding→guides, etc.)
    """
    PLANNING = "planning"
    ARCHITECTURE = "architecture"
    GUIDES = "guides"
    REFERENCE = "reference"
    PROCESSES = "processes"
    GOVERNANCE = "governance"
    OPERATIONS = "operations"
    COMMUNICATION = "communication"

    @classmethod
    def choices(cls) -> list[str]:
        """Get all enum values for CLI/form dropdowns."""
        return [item.value for item in cls]


class DocumentType(str, Enum):
    """
    Document categorization for document_references table.

    Classifies documents created during tasks/work items.

    Categories organized by purpose:
    - Planning: requirements, user_story, use_case
    - Architecture: architecture_doc, design_doc, adr, technical_spec
    - Implementation: implementation_plan, refactoring_guide, migration_guide
    - Testing: test_plan, test_report, coverage_report
    - Operations: runbook, deployment_guide, monitoring_guide
    - Documentation: user_guide, admin_guide, api_doc, troubleshooting
    - Analysis: research_report, analysis_report, assessment, competitive_analysis
    - Summaries: session_summary, status_report, progress_report, milestone_report
    - Business: business_pillars, market_research, stakeholder_analysis, quality_gates
    """
    # Planning documents
    IDEA = "idea"
    REQUIREMENTS = "requirements"
    USER_STORY = "user_story"
    USE_CASE = "use_case"

    # Architecture documents (renamed to avoid category name conflicts)
    ARCHITECTURE_DOC = "architecture_doc"  # Renamed from ARCHITECTURE
    DESIGN_DOC = "design_doc"              # Renamed from DESIGN
    ADR = "adr"
    TECHNICAL_SPEC = "technical_spec"      # Renamed from TECHNICAL_SPECIFICATION

    # Deprecated types removed - use new names above

    # Implementation documents
    IMPLEMENTATION_PLAN = "implementation_plan"
    REFACTORING_GUIDE = "refactoring_guide"
    MIGRATION_GUIDE = "migration_guide"
    INTEGRATION_GUIDE = "integration_guide"

    # Testing documents
    TEST_PLAN = "test_plan"
    TEST_REPORT = "test_report"
    COVERAGE_REPORT = "coverage_report"
    VALIDATION_REPORT = "validation_report"

    # Operations documents
    RUNBOOK = "runbook"
    DEPLOYMENT_GUIDE = "deployment_guide"
    MONITORING_GUIDE = "monitoring_guide"
    INCIDENT_REPORT = "incident_report"

    # User-facing documentation
    USER_GUIDE = "user_guide"
    ADMIN_GUIDE = "admin_guide"
    API_DOC = "api_doc"
    DEVELOPER_GUIDE = "developer_guide"
    TROUBLESHOOTING = "troubleshooting"
    FAQ = "faq"

    # Analysis & Research documents (NEW)
    RESEARCH_REPORT = "research_report"
    ANALYSIS_REPORT = "analysis_report"
    INVESTIGATION_REPORT = "investigation_report"
    ASSESSMENT_REPORT = "assessment_report"
    FEASIBILITY_STUDY = "feasibility_study"
    COMPETITIVE_ANALYSIS = "competitive_analysis"

    # Summary documents (NEW)
    SESSION_SUMMARY = "session_summary"
    STATUS_REPORT = "status_report"
    PROGRESS_REPORT = "progress_report"
    MILESTONE_REPORT = "milestone_report"
    RETROSPECTIVE_REPORT = "retrospective_report"

    # Business documents
    BUSINESS_PILLARS = "business_pillars"           # Renamed from BUSINESS_PILLARS_ANALYSIS
    MARKET_RESEARCH = "market_research"             # Renamed from MARKET_RESEARCH_REPORT
    STAKEHOLDER_ANALYSIS = "stakeholder_analysis"
    QUALITY_GATES_SPEC = "quality_gates_spec"       # Renamed from QUALITY_GATES_SPECIFICATION

    # Specification (kept for backward compatibility)
    SPECIFICATION = "specification"

    OTHER = "other"

    @classmethod
    def choices(cls) -> list[str]:
        """Get all enum values for CLI/form dropdowns."""
        return [item.value for item in cls]

    @classmethod
    def from_string(cls, value: str):
        """Safe conversion from string with helpful error message."""
        try:
            return cls(value)
        except ValueError:
            valid = ", ".join(cls.choices())
            raise ValueError(f"Invalid {cls.__name__}: '{value}'. Valid: {valid}")

    @classmethod
    def labels(cls) -> dict[str, str]:
        """Human-readable labels for UI display."""
        return {
            # Planning documents
            cls.IDEA.value: "Idea Document",
            cls.REQUIREMENTS.value: "Requirements Document",
            cls.USER_STORY.value: "User Story",
            cls.USE_CASE.value: "Use Case",

            # Architecture documents
            cls.ARCHITECTURE_DOC.value: "Architecture Document",
            cls.DESIGN_DOC.value: "Design Document",
            cls.ADR.value: "Architecture Decision Record",
            cls.TECHNICAL_SPEC.value: "Technical Specification",

            # Backward compatibility (deprecated)
            cls.ARCHITECTURE.value: "Architecture Document (deprecated - use architecture_doc)",
            cls.DESIGN.value: "Design Document (deprecated - use design_doc)",
            cls.TECHNICAL_SPECIFICATION.value: "Technical Specification (deprecated - use technical_spec)",

            # Implementation documents
            cls.IMPLEMENTATION_PLAN.value: "Implementation Plan",
            cls.REFACTORING_GUIDE.value: "Refactoring Guide",
            cls.MIGRATION_GUIDE.value: "Migration Guide",
            cls.INTEGRATION_GUIDE.value: "Integration Guide",

            # Testing documents
            cls.TEST_PLAN.value: "Test Plan",
            cls.TEST_REPORT.value: "Test Report",
            cls.COVERAGE_REPORT.value: "Coverage Report",
            cls.VALIDATION_REPORT.value: "Validation Report",

            # Operations documents
            cls.RUNBOOK.value: "Runbook",
            cls.DEPLOYMENT_GUIDE.value: "Deployment Guide",
            cls.MONITORING_GUIDE.value: "Monitoring Guide",
            cls.INCIDENT_REPORT.value: "Incident Report",

            # User-facing documentation
            cls.USER_GUIDE.value: "User Guide",
            cls.ADMIN_GUIDE.value: "Admin Guide",
            cls.API_DOC.value: "API Documentation",
            cls.DEVELOPER_GUIDE.value: "Developer Guide",
            cls.TROUBLESHOOTING.value: "Troubleshooting Guide",
            cls.FAQ.value: "Frequently Asked Questions",

            # Analysis & Research documents
            cls.RESEARCH_REPORT.value: "Research Report",
            cls.ANALYSIS_REPORT.value: "Analysis Report",
            cls.INVESTIGATION_REPORT.value: "Investigation Report",
            cls.ASSESSMENT_REPORT.value: "Assessment Report",
            cls.FEASIBILITY_STUDY.value: "Feasibility Study",
            cls.COMPETITIVE_ANALYSIS.value: "Competitive Analysis",

            # Summary documents
            cls.SESSION_SUMMARY.value: "Session Summary",
            cls.STATUS_REPORT.value: "Status Report",
            cls.PROGRESS_REPORT.value: "Progress Report",
            cls.MILESTONE_REPORT.value: "Milestone Report",
            cls.RETROSPECTIVE_REPORT.value: "Retrospective Report",

            # Business documents
            cls.BUSINESS_PILLARS.value: "Business Pillars Analysis",
            cls.MARKET_RESEARCH.value: "Market Research Report",
            cls.STAKEHOLDER_ANALYSIS.value: "Stakeholder Analysis",
            cls.QUALITY_GATES_SPEC.value: "Quality Gates Specification",

            # General
            cls.SPECIFICATION.value: "Specification",
            cls.OTHER.value: "Other Document",
        }


class DocumentFormat(str, Enum):
    """
    Document format for document_references table.
    """
    MARKDOWN = "markdown"
    YAML = "yaml"
    JSON = "json"
    PDF = "pdf"
    HTML = "html"
    DOCX = "docx"
    XLSX = "xlsx"
    PPTX = "pptx"
    TEXT = "text"
    OTHER = "other"

    @classmethod
    def choices(cls) -> list[str]:
        """Get all enum values for CLI/form dropdowns."""
        return [item.value for item in cls]

    @classmethod
    def from_string(cls, value: str):
        """Safe conversion from string with helpful error message."""
        try:
            return cls(value)
        except ValueError:
            valid = ", ".join(cls.choices())
            raise ValueError(f"Invalid {cls.__name__}: '{value}'. Valid: {valid}")


class AgentTier(int, Enum):
    """
    Agent tier classification for agent specialization.

    TIER_1: Universal specialists (work on any project)
    TIER_2: Tech stack specialists (language/framework specific)
    TIER_3: Domain specialists (business domain specific)
    """
    TIER_1 = 1  # Universal (requirements-analyst, code-reviewer, etc.)
    TIER_2 = 2  # Tech-specific (python-implementer, react-developer, etc.)
    TIER_3 = 3  # Domain-specific (healthcare-compliance, finance-security, etc.)

    @classmethod
    def choices(cls) -> list[int]:
        """Get all enum values for CLI/form dropdowns."""
        return [item.value for item in cls]

    @classmethod
    def from_string(cls, value: str):
        """Safe conversion from string with helpful error message."""
        try:
            return cls(int(value))
        except (ValueError, TypeError):
            valid = ", ".join(str(v) for v in cls.choices())
            raise ValueError(f"Invalid {cls.__name__}: '{value}'. Valid: {valid}")


class LearningType(str, Enum):
    """
    Session learning categorization (ADR-003: Sub-Agent Communication).

    Enables cross-agent knowledge sharing via AIPM database.
    AI agents save discoveries during sessions.
    Other agents read these learnings in future sessions.

    Example workflow:
      Session 1 (Claude): Discovers "Use JWT pattern" → saves as PATTERN
      Session 2 (Cursor): Loads patterns → sees JWT → implements consistently
      Result: Zero knowledge loss between sessions and agents

    Usage:
      apm session update --learning-type=decision --content="Use PostgreSQL"
      apm session update --learning-type=pattern --content="ServiceLayer for logic"
    """
    DECISION = "decision"        # Architectural or implementation decision
    PATTERN = "pattern"          # Code pattern discovered
    DISCOVERY = "discovery"      # System insight
    CONSTRAINT = "constraint"    # Limitation identified
    ANTIPATTERN = "antipattern"  # Pattern to avoid
    OPTIMIZATION = "optimization"  # Performance improvement
    SECURITY = "security"        # Security consideration
    INTEGRATION = "integration"  # Integration insight
    BEST_PRACTICE = "best_practice"  # Team standard

    @classmethod
    def choices(cls) -> list[str]:
        """Get all enum values for CLI/form dropdowns."""
        return [item.value for item in cls]

    @classmethod
    def from_string(cls, value: str):
        """Safe conversion from string with helpful error message."""
        try:
            return cls(value)
        except ValueError:
            valid = ", ".join(cls.choices())
            raise ValueError(f"Invalid {cls.__name__}: '{value}'. Valid: {valid}")


class RiskLevel(str, Enum):
    """
    Risk classification for human review workflow (ADR-007).

    Determines if human approval required before AI proceeds.
    Based on automated risk scoring algorithm (impact × reversibility × cost).

    Thresholds:
    - LOW (0.0-0.3): Auto-approve, AI proceeds immediately
    - MEDIUM (0.3-0.7): Peer review recommended but optional
    - HIGH (0.7-0.9): Senior review required, work blocked until approval
    - CRITICAL (0.9-1.0): Executive review required, work blocked

    Example:
      Decision: "Switch from PostgreSQL to MongoDB"
      Risk Factors: Architecture change (0.9), High cost (0.8), Hard to reverse (0.9)
      Risk Score: 0.95 → CRITICAL → Requires executive review
    """
    LOW = "low"          # <0.3 score, auto-approve
    MEDIUM = "medium"    # 0.3-0.7, peer review
    HIGH = "high"        # 0.7-0.9, senior review required
    CRITICAL = "critical"  # 0.9-1.0, executive review required

    @classmethod
    def from_score(cls, score: float) -> 'RiskLevel':
        """
        Convert risk score to risk level.

        Args:
            score: Risk score (0.0-1.0)

        Returns:
            Appropriate risk level for review routing
        """
        if score < 0.3:
            return cls.LOW
        elif score < 0.7:
            return cls.MEDIUM
        elif score < 0.9:
            return cls.HIGH
        else:
            return cls.CRITICAL

    @classmethod
    def choices(cls) -> list[str]:
        """Get all enum values for CLI/form dropdowns."""
        return [item.value for item in cls]

    @classmethod
    def from_string(cls, value: str):
        """Safe conversion from string with helpful error message."""
        try:
            return cls(value)
        except ValueError:
            valid = ", ".join(cls.choices())
            raise ValueError(f"Invalid {cls.__name__}: '{value}'. Valid: {valid}")


class ReviewStatus(str, Enum):
    """
    Human review request status (ADR-007: Human-in-the-Loop).

    Tracks review lifecycle from request through resolution.
    Includes SLA management and escalation handling.
    """
    PENDING = "pending"              # Awaiting review assignment
    UNDER_REVIEW = "under_review"    # Actively being reviewed
    APPROVED = "approved"            # Approved, work can proceed
    REJECTED = "rejected"            # Rejected, work blocked or revised
    ESCALATED = "escalated"          # Escalated to higher authority
    EXPIRED = "expired"              # SLA deadline passed
    CANCELLED = "cancelled"          # Review no longer needed

    @classmethod
    def choices(cls) -> list[str]:
        """Get all enum values for CLI/form dropdowns."""
        return [item.value for item in cls]

    @classmethod
    def from_string(cls, value: str):
        """Safe conversion from string with helpful error message."""
        try:
            return cls(value)
        except ValueError:
            valid = ", ".join(cls.choices())
            raise ValueError(f"Invalid {cls.__name__}: '{value}'. Valid: {valid}")


class DependencyType(str, Enum):
    """
    Task dependency types (ADR-010: Dependency Management).

    PMBOK standard dependency relationships for project scheduling.
    Enables critical path calculation and intelligent task ordering.

    Statistics: 90% of dependencies are FINISH_TO_START
    """
    FINISH_TO_START = "finish_to_start"  # A finishes → B starts (most common)
    START_TO_START = "start_to_start"    # A starts → B can start (parallel)
    FINISH_TO_FINISH = "finish_to_finish"  # A finishes → B finishes (synchronized)
    START_TO_FINISH = "start_to_finish"  # A starts → B finishes (rare, <1%)

    @classmethod
    def choices(cls) -> list[str]:
        """Get all enum values for CLI/form dropdowns."""
        return [item.value for item in cls]

    @classmethod
    def from_string(cls, value: str):
        """Safe conversion from string with helpful error message."""
        try:
            return cls(value)
        except ValueError:
            valid = ", ".join(cls.choices())
            raise ValueError(f"Invalid {cls.__name__}: '{value}'. Valid: {valid}")


class CacheStrategy(str, Enum):
    """
    Context caching strategy (ADR-002: Context Compression).

    Balances performance (fast context) vs freshness (up-to-date).

    MVP: DISABLED (simplest, no cache invalidation complexity)
    Phase 2: MODERATE (good balance for production use)
    Performance: AGGRESSIVE (when speed critical)
    """
    AGGRESSIVE = "aggressive"    # 1-hour TTL, maximum performance
    MODERATE = "moderate"        # 30-minute TTL, balanced
    CONSERVATIVE = "conservative"  # 15-minute TTL, maximum freshness
    DISABLED = "disabled"        # No caching (MVP default)

    @classmethod
    def choices(cls) -> list[str]:
        """Get all enum values for CLI/form dropdowns."""
        return [item.value for item in cls]

    @classmethod
    def from_string(cls, value: str):
        """Safe conversion from string with helpful error message."""
        try:
            return cls(value)
        except ValueError:
            valid = ", ".join(cls.choices())
            raise ValueError(f"Invalid {cls.__name__}: '{value}'. Valid: {valid}")


class DocumentStatus(str, Enum):
    """
    Document lifecycle status (ADR-006: Document Store).

    Tracks document maturity and currency for search and context.
    Enables document version management and supersession tracking.
    """
    DRAFT = "draft"          # Work in progress, not ready for use
    REVIEW = "review"        # Ready for review
    APPROVED = "approved"    # Approved and current
    SUPERSEDED = "superseded"  # Replaced by newer version
    ARCHIVED = "archived"    # Historical only, not active

    @classmethod
    def choices(cls) -> list[str]:
        """Get all enum values for CLI/form dropdowns."""
        return [item.value for item in cls]

    @classmethod
    def from_string(cls, value: str):
        """Safe conversion from string with helpful error message."""
        try:
            return cls(value)
        except ValueError:
            valid = ", ".join(cls.choices())
            raise ValueError(f"Invalid {cls.__name__}: '{value}'. Valid: {valid}")


class EvidenceStatus(str, Enum):
    """
    Evidence verification status (ADR-004: Evidence Storage).

    Tracks if evidence sources are still valid and accessible.
    Used for evidence quality assessment and credibility.

    Verification schedule:
    - VERIFIED: Checked within 30 days
    - STALE: Not verified in 30+ days
    - BROKEN: Source inaccessible or content changed
    """
    VERIFIED = "verified"    # Recently verified, content valid
    STALE = "stale"          # Not verified in 30+ days
    BROKEN = "broken"        # Source inaccessible or changed
    UNVERIFIED = "unverified"  # Never verified

    @classmethod
    def choices(cls) -> list[str]:
        """Get all enum values for CLI/form dropdowns."""
        return [item.value for item in cls]

    @classmethod
    def from_string(cls, value: str):
        """Safe conversion from string with helpful error message."""
        try:
            return cls(value)
        except ValueError:
            valid = ", ".join(cls.choices())
            raise ValueError(f"Invalid {cls.__name__}: '{value}'. Valid: {valid}")


class NotificationChannel(str, Enum):
    """
    Notification delivery channels (ADR-009: Event System).

    Where to send alerts, review requests, and status updates.
    Used for human review notifications, budget warnings, etc.
    """
    EMAIL = "email"          # Email notification
    SLACK = "slack"          # Slack message
    CLI = "cli"              # CLI output/alert
    WEBHOOK = "webhook"      # HTTP webhook POST
    NONE = "none"            # No notification (silent)

    @classmethod
    def choices(cls) -> list[str]:
        """Get all enum values for CLI/form dropdowns."""
        return [item.value for item in cls]

    @classmethod
    def from_string(cls, value: str):
        """Safe conversion from string with helpful error message."""
        try:
            return cls(value)
        except ValueError:
            valid = ", ".join(cls.choices())
            raise ValueError(f"Invalid {cls.__name__}: '{value}'. Valid: {valid}")


class SummaryType(str, Enum):
    """
    Summary types for hierarchical summary system.
    
    Supports summaries at all levels of the APM (Agent Project Manager) hierarchy:
    - Project summaries (strategic, milestone, retrospective)
    - Session summaries (handover, progress, error analysis)
    - Work item summaries (progress, milestone, decision)
    - Task summaries (completion, progress, blocker resolution)
    """
    
    # Project-level summaries
    PROJECT_MILESTONE = "project_milestone"
    PROJECT_RETROSPECTIVE = "project_retrospective"
    PROJECT_STATUS_REPORT = "project_status_report"
    PROJECT_STRATEGIC_REVIEW = "project_strategic_review"
    
    # Session-level summaries
    SESSION_HANDOVER = "session_handover"
    SESSION_PROGRESS = "session_progress"
    SESSION_ERROR_ANALYSIS = "session_error_analysis"
    SESSION_DECISION_LOG = "session_decision_log"
    
    # Work item-level summaries
    WORK_ITEM_PROGRESS = "work_item_progress"
    WORK_ITEM_MILESTONE = "work_item_milestone"
    WORK_ITEM_DECISION = "work_item_decision"
    WORK_ITEM_RETROSPECTIVE = "work_item_retrospective"
    
    # Task-level summaries
    TASK_COMPLETION = "task_completion"
    TASK_PROGRESS = "task_progress"
    TASK_BLOCKER_RESOLUTION = "task_blocker_resolution"
    TASK_TECHNICAL_NOTES = "task_technical_notes"
    
    # Legacy support (for migration from work_item_summaries)
    SESSION = "session"  # Maps to SESSION_HANDOVER
    MILESTONE = "milestone"  # Maps to WORK_ITEM_MILESTONE
    DECISION = "decision"  # Maps to WORK_ITEM_DECISION
    RETROSPECTIVE = "retrospective"  # Maps to WORK_ITEM_RETROSPECTIVE

    @classmethod
    def choices(cls) -> list[str]:
        """Get all enum values for CLI/form dropdowns."""
        return [item.value for item in cls]

    @classmethod
    def from_string(cls, value: str):
        """Safe conversion from string with helpful error message."""
        try:
            return cls(value)
        except ValueError:
            valid = ", ".join(cls.choices())
            raise ValueError(f"Invalid {cls.__name__}: '{value}'. Valid: {valid}")

    @classmethod
    def labels(cls) -> dict[str, str]:
        """Human-readable labels for UI display."""
        return {
            # Project-level
            cls.PROJECT_MILESTONE.value: "Project Milestone - Major project milestone achieved",
            cls.PROJECT_RETROSPECTIVE.value: "Project Retrospective - Project reflection and lessons learned",
            cls.PROJECT_STATUS_REPORT.value: "Project Status Report - Current project status and progress",
            cls.PROJECT_STRATEGIC_REVIEW.value: "Project Strategic Review - Strategic project review and direction",
            
            # Session-level
            cls.SESSION_HANDOVER.value: "Session Handover - Session completion and handover notes",
            cls.SESSION_PROGRESS.value: "Session Progress - Progress made during session",
            cls.SESSION_ERROR_ANALYSIS.value: "Session Error Analysis - Errors encountered and resolved",
            cls.SESSION_DECISION_LOG.value: "Session Decision Log - Decisions made during session",
            
            # Work item-level
            cls.WORK_ITEM_PROGRESS.value: "Work Item Progress - Progress on work item",
            cls.WORK_ITEM_MILESTONE.value: "Work Item Milestone - Work item milestone achieved",
            cls.WORK_ITEM_DECISION.value: "Work Item Decision - Decision made for work item",
            cls.WORK_ITEM_RETROSPECTIVE.value: "Work Item Retrospective - Work item reflection and lessons",
            
            # Task-level
            cls.TASK_COMPLETION.value: "Task Completion - Task completed successfully",
            cls.TASK_PROGRESS.value: "Task Progress - Progress made on task",
            cls.TASK_BLOCKER_RESOLUTION.value: "Task Blocker Resolution - Blocker resolved for task",
            cls.TASK_TECHNICAL_NOTES.value: "Task Technical Notes - Technical notes and implementation details",
            
            # Legacy
            cls.SESSION.value: "Session - Session summary (legacy)",
            cls.MILESTONE.value: "Milestone - Milestone summary (legacy)",
            cls.DECISION.value: "Decision - Decision summary (legacy)",
            cls.RETROSPECTIVE.value: "Retrospective - Retrospective summary (legacy)",
        }

    @classmethod
    def get_appropriate_types(cls, entity_type: 'EntityType') -> list['SummaryType']:
        """Get summary types appropriate for specific entity types."""
        if entity_type == EntityType.PROJECT:
            return [
                cls.PROJECT_MILESTONE,
                cls.PROJECT_RETROSPECTIVE,
                cls.PROJECT_STATUS_REPORT,
                cls.PROJECT_STRATEGIC_REVIEW,
            ]
        elif entity_type == EntityType.WORK_ITEM:
            return [
                cls.WORK_ITEM_PROGRESS,
                cls.WORK_ITEM_MILESTONE,
                cls.WORK_ITEM_DECISION,
                cls.WORK_ITEM_RETROSPECTIVE,
                # Legacy support
                cls.SESSION,
                cls.MILESTONE,
                cls.DECISION,
                cls.RETROSPECTIVE,
            ]
        elif entity_type == EntityType.TASK:
            return [
                cls.TASK_COMPLETION,
                cls.TASK_PROGRESS,
                cls.TASK_BLOCKER_RESOLUTION,
                cls.TASK_TECHNICAL_NOTES,
            ]
        else:
            # For other entity types, return all types
            return list(cls)


class SearchResultType(str, Enum):
    """
    Search result types for unified search system.

    Categorizes search results by the type of content found.
    """

    # Entity results
    WORK_ITEM = "work_item"
    TASK = "task"
    IDEA = "idea"
    DOCUMENT = "document"
    SUMMARY = "summary"
    EVIDENCE = "evidence"
    LEARNING = "learning"
    SESSION = "session"

    # Content results
    CONTENT_MATCH = "content_match"
    METADATA_MATCH = "metadata_match"
    TAG_MATCH = "tag_match"
    RELATIONSHIP_MATCH = "relationship_match"

    @classmethod
    def choices(cls) -> list[str]:
        """Get all enum values for CLI/form dropdowns."""
        return [item.value for item in cls]


class StorageMode(str, Enum):
    """
    Document storage strategy for hybrid storage system (WI-133).

    Controls where document content is stored and how it's synchronized:
    - DATABASE_ONLY: Content only in database, no file written
    - FILE_ONLY: Content only in file, database stores metadata only
    - HYBRID: Database is source of truth, file is synchronized cache (default)

    Hybrid mode benefits:
    - Database: Query, search, version control, backup
    - Files: Git diffs, IDE editing, markdown preview
    - Sync: Automatic bidirectional synchronization

    Migration 0039
    """
    DATABASE_ONLY = "database_only"  # No file, database only
    FILE_ONLY = "file_only"          # No content in DB, file only
    HYBRID = "hybrid"                # Both (database is source of truth)

    @classmethod
    def choices(cls) -> list[str]:
        """Get all enum values for CLI/form dropdowns."""
        return [item.value for item in cls]

    @classmethod
    def from_string(cls, value: str):
        """Safe conversion from string with helpful error message."""
        try:
            return cls(value)
        except ValueError:
            valid = ", ".join(cls.choices())
            raise ValueError(f"Invalid {cls.__name__}: '{value}'. Valid: {valid}")


class SyncStatus(str, Enum):
    """
    Document synchronization status for hybrid storage (WI-133).

    Tracks sync state between database content and filesystem:
    - SYNCED: Database and file are in sync
    - PENDING: Database updated, file needs sync
    - CONFLICT: Both database and file modified independently
    - ERROR: Sync failed, manual intervention needed

    Sync workflow:
    1. User updates document via CLI → database updated, status=PENDING
    2. Sync daemon runs → writes file, status=SYNCED
    3. User edits file in IDE → file watcher detects → database updated, status=SYNCED
    4. Conflict detection → both modified → status=CONFLICT (user resolves)

    Migration 0039
    """
    SYNCED = "synced"      # Database and file match
    PENDING = "pending"    # Database updated, file needs sync
    CONFLICT = "conflict"  # Both modified independently
    ERROR = "error"        # Sync failed

    @classmethod
    def choices(cls) -> list[str]:
        """Get all enum values for CLI/form dropdowns."""
        return [item.value for item in cls]

    @classmethod
    def from_string(cls, value: str):
        """Safe conversion from string with helpful error message."""
        try:
            return cls(value)
        except ValueError:
            valid = ", ".join(cls.choices())
            raise ValueError(f"Invalid {cls.__name__}: '{value}'. Valid: {valid}")
