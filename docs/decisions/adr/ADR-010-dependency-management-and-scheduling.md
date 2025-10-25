# ADR-010: Dependency Management and Scheduling

**Status:** Proposed
**Date:** 2025-10-12
**Deciders:** AIPM Core Team
**Technical Story:** Track task dependencies, detect critical paths, enable intelligent scheduling

---

## Context

### The Dependency Problem

Complex projects have intricate task dependencies:

**Example: Multi-Tenant Platform**
```
Authentication System (Work Item #5)
├─ Task 1: Database schema (4h)
│  └─ MUST complete before Task 2
│
├─ Task 2: User model implementation (4h)
│  └─ DEPENDS ON: Task 1
│  └─ MUST complete before Task 3, 4
│
├─ Task 3: JWT middleware (4h)
│  └─ DEPENDS ON: Task 2
│
├─ Task 4: Login endpoint (3h)
│  └─ DEPENDS ON: Task 2
│
└─ Task 5: Integration tests (6h)
   └─ DEPENDS ON: All above tasks

Critical Path: 1 → 2 → 3 → 5 (17 hours)
Parallelizable: Task 3 and 4 (after Task 2)
```

**Current Problems:**

1. **No Dependency Tracking**
   ```
   AI agent starts Task 3 (JWT middleware)
   ├─ Requires User model (Task 2)
   ├─ But Task 2 not complete yet ❌
   ├─ Agent fails or creates wrong implementation
   └─ Wasted effort, must redo
   ```

2. **No Critical Path Analysis**
   ```
   5 tasks, total 21 hours of work
   ├─ Sequential: 21 hours (if done one-by-one)
   ├─ Critical path: 17 hours (optimal with parallelization)
   ├─ Current: No visibility into optimal order
   └─ Inefficient scheduling
   ```

3. **No Blocking Detection**
   ```
   Task 2 blocked (waiting for review)
   ├─ Tasks 3, 4, 5 all depend on Task 2
   ├─ No automatic detection of downstream impact
   ├─ Agents start dependent tasks and fail
   └─ No alert that critical path is blocked
   ```

### Requirements

1. **Explicit Dependencies**: Declare "Task B depends on Task A"
2. **Dependency Validation**: Prevent circular dependencies
3. **Critical Path Calculation**: Identify longest path to completion
4. **Intelligent Scheduling**: Suggest optimal task order
5. **Blocking Detection**: Alert when dependencies block downstream work
6. **Automatic Readiness**: Mark tasks "ready to start" when dependencies complete

---

## Decision

We will implement a **Dependency Management and Scheduling System** with:

1. **Dependency Graph**: Directed acyclic graph (DAG) of task dependencies
2. **Critical Path Analysis**: Calculate critical path through project
3. **Task Readiness**: Auto-detect when task dependencies are met
4. **Blocking Alerts**: Notify when critical path is blocked
5. **Intelligent Scheduling**: Suggest optimal task execution order

### Architecture

```
┌──────────────────────────────────────────────────────────┐
│                  Dependency System                        │
│                                                          │
│  ┌────────────────────────────────────────────────────┐ │
│  │ Dependency Graph (DAG)                             │ │
│  │                                                    │ │
│  │   Task 1 (schema)                                  │ │
│  │      │                                             │ │
│  │      └──→ Task 2 (model)                           │ │
│  │            │    \                                   │ │
│  │            │     \                                  │ │
│  │            ▼      ▼                                 │ │
│  │         Task 3  Task 4                             │ │
│  │         (JWT)   (login)                            │ │
│  │            │      │                                 │ │
│  │            └──┬───┘                                 │ │
│  │               │                                     │ │
│  │               ▼                                     │ │
│  │           Task 5 (tests)                           │ │
│  │                                                    │ │
│  │  Critical Path: 1 → 2 → 3 → 5 (17h)               │ │
│  │  Parallelizable: 3 ∥ 4 (after 2)                  │ │
│  └────────────────────────────────────────────────────┘ │
│                                                          │
│  ┌────────────────────────────────────────────────────┐ │
│  │ Scheduling Engine                                  │ │
│  │                                                    │ │
│  │  • Calculate critical path                         │ │
│  │  • Detect parallelization opportunities           │ │
│  │  • Suggest optimal task order                     │ │
│  │  • Auto-mark tasks "ready" when deps complete     │ │
│  │  • Alert when critical path blocked               │ │
│  └────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────┘
```

