# Gemini Context for AIPM Project

This document provides a comprehensive overview of the Agent Project Manager (APM) project, its architecture, development practices, and how to interact with it. This context is generated for Gemini to facilitate effective understanding and interaction with the codebase.

## Project Overview

The AIPM is a local-first, AI-powered project management system designed to enhance project intelligence and automate workflows. It primarily consists of a Python-based Command-Line Interface (CLI). The system leverages a "6W Intelligence Framework" (What, Where, Why, When, Who, How) to provide deep insights and automation.

**Key Features:**
*   **AI-Powered Project Management:** Intelligent insights for project analysis, objective processing, task planning, and agent coordination.
*   **6W Intelligence Framework:** Core services for Objective Intelligence, Context Enhancement (Tech Detection), SOP Intelligence, Task Routing/Planning, Agent Intelligence/Assignment, and Workflow Intelligence.
*   **Local-First Architecture:** Ensures data privacy and offline capability, primarily using SQLite for storage.
*   **CLI Interface:** The main user interaction point (`apm` command).
*   **Extensible Plugin System:** Framework-agnostic architecture allowing for technology-specific intelligence.
*   **Modular Database Architecture:** Specialized database services with file-based migrations.
*   **Anti-Accumulation Development Rules:** Strict guidelines to prevent technical debt and maintain a clean codebase.

## Architecture and Technologies

The APM project adheres to a **Service-Oriented Clean Architecture** with a strong emphasis on modularity, separation of concerns, and event-driven design.

**Core Components:**
*   **`agentpm` (Python):**
    *   **CLI Framework:** `click` for command-line interface.
    *   **Data Modeling:** `Pydantic` for robust, type-safe data models.
    *   **Database:** `SQLite` for local data persistence.
    *   **Rich Output:** `rich` library for enhanced terminal output.
    *   **Service Orchestrator:** Central component routing all business operations, handling caching and cross-cutting concerns.
    *   **Plugin System:** A highly extensible, performance-monitored system for technology detection and intelligence.
    *   **Anti-Accumulation Enforcement:** Pre-commit hooks and health checks to enforce development rules.

**Architectural Layers:**
1.  **Presentation Layer:** Thin adapters (CLI) that interact with the Service Orchestrator.
2.  **Service Orchestrator Layer:** Single entry point for business operations, managing command routing, validation, caching, and cross-cutting concerns.
3.  **Business Services Layer:** Dedicated services for core business logic (e.g., Objective Intelligence, Context Enhancer, SOP Intelligence), located in `agentpm/core`.
4.  **Infrastructure Layer:** Handles external dependencies (Database, File System, External APIs).
5.  **Plugin System:** Provides framework-agnostic extensibility for technology-specific intelligence.

## Building and Running

**Installation (using pip):**
```bash
pip install -e .
```

**Running CLI Commands:**
*   **Global Commands (outside a project):**
    ```bash
    apm init "My New Project" -p .
    apm status
    ```
*   **Project-Specific Commands (inside an initialized project directory):**
    ```bash
    apm work-item create "Add User Authentication" --type feature
    apm task create "Design auth schema" --type design --effort 3h
    apm context 123
    ```

**Testing:**
The project uses `pytest`.
```bash
# Run all tests
python -m pytest tests/ -v

# Test specific module
python -m pytest tests/core/database/ -v
python -m pytest tests/core/plugins/ -v

# With coverage
python -m pytest tests/ --cov=agentpm --cov-report=html
```

## Development Conventions

*   **Anti-Accumulation Rules:** Strict adherence to "REPLACE, DON'T ADD," "DELETE, DON'T ARCHIVE," "CONSOLIDATE, DON'T DUPLICATE," and "SINGLE SOURCE OF TRUTH." Git history is the primary archive.
*   **AI Assistant Behavior:** AI agents are mandated to proactively identify and remove superseded code, refuse to create legacy directories, and always ask "What should I remove?" when adding new code.
*   **Docstring Standards:** Comprehensive docstrings are expected.
*   **Code Quality:** Enforced through tools like `black`, `ruff`, and `mypy`.
*   **Testing:** Multi-layered testing approach (unit, integration, system, performance, compliance) using `pytest`.
*   **Modular Design:** Clear separation of concerns across services, plugins, and database interactions.

## Key Files and Directories

*   `/README.md`: Main project documentation overview.
*   `/pyproject.toml`: Project metadata and Python dependencies.
*   `/agentpm/cli/main.py`: Main CLI entry point, handles global and project-specific command routing.
*   `/agentpm/core/`: Contains modular business logic services.
*   `/agentpm/core/database/`: Unified database service for SQLite interactions.
*   `/agentpm/core/plugins/`: Defines the core plugin architecture and registry.
*   `/pytest.ini`: `pytest` configuration for testing.

---
*This `GEMINI.md` was generated by Gemini based on an analysis of the project directory and its documentation.*