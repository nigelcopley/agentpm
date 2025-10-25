# AIPM Agent Development Guidelines

## 1. Core Mandate: The Anti-Accumulation Philosophy

Your primary directive is to prevent technical debt and maintain a clean, lean codebase. You must strictly adhere to the following principles:

*   **REPLACE, DON'T ADD:** When implementing new features or logic, your first instinct must be to refactor or replace existing code. Avoid adding redundant logic.
*   **DELETE, DON'T ARCHIVE:** Aggressively remove obsolete code, files, and features. The Git history is the only sanctioned archive. You are forbidden from creating legacy directories (e.g., `_v1`, `_old`, `_backup`).
*   **CONSOLIDATE, DON'T DUPLICATE:** Maintain a zero-tolerance policy for code duplication. Always abstract and reuse common functionality.
*   **SINGLE SOURCE OF TRUTH (SSOT):** Ensure every piece of data, configuration, and logic has one, and only one, authoritative source.

## 2. Proactive Engagement & Responsibility

*   **Always Ask "What Should I Remove?":** When adding any new code, you are required to ask the user what existing code, files, or logic can be removed or superseded by your changes.
*   **Proactively Identify and Refactor:** You must actively identify code that violates the Anti-Accumulation Philosophy or other project standards and propose a refactoring plan to the user.
*   **Reject Low-Quality Requests:** If a user request would lead to a violation of these guidelines (e.g., creating duplicate logic, adding code without tests), you must refuse the request and explain why, offering a better, compliant alternative.

## 3. Architecture & Design

*   **Adhere to Service-Oriented Clean Architecture:** All changes must respect the strict separation of concerns between the Presentation, Service Orchestrator, Business Services, and Infrastructure layers.
*   **Use the Service Orchestrator:** All business operations must be routed through the central Service Orchestrator. Do not bypass it to interact directly with lower-level services.
*   **Leverage Existing Services:** Before writing any new code, you must thoroughly inspect the existing services in `agentpm/core/services/` to determine if the required functionality already exists.
*   **Extend via Plugins:** For technology-specific intelligence (e.g., framework detection, language-specific analysis), you must create a new plugin that inherits from `BasePlugin` and is registered with the plugin system.

## 4. Development, Quality, and Style

*   **Test-Driven Development is Mandatory:** All new features, bug fixes, or refactors must be accompanied by comprehensive `pytest` tests. Your changes are not complete until the tests are written and passing.
*   **Mimic Existing Code:** Your contributions must be stylistically and structurally indistinguishable from the surrounding code. This includes:
    *   **Formatting:** Adhere to `black` formatting.
    *   **Typing:** Use `Pydantic` models for all data structures.
    *   **Naming Conventions:** Follow existing patterns for variables, functions, classes, and modules.
*   **Comprehensive Docstrings:** All new or modified functions, classes, and modules must have clear, complete docstrings that explain their purpose, arguments, return values, and any exceptions raised.
*   **Dependency Management:** All new dependencies for the `aipm-cli` must be added and managed via the `pyproject.toml` file using Poetry.

## 5. Prohibited Actions

*   **No Direct Database Interaction:** You are forbidden from interacting directly with the SQLite database. All database operations must go through the `DatabaseService`.
*   **No Bypassing Architectural Layers:** Direct calls from the presentation layer (e.g., CLI commands) to infrastructure or business services are strictly prohibited.
*   **Do Not Introduce Unmanaged State:** All application state should be managed explicitly through the defined services and data models.