### Dependency Model

```python
@dataclass
class TaskDependency:
    """
    Declares that one task depends on another.

    Types:
    - finish_to_start: Task B starts after Task A finishes (most common)
    - start_to_start: Task B starts when Task A starts (parallel work)
    - finish_to_finish: Task B finishes when Task A finishes
    - start_to_finish: Task B finishes when Task A starts (rare)
    """

    id: str
    dependent_task_id: int  # Task that depends
    prerequisite_task_id: int  # Task that must complete first
    dependency_type: Literal[
        "finish_to_start",  # A finishes → B starts
        "start_to_start",   # A starts → B starts
        "finish_to_finish", # A finishes → B finishes
        "start_to_finish"   # A starts → B finishes
    ]
    lag: Optional[timedelta]  # Optional delay (e.g., 1 day after completion)
    mandatory: bool  # True = hard dependency, False = soft/recommended

    created_at: datetime
    created_by: str

class DependencyGraphService:
    """
    Build and analyze dependency graphs.
    """

    def add_dependency(
        self,
        dependent_task_id: int,
        prerequisite_task_id: int,
        dependency_type: str = "finish_to_start",
        mandatory: bool = True
    ) -> TaskDependency:
        """
        Add dependency between tasks.

        Validates:
        - No circular dependencies
        - Both tasks in same work item
        - Prerequisite task exists
        """

        # Validate no circular dependency
        if self._creates_cycle(dependent_task_id, prerequisite_task_id):
            raise CircularDependencyError(
                f"Cannot add dependency: would create cycle"
            )

        dependency = TaskDependency(
            id=generate_uuid(),
            dependent_task_id=dependent_task_id,
            prerequisite_task_id=prerequisite_task_id,
            dependency_type=dependency_type,
            mandatory=mandatory,
            created_at=datetime.now(),
            created_by=get_current_agent()
        )

        db.add(dependency)
        db.commit()

        # Recalculate task readiness
        self._update_task_readiness(dependent_task_id)

        return dependency

    def _creates_cycle(self, from_task: int, to_task: int) -> bool:
        """
        Check if adding dependency creates cycle.

        Uses depth-first search to detect cycles.
        """

        visited = set()
        stack = [to_task]

        while stack:
            current = stack.pop()

            if current == from_task:
                return True  # Cycle detected

            if current in visited:
                continue

            visited.add(current)

            # Get all prerequisites of current task
            prerequisites = db.query(TaskDependency).filter(
                TaskDependency.dependent_task_id == current
            ).all()

            for prereq in prerequisites:
                stack.append(prereq.prerequisite_task_id)

        return False  # No cycle

    def get_dependency_graph(self, work_item_id: int) -> DependencyGraph:
        """
        Get complete dependency graph for work item.

        Returns: Graph with nodes (tasks) and edges (dependencies)
        """

        tasks = db.query(Task).filter(
            Task.work_item_id == work_item_id
        ).all()

        dependencies = db.query(TaskDependency).join(Task).filter(
            Task.work_item_id == work_item_id
        ).all()

        return DependencyGraph(
            nodes=[TaskNode(t.id, t.title, t.status, t.effort) for t in tasks],
            edges=[DependencyEdge(d.prerequisite_task_id, d.dependent_task_id, d.dependency_type) for d in dependencies]
        )
```

### Critical Path Analysis

