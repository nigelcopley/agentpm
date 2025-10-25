# Ideas Workflow

> **Navigation**: [📚 Index](INDEX.md) | [← Previous](workflows/phase-workflow.md) | [Next →](workflows/troubleshooting.md)

## Overview

Ideas in APM (Agent Project Manager) provide a lightweight brainstorming system before committing to formal work items. They enable low-friction capture of concepts that can be voted on, refined through research and design, and eventually converted to work items.

## When to Use Ideas vs Work Items

### Use Ideas For:
- **Early brainstorming** - Capturing concepts before they're fully formed
- **Team voting** - Democratic prioritization of concepts
- **Research phase** - Investigating feasibility and requirements
- **Design exploration** - Planning approach before implementation
- **Low-friction capture** - Quick capture without formal structure

### Use Work Items For:
- **Formal deliverables** - Features, bug fixes, research projects
- **Structured workflow** - Following quality gates and phase progression
- **Task management** - Breaking down work into actionable tasks
- **Time tracking** - Effort estimation and time-boxing
- **Dependencies** - Managing relationships between deliverables

## Idea Lifecycle

Ideas follow a simple 6-state lifecycle:

```
idea → research → design → accepted → converted (terminal)
any state → rejected (terminal)
```

### States Explained

1. **idea** - Initial brainstorming state
2. **research** - Investigating feasibility and requirements
3. **design** - Planning approach and architecture
4. **accepted** - Ready for conversion to work item
5. **converted** - Successfully became a work item (terminal)
6. **rejected** - Not viable, kept for audit trail (terminal)

## Phase Alignment with Work Items

Ideas align with work item phases to ensure smooth transition:

| Idea Status | Work Item Phase | Description |
|-------------|-----------------|-------------|
| idea | pre-D1 | Before discovery phase |
| research | D1_DISCOVERY | Discovery and requirements gathering |
| design | P1_PLAN | Planning and design phase |
| accepted | P1_PLAN | Ready for implementation |
| converted | (work item) | Continues in work item phases |
| rejected | (none) | No work item created |

## Common Workflows

### 1. Quick Idea Capture
```bash
# Create a simple idea
apm idea create "Add dark mode support"

# Add more details
apm idea update 5 --description "Support system dark mode with user preference toggle"
apm idea update 5 --tags ui accessibility
```

### 2. Team Voting and Prioritization
```bash
# List ideas for voting
apm idea list --status=idea

# Vote on ideas
apm idea vote 5 --upvote
apm idea vote 8 --downvote

# See top ideas
apm idea list --limit=10
```

### 3. Research and Design Process
```bash
# Start research phase
apm idea transition 5 research

# Add research findings
apm idea update 5 --description "Research shows 60% of users prefer dark mode. Technical feasibility confirmed."

# Move to design phase
apm idea transition 5 design

# Add design details
apm idea update 5 --description "Design: Toggle in user settings, system preference detection, CSS variables approach"

# Accept the idea
apm idea transition 5 accepted
```

### 4. Conversion to Work Item
```bash
# Convert to work item (auto-phase detection)
apm idea convert 5

# Convert with specific type and priority
apm idea convert 5 --type=feature --priority=2

# Convert and skip discovery phase (research/design already done)
apm idea convert 5 --start-phase=P1_PLAN

# Convert and start directly in implementation
apm idea convert 5 --start-phase=I1_IMPLEMENTATION
```

## CLI Commands Reference

### Core Commands
- `apm idea create "Title"` - Create new idea
- `apm idea list` - List ideas with filters
- `apm idea show <id>` - Display idea details
- `apm idea context <id>` - Show comprehensive context
- `apm idea vote <id> --upvote/--downvote` - Vote on idea
- `apm idea update <id> --description="..."` - Update idea
- `apm idea transition <id> <status>` - Move through workflow
- `apm idea convert <id>` - Convert to work item
- `apm idea reject <id> "Reason"` - Reject idea

### Useful Filters
- `apm idea list --status=accepted` - Ideas ready for conversion
- `apm idea list --tags=ui` - Ideas with specific tags
- `apm idea list --limit=10` - Top 10 ideas by votes

## Best Practices

### 1. Idea Creation
- **Clear titles** - Use descriptive, actionable titles
- **Add tags** - Categorize for easy filtering
- **Include source** - Track where ideas come from
- **Set attribution** - Record who created the idea

### 2. Research Phase
- **Investigate feasibility** - Technical and business viability
- **Gather requirements** - User needs and constraints
- **Assess effort** - Rough estimation of complexity
- **Document findings** - Update description with research results

### 3. Design Phase
- **Plan approach** - Architecture and implementation strategy
- **Consider alternatives** - Evaluate different solutions
- **Define scope** - What's included and excluded
- **Document decisions** - Rationale for chosen approach

### 4. Conversion
- **Choose right type** - Feature, bugfix, research, etc.
- **Set appropriate priority** - Based on business value
- **Use phase override** - Skip phases if work already done
- **Add business context** - Justification and impact

## Integration with Work Items

### Traceability
- Ideas maintain bidirectional links with work items
- Work items show origin information
- Full audit trail from brainstorm to delivery

### Context Transfer
- Idea metadata copied to work item
- Tags, source, and votes preserved
- Research and design work carried forward

### Phase Continuity
- Work items start in appropriate phase
- No duplication of research/design work
- Smooth transition from exploration to execution

## Decision Tree: Idea vs Work Item

```
Is this a fully formed concept with clear requirements?
├─ Yes → Create Work Item
└─ No → Is this worth exploring further?
    ├─ Yes → Create Idea
    └─ No → Don't create anything

Is this a quick fix or small improvement?
├─ Yes → Create Work Item (type: bugfix/enhancement)
└─ No → Is this a new feature or major change?
    ├─ Yes → Create Idea (explore first)
    └─ No → Create Work Item (type: research/planning)
```

## Troubleshooting

### Common Issues

**Q: Can I convert an idea that's not in 'accepted' status?**
A: No, only ideas in 'accepted' status can be converted. Use `apm idea transition <id> accepted` first.

**Q: What happens to idea votes after conversion?**
A: Votes are preserved in work item metadata for historical reference.

**Q: Can I reject an idea that's already converted?**
A: No, converted ideas are in terminal state. Create a new work item to track issues.

**Q: How do I see which work item came from an idea?**
A: Use `apm work-item show <id>` to see origin information, or `apm idea show <id>` to see conversion details.

### Getting Help
- Use `apm idea context <id>` for comprehensive information
- Check `apm idea show <id>` for current status and next steps
- Review phase alignment with `apm idea show <id>` output

---

## Navigation

- [📚 Back to Index](INDEX.md)
- [⬅️ Previous: Ideas Workflow](workflows/phase-workflow.md)
- [➡️ Next: Troubleshooting](workflows/troubleshooting.md)

---
