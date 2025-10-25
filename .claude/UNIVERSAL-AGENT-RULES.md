# Universal Agent Rules

**1. ALWAYS Use `apm` Commands for All Project Management Tasks**

*   **MUST NOT** directly interact with the AIPM database.
*   **MUST** use the `apm` command-line tool for all project management tasks, including creating, updating, and managing work items, tasks, documents, and summaries.

**2. ALWAYS Follow the Correct Workflow**

*   **MUST** ensure that a work item is in the `active` state before starting a task.
*   **MUST** ensure that a task is in the `active` state before starting to work on it.
*   **MUST** use the `apm work-item next <id>` and `apm task next <id>` commands to move work items and tasks through their respective workflows.

**3. ALWAYS Document Everything**

*   **MUST** create a document for all significant work, including design documents, technical specifications, and user guides.
*   **MUST** follow the project's documentation location rules.
*   **MUST** use the `apm document add` command to add all documents to the AIPM database.

**4. ALWAYS Create Summaries for Key Information**

*   **MUST** create a summary for all completed tasks, work items, and other significant events.
*   **MUST** use the `apm summary create` command to add all summaries to the AIPM database.

**5. ALWAYS Run Multiple Agents in Parallel Where Possible**

*   **MUST** identify opportunities to run agents in parallel to speed up the development process.
*   **MUST** use the appropriate tools and techniques to manage parallel agent execution.

**6. ALWAYS Adhere to Quality Gates**

*   **MUST** ensure that all work meets the project's quality gates before it is submitted for review.
*   **MUST** use the `apm work-item validate` and `apm task validate` commands to check the quality gates for work items and tasks.

**7. ALWAYS Keep the System Up-to-Date**

*   **MUST** run the `apm migrate` command regularly to ensure that the database is up-to-date with the latest schema changes.