```python
class CriticalPathAnalyzer:
    """
    Calculate critical path through project.

    Critical path = longest path from start to finish.
    Determines minimum project duration.
    """

    def calculate_critical_path(self, work_item_id: int) -> CriticalPath:
        """
        Find critical path using forward/backward pass algorithm.

        Returns:
        - Critical tasks (tasks on critical path)
        - Project duration (minimum time to complete)
        - Slack time per task (how much delay tolerable)
        - Parallelization opportunities
        """

        graph = dependency_service.get_dependency_graph(work_item_id)

        # Forward pass: Calculate earliest start/finish
        earliest_start = {}
        earliest_finish = {}

        for node in graph.topological_sort():
            # Earliest start = max(predecessors' earliest finish)
            predecessors = graph.get_predecessors(node.id)

            if not predecessors:
                earliest_start[node.id] = 0  # Start task
            else:
                earliest_start[node.id] = max(
                    earliest_finish.get(pred, 0)
                    for pred in predecessors
                )

            earliest_finish[node.id] = earliest_start[node.id] + node.effort

        # Project duration = max earliest finish
        project_duration = max(earliest_finish.values())

        # Backward pass: Calculate latest start/finish
        latest_start = {}
        latest_finish = {}

        for node in reversed(graph.topological_sort()):
            successors = graph.get_successors(node.id)

            if not successors:
                latest_finish[node.id] = project_duration  # End task
            else:
                latest_finish[node.id] = min(
                    latest_start.get(succ, project_duration)
                    for succ in successors
                )

            latest_start[node.id] = latest_finish[node.id] - node.effort

        # Calculate slack (float)
        slack = {
            node_id: latest_start[node_id] - earliest_start[node_id]
            for node_id in earliest_start
        }

        # Critical path = tasks with zero slack
        critical_tasks = [
            node_id for node_id, slack_time in slack.items()
            if slack_time == 0
        ]

        return CriticalPath(
            tasks=critical_tasks,
            duration=project_duration,
            slack=slack,
            parallelization_opportunities=self._find_parallel_tasks(graph, slack)
        )

    def _find_parallel_tasks(self, graph: DependencyGraph, slack: Dict) -> List[List[int]]:
        """
        Find tasks that can run in parallel.

        Returns: List of task groups that can run simultaneously
        """

        parallel_groups = []

        # Group tasks by earliest start time
        by_start_time = {}
        for node in graph.nodes:
            start = earliest_start[node.id]
            if start not in by_start_time:
                by_start_time[start] = []
            by_start_time[start].append(node.id)

        # Groups with >1 task can run in parallel
        for start_time, tasks in by_start_time.items():
            if len(tasks) > 1:
                parallel_groups.append(tasks)

        return parallel_groups
```

### Intelligent Scheduling

```python
class TaskScheduler:
    """
    Suggest optimal task execution order.
    """

    def get_next_tasks(self, work_item_id: int, agent_id: Optional[str] = None) -> List[Task]:
        """
        Get tasks that are ready to start.

        Ready = All dependencies done + status is READY

        Sorted by:
        1. Priority (high priority first)
        2. Critical path (critical tasks first)
        3. Slack time (zero slack first)
        4. Effort (shorter tasks first for quick wins)
        """

        # Get all ACCEPTED tasks
        tasks = db.query(Task).filter(
            Task.work_item_id == work_item_id,
            Task.status == "ACCEPTED"
        ).all()

        # Filter to ready tasks (dependencies met)
        ready_tasks = []
        for task in tasks:
            if self._are_dependencies_met(task.id):
                ready_tasks.append(task)

        if not ready_tasks:
            return []

        # Get critical path
        critical_path = critical_path_analyzer.calculate_critical_path(work_item_id)

        # Score tasks
        scored_tasks = []
        for task in ready_tasks:
            score = self._calculate_priority_score(
                task=task,
                critical_path=critical_path,
                agent_id=agent_id
            )
            scored_tasks.append((task, score))

        # Sort by score (highest first)
        scored_tasks.sort(key=lambda x: x[1], reverse=True)

        return [task for task, score in scored_tasks]

    def _are_dependencies_met(self, task_id: int) -> bool:
        """
        Check if all task dependencies are done.

        Returns: True if task can start
        """

        dependencies = db.query(TaskDependency).filter(
            TaskDependency.dependent_task_id == task_id,
            TaskDependency.mandatory == True
        ).all()

        for dep in dependencies:
            prereq_task = db.query(Task).get(dep.prerequisite_task_id)

            if dep.dependency_type == "finish_to_start":
                if prereq_task.status != "COMPLETED":
                    return False  # Prerequisite not finished

            elif dep.dependency_type == "start_to_start":
                if prereq_task.status == "PROPOSED":
                    return False  # Prerequisite not started

        return True  # All dependencies met

    def _calculate_priority_score(
        self,
        task: Task,
        critical_path: CriticalPath,
        agent_id: Optional[str]
    ) -> float:
        """
        Calculate priority score for task scheduling.

        Factors:
        - Priority level (1-5): 40% weight
        - On critical path: 30% weight
        - Slack time: 20% weight
        - Effort (prefer short tasks): 10% weight
        - Agent match: Bonus if agent specialized for task
        """

        # Base score from priority
        priority_score = task.priority / 5.0  # Normalize to 0-1

        # Critical path bonus
        on_critical_path = 1.0 if task.id in critical_path.tasks else 0.0

        # Slack time (less slack = higher priority)
        slack_hours = critical_path.slack.get(task.id, 100)  # Default high slack
        slack_score = 1.0 - min(slack_hours / 24.0, 1.0)  # Normalize to 0-1

        # Effort (shorter tasks first for quick wins)
        effort_score = 1.0 - (task.effort / 8.0)  # Normalize assuming max 8h

        # Agent match bonus
        agent_bonus = 0.0
        if agent_id and self._is_agent_specialized(agent_id, task.type):
            agent_bonus = 0.2

        # Weighted score
        score = (
            priority_score * 0.4 +
            on_critical_path * 0.3 +
            slack_score * 0.2 +
            effort_score * 0.1 +
            agent_bonus
        )

        return score
```

### Blocking Detection

```python
class BlockingDetectionService:
    """
    Detect when blocked tasks affect critical path.
    """

    def detect_blocking_impact(self, task_id: int) -> BlockingImpact:
        """
        Analyze impact of a blocked task.

        Returns:
        - Downstream tasks affected
        - Critical path impact
        - Time delay caused
        - Recommended actions
        """

        task = db.query(Task).get(task_id)

        if task.status != "BLOCKED":
            return BlockingImpact(blocked=False)

        # Find all tasks that depend on this task
        dependents = self._find_all_dependents(task_id)

        # Check if on critical path
        critical_path = critical_path_analyzer.calculate_critical_path(task.work_item_id)
        on_critical_path = task_id in critical_path.tasks

        # Calculate delay impact
        if on_critical_path:
            # Blocking a critical task delays entire project
            delay = self._estimate_unblock_time(task)
            impact = "CRITICAL"
        elif dependents:
            # Blocking non-critical task delays downstream work
            delay = self._estimate_unblock_time(task)
            impact = "HIGH"
        else:
            # No downstream impact
            delay = None
            impact = "LOW"

        return BlockingImpact(
            blocked=True,
            impact_level=impact,
            affected_tasks=dependents,
            on_critical_path=on_critical_path,
            estimated_delay=delay,
            recommendations=self._get_recommendations(task, impact)
        )

    def _find_all_dependents(self, task_id: int) -> List[int]:
        """
        Recursively find all tasks that depend (directly or indirectly).
        """

        dependents = []
        visited = set()
        queue = [task_id]

        while queue:
            current = queue.pop(0)

            if current in visited:
                continue

            visited.add(current)

            # Find direct dependents
            direct_deps = db.query(TaskDependency).filter(
                TaskDependency.prerequisite_task_id == current
            ).all()

            for dep in direct_deps:
                dependent_id = dep.dependent_task_id
                dependents.append(dependent_id)
                queue.append(dependent_id)  # Recursive

        return dependents

    def _get_recommendations(self, task: Task, impact: str) -> List[str]:
        """
        Recommend actions to unblock.
        """

        recommendations = []

        if impact == "CRITICAL":
            recommendations.append("🚨 URGENT: Unblock immediately (critical path affected)")
            recommendations.append("Consider: Escalate to senior dev or human review")
            recommendations.append("Alternative: Reassign to different agent")

        if task.blocker_type == "waiting_for_review":
            recommendations.append("Escalate review request (SLA at risk)")

        if task.blocker_type == "missing_information":
            recommendations.append("Request clarification from stakeholder")
            recommendations.append("Or: Make assumption and document (risky)")

        return recommendations
```

---

## Consequences

### Positive

1. **Optimal Scheduling**
   - Critical path identified automatically
   - Tasks scheduled in optimal order
   - Parallelization opportunities found

2. **Prevent Wasted Work**
   - Can't start task until dependencies met
   - No working on wrong assumptions
   - Clear prerequisite requirements

3. **Impact Visibility**
   - Know when blocking affects critical path
   - Understand downstream impact
   - Prioritize unblocking work

4. **Better Estimation**
   - Project duration calculated accurately
   - Account for dependencies in timeline
   - Realistic delivery dates

5. **Intelligent Automation**
   - Auto-mark tasks "ready" when deps complete
   - Auto-assign next task to agents
   - Auto-alert on critical path blocks

### Negative

1. **Complexity**
   - Dependency graph maintenance
   - Critical path recalculation overhead
   - More metadata to manage

2. **Overhead**
   - Declaring dependencies takes time
   - Graph analysis computationally expensive
   - Could slow down task creation

3. **Rigidity**
   - Can't start task without dependencies (even if safe)
   - May be too strict for experimental work
   - Override mechanism needed

4. **False Blocking**
   - Soft dependencies treated as hard dependencies
   - May prevent legitimate parallel work
   - Needs tuning

### Mitigation Strategies

1. **Smart Defaults**
   - Auto-detect common dependencies (DESIGN → IMPL → TEST)
   - Suggest dependencies based on task types
   - Optional dependencies for flexibility

2. **Performance Optimization**
   - Cache critical path calculations
   - Incremental graph updates (not full recalculation)
   - Index dependency queries

3. **Flexibility**
   - Mark dependencies as "recommended" vs "mandatory"
   - Override capability (with warning)
   - Soft dependencies for guidance

4. **User Experience**
   - Visual dependency graph
   - Clear error messages
   - Suggested dependency fixes

---

## Implementation Plan

### Phase 1: Core Dependencies (Week 1-2)

```yaml
Week 1: Dependency Model
  Tasks:
    - Create TaskDependency model
    - Implement DependencyGraphService
    - Add circular dependency detection
    - Database migration

  Deliverables:
    - Migration: 0020_add_task_dependencies.py
    - agentpm/core/dependencies/graph.py
    - Tests: circular dependency detection

  Success Criteria:
    - Can add dependencies
    - Circular deps rejected
    - Queries perform <50ms

Week 2: Readiness Detection
  Tasks:
    - Implement task readiness calculation
    - Auto-mark tasks "ready" when deps complete
    - Update task status on dependency changes
    - Event publishing

  Deliverables:
    - Task readiness system
    - Auto-status updates
    - Events: task.ready

  Success Criteria:
    - Tasks auto-marked ready
    - Status updates correct
    - Events published
```

### Phase 2: Critical Path (Week 3-4)

```yaml
Week 3: Critical Path Algorithm
  Tasks:
    - Implement CriticalPathAnalyzer
    - Forward/backward pass algorithm
    - Slack time calculation
    - Parallelization detection

  Deliverables:
    - agentpm/core/dependencies/critical_path.py
    - Critical path tests-BAK
    - CLI: apm work-item critical-path

  Success Criteria:
    - Critical path calculated correctly
    - Parallel tasks identified
    - Performance <200ms for 100 tasks

Week 4: Scheduling Intelligence
  Tasks:
    - Implement TaskScheduler
    - Priority scoring algorithm
    - "Next task" suggestions
    - Agent task matching

  Deliverables:
    - agentpm/core/dependencies/scheduler.py
    - CLI: apm task next
    - Scheduling tests-BAK

  Success Criteria:
    - Next task suggestions accurate
    - Agent matching works
    - Optimal order suggested
```

### Phase 3: Blocking Detection (Week 5-6)

```yaml
Week 5: Blocking Analysis
  Tasks:
    - Implement BlockingDetectionService
    - Downstream impact analysis
    - Critical path impact detection
    - Alert system

  Deliverables:
    - agentpm/core/dependencies/blocking.py
    - Impact analysis
    - Alerts and notifications

  Success Criteria:
    - Blocking impact calculated correctly
    - Critical path blocks detected
    - Alerts sent appropriately

Week 6: Visualization & Reporting
  Tasks:
    - Dependency graph visualization (ASCII)
    - Critical path highlighting
    - Blocking dashboard
    - Reports

  Deliverables:
    - CLI: apm work-item graph
    - Visualization system
    - Reports

  Success Criteria:
    - Graph rendered clearly
    - Critical path highlighted
    - Reports useful
```

---

## Usage Examples

### Example 1: Declaring Dependencies

```bash
# Create tasks for authentication system
apm task create "Database schema" --work-item=5 --type=design --effort=4
# Task ID: 40

apm task create "User model" --work-item=5 --type=implementation --effort=4
# Task ID: 41

apm task create "JWT middleware" --work-item=5 --type=implementation --effort=4
# Task ID: 42

# Declare dependencies
apm task depends 41 --on=40  # User model depends on schema
apm task depends 42 --on=41  # JWT middleware depends on user model

# Validation:
✅ Dependency added: Task #41 depends on Task #40
✅ Dependency added: Task #42 depends on Task #41
✅ No circular dependencies detected

# Check readiness
apm task ready --work-item=5

# Output:
# 📋 Ready to start:
#   • Task #40: Database schema (no dependencies)
#
# ⏳ Waiting on dependencies:
#   • Task #41: User model (waiting on Task #40)
#   • Task #42: JWT middleware (waiting on Task #41)
```

### Example 2: Critical Path Analysis

```bash
apm work-item critical-path 5

# Output:
# 🎯 Critical Path Analysis: Multi-Tenant Authentication
#
# Critical Path (17 hours):
#   Task #40: Database schema (4h)
#      ↓
#   Task #41: User model (4h)
#      ↓
#   Task #42: JWT middleware (4h)
#      ↓
#   Task #45: Integration tests-BAK (5h)
#
# Parallelization Opportunities:
#   After Task #41 completes:
#   ├─ Task #42: JWT middleware (4h)    } Can run
#   └─ Task #43: Login endpoint (3h)    } in parallel
#
# Project Duration:
#   Sequential: 25 hours
#   Optimized: 17 hours (8h saved via parallelization)
#
# Recommendations:
#   • Start Task #40 immediately (on critical path)
#   • Assign 2 agents after Task #41 (parallel work)
#   • Task #44 has 5h slack (can delay if needed)
```

### Example 3: Blocking Impact

```bash
# Task gets blocked
apm task block 41 \
  --reason="Waiting for database review" \
  --blocker-type="waiting_for_review"

# Blocking detection analyzes impact:
🚨 CRITICAL BLOCKING DETECTED

Blocked Task: #41 User model implementation
Reason: Waiting for database review
Blocked since: 2 hours ago

Impact Analysis:
  ❌ On critical path: YES
  ❌ Blocking 3 downstream tasks:
     • Task #42: JWT middleware
     • Task #43: Login endpoint
     • Task #45: Integration tests-BAK

  ⏱️  Project delay: +2 hours (if not unblocked soon)
  📊 Affected work: 17 hours of downstream work blocked

Recommendations:
  🚨 URGENT: Escalate database review (critical path affected)
  💡 Alternative: Assign different agent to review
  💡 Or: Use mock User model for downstream work (risky)

Actions:
  apm review escalate <review-id>
  apm task unblock 41 --approved-by=<reviewer>
```

---

## Related Documents

- **ADR-003**: Sub-Agent Communication Protocol (task coordination)
- **ADR-007**: Human-in-the-Loop Workflows (review blocking)
- **ADR-009**: Event System (blocking events)

---

## Decision Log

| Date | Decision | Rationale |
|------|----------|-----------|
| 2025-10-12 | DAG for dependency graph | Standard, proven approach |
| 2025-10-12 | Critical path algorithm | Optimize project duration |
| 2025-10-12 | Automatic readiness detection | Reduce manual coordination |
| 2025-10-12 | Blocking impact analysis | Prioritize critical work |
| 2025-10-12 | Mandatory vs optional dependencies | Flexibility without chaos |

---

**Status:** Proposed (awaiting review)
**Next Steps:**
1. Review with AIPM core team
2. Prototype dependency graph
3. Test critical path calculation
4. Approve and begin implementation

**Owner:** AIPM Core Team
**Reviewers:** TBD
**Last Updated:** 2025-10-12
