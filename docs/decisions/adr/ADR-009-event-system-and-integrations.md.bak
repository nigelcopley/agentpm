# ADR-009: Event System and Integrations

**Status:** Proposed
**Date:** 2025-10-12
**Deciders:** AIPM Core Team
**Technical Story:** Enable real-time notifications and external system integrations

---

## Context

### The Integration Problem

Teams don't work in isolation - they use multiple tools:
- **Communication**: Slack, Microsoft Teams, Discord
- **Project Management**: Jira, Linear, Asana, Monday.com
- **CI/CD**: GitHub Actions, GitLab CI, Jenkins
- **Monitoring**: Datadog, New Relic, Sentry
- **Documentation**: Notion, Confluence, Google Docs

**Current Problem:**

```
AIPM makes decision → Stored in database → No one knows

Team workflow:
├─ AI agent completes task in AIPM
├─ Task status: COMPLETED in AIPM database
├─ Team using Slack for coordination
├─ No notification sent ❌
└─ Team doesn't know work is done

Result:
- Work sits in review queue (no one knows)
- Blocked dependencies (waiting on unknown completion)
- Manual status checking (inefficient)
- Context fragmentation (AIPM separate from team tools)
```

**Integration Requirements:**

1. **Real-Time Notifications**: Team knows when things happen
2. **Bidirectional Sync**: AIPM ↔ External tools (Jira, Linear)
3. **CI/CD Triggers**: Automate builds/deployments on task completion
4. **Custom Webhooks**: Flexible integration with any external system
5. **Event Filtering**: Subscribe to specific events only

---

## Decision

We will implement an **Event-Driven Integration System** with:

1. **Event Bus**: Publish/subscribe pattern for all AIPM events
2. **Webhook System**: HTTP callbacks for external integrations
3. **Provider Integrations**: Pre-built connectors for common tools
4. **Event Filtering**: Subscribe to specific event types
5. **Retry & Reliability**: Guaranteed event delivery with retries

### Architecture

```
┌──────────────────────────────────────────────────────────┐
│                    AIPM Core Events                       │
│                                                          │
│  Work Items: created, updated, done                │
│  Tasks: created, started, done, blocked            │
│  Decisions: proposed, approved, rejected                │
│  Sessions: started, ended, learning_captured            │
│  Documents: created, updated, superseded                │
│  Agents: assigned, started, done                   │
│                                                          │
│         All events published to Event Bus                │
└─────────────────────────┬────────────────────────────────┘
                          │
                          ▼
          ┌───────────────────────────────┐
          │        Event Bus              │
          │  (In-Process or Redis Pub/Sub)│
          └───────┬───────────────────────┘
                  │
      ┌───────────┼───────────┬────────────────┐
      │           │           │                │
┌─────▼─────┐ ┌──▼──────┐ ┌─▼────────┐ ┌─────▼─────┐
│  Slack    │ │  Webhook│ │   Jira   │ │   CI/CD   │
│Integration│ │ Handler │ │  Sync    │ │  Trigger  │
│           │ │         │ │          │ │           │
│ Sends msg │ │ HTTP    │ │ Updates  │ │ Starts    │
│ to channel│ │ POST    │ │ issues   │ │ pipeline  │
└───────────┘ └─────────┘ └──────────┘ └───────────┘
```

### Event Model

```python
@dataclass
class Event:
    """
    Standard event format for all AIPM events.
    """

    # Identification
    id: str  # UUID
    event_type: str  # dot-notation: task.done, decision.approved
    timestamp: datetime

    # Source
    source: str  # What generated this event
    source_type: Literal["agent", "human", "system"]

    # Payload
    entity_type: str  # work_item, task, decision, etc.
    entity_id: str  # ID of the entity
    data: Dict[str, Any]  # Event-specific data

    # Context
    project_id: int
    work_item_id: Optional[int]
    task_id: Optional[int]
    session_id: Optional[int]

    # Metadata
    correlation_id: Optional[str]  # Group related events
    causation_id: Optional[str]  # What caused this event
    version: int  # Event schema version

@dataclass
class EventSubscription:
    """
    Subscription to specific events.
    """

    id: str
    name: str  # Friendly name
    event_pattern: str  # "task.*" or "decision.approved"
    handler_type: Literal["webhook", "slack", "jira", "custom"]
    handler_config: Dict[str, Any]
    enabled: bool
    created_at: datetime
    last_triggered: Optional[datetime]
    trigger_count: int
```

### Event Bus

```python
class EventBus:
    """
    Publish/subscribe event system.

    Simple in-process for single-server.
    Redis Pub/Sub for distributed/scale.
    """

    def publish(self, event: Event):
        """
        Publish event to all subscribers.

        Steps:
        1. Store event in database (audit trail)
        2. Find matching subscriptions
        3. Trigger handlers (async)
        4. Track delivery status
        """

        # Store event (audit trail)
        db.add(event)
        db.commit()

        # Find subscriptions matching this event type
        subscriptions = self._find_matching_subscriptions(event.event_type)

        # Trigger handlers (asynchronously)
        for subscription in subscriptions:
            asyncio.create_task(
                self._trigger_handler(subscription, event)
            )

    def subscribe(
        self,
        event_pattern: str,
        handler: Callable[[Event], None],
        name: str = None
    ) -> EventSubscription:
        """
        Subscribe to events matching pattern.

        Patterns:
        - "task.done": Exact match
        - "task.*": All task events
        - "*.done": All completion events
        - "*": All events (use sparingly)

        Example:
        event_bus.subscribe(
            event_pattern="decision.approved",
            handler=slack_notification_handler,
            name="Notify team of approved decisions"
        )
        """

    async def _trigger_handler(self, subscription: EventSubscription, event: Event):
        """
        Trigger event handler with retry logic.

        Retry policy:
        - 3 attempts
        - Exponential backoff (1s, 2s, 4s)
        - Log failures
        """

        for attempt in range(3):
            try:
                if subscription.handler_type == "webhook":
                    await self._trigger_webhook(subscription, event)
                elif subscription.handler_type == "slack":
                    await self._trigger_slack(subscription, event)
                elif subscription.handler_type == "jira":
                    await self._trigger_jira(subscription, event)

                # Success - update subscription stats
                subscription.last_triggered = datetime.now()
                subscription.trigger_count += 1
                db.commit()
                break

            except Exception as e:
                logger.error(f"Handler failed (attempt {attempt + 1}): {e}")
                if attempt < 2:
                    await asyncio.sleep(2 ** attempt)  # Exponential backoff
                else:
                    # Final failure - log and alert
                    logger.error(f"Handler permanently failed: {subscription.name}")
                    self._alert_admin(subscription, event, e)
```

### Integration Handlers

#### Slack Integration

```python
class SlackIntegrationHandler:
    """
    Send notifications to Slack channels.
    """

    def __init__(self, webhook_url: str, channel: str):
        self.webhook_url = webhook_url
        self.channel = channel

    async def handle_event(self, event: Event):
        """
        Format event for Slack and send.
        """

        if event.event_type == "task.done":
            message = self._format_task_completed(event)
        elif event.event_type == "decision.needs_review":
            message = self._format_review_request(event)
        elif event.event_type == "work_item.done":
            message = self._format_work_item_completed(event)
        else:
            message = self._format_generic(event)

        # Send to Slack
        async with aiohttp.ClientSession() as session:
            await session.post(
                self.webhook_url,
                json=message
            )

    def _format_task_completed(self, event: Event) -> Dict:
        """
        Format task completion message.

        Example output in Slack:
        ✅ Task Completed: JWT Middleware Implementation
        Work Item: #5 Multi-Tenant Authentication
        Completed by: aipm-python-cli-developer
        Duration: 2h 15m
        Files modified: 3 (auth/middleware.py, auth/jwt.py, settings.py)
        Tests: ✅ 95% coverage

        [View Task] [Review Code]
        """

        task = db.query(Task).get(event.entity_id)
        work_item = task.work_item

        return {
            "channel": self.channel,
            "text": f"✅ Task Completed: {task.title}",
            "blocks": [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*Task Completed:* {task.title}\n"
                                f"*Work Item:* #{work_item.id} {work_item.title}\n"
                                f"*Completed by:* {event.source}\n"
                                f"*Duration:* {event.data.get('duration')}\n"
                                f"*Files modified:* {len(event.data.get('files', []))}"
                    }
                },
                {
                    "type": "actions",
                    "elements": [
                        {
                            "type": "button",
                            "text": {"type": "plain_text", "text": "View Task"},
                            "url": f"https://aipm.app/tasks/{task.id}"
                        },
                        {
                            "type": "button",
                            "text": {"type": "plain_text", "text": "Review Code"},
                            "url": event.data.get('pr_url')
                        }
                    ]
                }
            ]
        }
```

#### Jira Sync Integration

```python
class JiraIntegrationHandler:
    """
    Bidirectional sync with Jira.

    AIPM → Jira: Update Jira issues when AIPM tasks change
    Jira → AIPM: Update AIPM tasks when Jira issues change
    """

    def __init__(self, jira_url: str, api_token: str, project_key: str):
        self.jira_url = jira_url
        self.api_token = api_token
        self.project_key = project_key
        self.jira_client = JIRA(jira_url, token_auth=api_token)

    async def handle_event(self, event: Event):
        """
        Sync AIPM event to Jira.
        """

        if event.event_type == "work_item.created":
            # Create Jira issue
            jira_issue = self._create_jira_issue(event)
            # Store mapping
            self._store_mapping(event.entity_id, jira_issue.key)

        elif event.event_type == "task.done":
            # Update Jira issue status
            jira_key = self._get_jira_key(event.entity_id)
            if jira_key:
                self.jira_client.transition_issue(jira_key, "Done")

        elif event.event_type == "decision.approved":
            # Add comment to Jira
            jira_key = self._get_jira_key_for_work_item(event.work_item_id)
            if jira_key:
                decision = db.query(Decision).get(event.entity_id)
                self.jira_client.add_comment(
                    jira_key,
                    f"Decision Approved: {decision.title}\n\n{decision.decision}"
                )

    def sync_from_jira(self):
        """
        Periodic sync: Jira → AIPM

        Checks for Jira updates and syncs to AIPM.
        Run every 5 minutes via cron.
        """

        # Get AIPM work items with Jira mappings
        mappings = db.query(JiraMapping).all()

        for mapping in mappings:
            jira_issue = self.jira_client.issue(mapping.jira_key)

            # Check if Jira updated
            if jira_issue.fields.updated > mapping.last_synced:
                # Sync changes to AIPM
                work_item = db.query(WorkItem).get(mapping.work_item_id)

                # Update status
                aipm_status = self._map_jira_status(jira_issue.fields.status.name)
                if work_item.status != aipm_status:
                    work_item.status = aipm_status
                    db.commit()

                    # Publish event
                    event_bus.publish(Event(
                        event_type="work_item.synced_from_jira",
                        source="jira-integration",
                        entity_type="work_item",
                        entity_id=work_item.id,
                        data={"jira_key": mapping.jira_key}
                    ))

                mapping.last_synced = datetime.now()
                db.commit()
```

#### GitHub Actions Integration

```python
class GitHubActionsIntegrationHandler:
    """
    Trigger GitHub Actions workflows on AIPM events.
    """

    async def handle_event(self, event: Event):
        """
        Trigger CI/CD on task completion.
        """

        if event.event_type == "task.done":
            task = db.query(Task).get(event.entity_id)

            # If task is testing or deployment
            if task.type in ["TESTING", "DEPLOYMENT"]:
                # Trigger GitHub Actions workflow
                await self._trigger_workflow(
                    workflow="deploy.yml",
                    inputs={
                        "task_id": task.id,
                        "environment": event.data.get("environment", "staging")
                    }
                )

    async def _trigger_workflow(self, workflow: str, inputs: Dict):
        """
        Trigger GitHub Actions workflow via API.
        """

        url = f"https://api.github.com/repos/{owner}/{repo}/actions/workflows/{workflow}/dispatches"

        async with aiohttp.ClientSession() as session:
            await session.post(
                url,
                headers={
                    "Authorization": f"Bearer {github_token}",
                    "Accept": "application/vnd.github.v3+json"
                },
                json={
                    "ref": "main",
                    "inputs": inputs
                }
            )
```

### Webhook System

```python
class WebhookService:
    """
    Generic webhook system for custom integrations.
    """

    def create_webhook(
        self,
        name: str,
        url: str,
        event_pattern: str,
        secret: Optional[str] = None,
        headers: Optional[Dict[str, str]] = None
    ) -> Webhook:
        """
        Create webhook subscription.

        Example:
        create_webhook(
            name="Deploy on task completion",
            url="https://deploy.company.com/trigger",
            event_pattern="task.done",
            secret="webhook_secret_123",
            headers={"X-Deploy-Token": "token_xyz"}
        )
        """

        webhook = Webhook(
            id=generate_uuid(),
            name=name,
            url=url,
            event_pattern=event_pattern,
            secret=secret,
            headers=headers or {},
            enabled=True,
            created_at=datetime.now()
        )

        db.add(webhook)
        db.commit()

        # Subscribe to event bus
        event_bus.subscribe(
            event_pattern=event_pattern,
            handler=lambda event: self._trigger_webhook(webhook, event),
            name=name
        )

        return webhook

    async def _trigger_webhook(self, webhook: Webhook, event: Event):
        """
        Send HTTP POST to webhook URL.

        Payload:
        {
          "event_id": "evt_uuid_123",
          "event_type": "task.done",
          "timestamp": "2025-10-12T10:30:00Z",
          "source": "aipm-python-cli-developer",
          "entity": {
            "type": "task",
            "id": 42,
            "data": {...}
          },
          "signature": "sha256=..."  # HMAC signature if secret provided
        }
        """

        payload = {
            "event_id": event.id,
            "event_type": event.event_type,
            "timestamp": event.timestamp.isoformat(),
            "source": event.source,
            "entity": {
                "type": event.entity_type,
                "id": event.entity_id,
                "data": event.data
            }
        }

        headers = dict(webhook.headers)
        headers["Content-Type"] = "application/json"

        # Add HMAC signature if secret provided
        if webhook.secret:
            signature = self._generate_signature(payload, webhook.secret)
            headers["X-AIPM-Signature"] = signature

        # Send POST request
        async with aiohttp.ClientSession() as session:
            response = await session.post(
                webhook.url,
                json=payload,
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=10)
            )

            # Log delivery
            webhook_delivery = WebhookDelivery(
                webhook_id=webhook.id,
                event_id=event.id,
                delivered_at=datetime.now(),
                status_code=response.status,
                response_body=await response.text() if response.status != 200 else None
            )
            db.add(webhook_delivery)
            db.commit()

            if response.status not in [200, 201, 202]:
                logger.error(f"Webhook delivery failed: {response.status}")
                raise WebhookDeliveryError(f"Status {response.status}")

    def _generate_signature(self, payload: Dict, secret: str) -> str:
        """
        Generate HMAC-SHA256 signature for webhook security.
        """

        payload_bytes = json.dumps(payload, sort_keys=True).encode()
        signature = hmac.new(
            secret.encode(),
            payload_bytes,
            hashlib.sha256
        ).hexdigest()

        return f"sha256={signature}"
```

---

## Consequences

### Positive

1. **Team Awareness**
   - Real-time notifications in Slack/Teams
   - Everyone knows what's happening
   - No manual status checking

2. **Tool Integration**
   - AIPM works with existing tools (Jira, Linear)
   - Don't have to abandon current workflows
   - Gradual adoption possible

3. **Automation Unlocked**
   - Trigger CI/CD on task completion
   - Auto-deploy when tests pass
   - Workflow automation across tools

4. **Flexibility**
   - Webhook system supports any integration
   - Custom workflows via webhooks
   - Extensible for future tools

5. **Audit Trail**
   - All events logged
   - Can trace what triggered what
   - Complete system history

### Negative

1. **External Dependencies**
   - Relies on third-party services (Slack, Jira)
   - Service outages affect notifications
   - API changes can break integrations

2. **Complexity**
   - Multiple integration points
   - Configuration overhead
   - Testing difficulty (mocking external services)

3. **Security Risks**
   - Webhook URLs can be attacked
   - API tokens must be secured
   - Data exposure via webhooks

4. **Event Volume**
   - High-activity projects generate many events
   - Could spam Slack channels
   - Webhook rate limits

### Mitigation Strategies

1. **Graceful Degradation**
   - AIPM works even if integrations fail
   - Queue failed events for retry
   - Alert admins to integration issues

2. **Simplified Configuration**
   - Sensible defaults
   - Configuration wizards
   - Pre-built integration templates

3. **Security Hardening**
   - HMAC signatures for webhooks
   - API token encryption
   - Redact sensitive data in events
   - HTTPS-only webhooks

4. **Event Throttling**
   - Rate limits per integration
   - Event batching for high volume
   - Intelligent filtering (only important events)
   - Digest mode (hourly summary vs real-time)

---

## Implementation Plan

### Phase 1: Event Bus (Week 1-2)

```yaml
Week 1: Core Event System
  Tasks:
    - Implement Event model
    - Create EventBus (in-process)
    - Publish/subscribe pattern
    - Event storage (audit trail)

  Deliverables:
    - agentpm/core/events/bus.py
    - agentpm/core/events/models.py
    - Event tests-BAK

  Success Criteria:
    - Can publish events
    - Subscriptions work
    - Events stored in database

Week 2: Event Integration
  Tasks:
    - Integrate events into all services
    - Publish on work item changes
    - Publish on task changes
    - Publish on decision changes

  Deliverables:
    - Events in all core services
    - Event documentation
    - Integration tests-BAK

  Success Criteria:
    - All state changes publish events
    - Event data complete
    - No performance regression
```

### Phase 2: Webhook System (Week 3-4)

```yaml
Week 3: Webhook Infrastructure
  Tasks:
    - Implement WebhookService
    - HTTP delivery with retries
    - HMAC signature generation
    - Delivery tracking

  Deliverables:
    - agentpm/core/integrations/webhooks.py
    - CLI: apm webhook create/list/delete
    - Webhook tests-BAK

  Success Criteria:
    - Webhooks deliver reliably
    - Retries work
    - Signatures validate

Week 4: Webhook Management
  Tasks:
    - Webhook UI (CLI)
    - Delivery dashboard
    - Failure alerting
    - Rate limiting

  Deliverables:
    - CLI: apm webhook status
    - Delivery monitoring
    - Alert system

  Success Criteria:
    - Can manage webhooks easily
    - Failures detected and alerted
    - Rate limits prevent abuse
```

### Phase 3: Pre-Built Integrations (Week 5-8)

```yaml
Week 5-6: Slack Integration
  Tasks:
    - SlackIntegrationHandler
    - Message formatting
    - Channel configuration
    - Interactive buttons

  Deliverables:
    - Slack integration
    - CLI: apm integrations slack setup
    - Message templates

  Success Criteria:
    - Notifications sent to Slack
    - Messages formatted nicely
    - Interactive buttons work

Week 7: Jira Integration
  Tasks:
    - JiraIntegrationHandler
    - Bidirectional sync
    - Issue mapping
    - Status synchronization

  Deliverables:
    - Jira integration
    - CLI: apm integrations jira setup
    - Sync dashboard

  Success Criteria:
    - AIPM ↔ Jira sync works
    - Status changes propagate
    - No data loss

Week 8: CI/CD Integration
  Tasks:
    - GitHub Actions handler
    - GitLab CI handler
    - Workflow triggers
    - Build status tracking

  Deliverables:
    - CI/CD integrations
    - Trigger system
    - Status dashboard

  Success Criteria:
    - Can trigger builds from AIPM
    - Build status reflected in AIPM
    - Deployment automation works
```

---

## Usage Examples

### Example 1: Slack Notifications

```bash
# Setup Slack integration
apm integrations slack setup \
  --webhook-url="https://hooks.slack.com/services/XXX/YYY/ZZZ" \
  --channel="#engineering"

# Subscribe to events
apm integrations slack subscribe \
  --event="task.done" \
  --event="decision.needs_review" \
  --event="work_item.done"

# Test integration
apm integrations slack test

# Output in Slack:
# ✅ Test message from AIPM
# Integration working correctly!

# Now automatic notifications:
# - Task done → Slack message
# - Decision needs review → Slack alert
# - Work item done → Slack celebration 🎉
```

### Example 2: Jira Bidirectional Sync

```bash
# Setup Jira integration
apm integrations jira setup \
  --url="https://company.atlassian.net" \
  --project-key="PROJ" \
  --api-token="$JIRA_TOKEN"

# Enable sync
apm integrations jira sync --enable

# Create work item in AIPM
apm work-item create "Add payment processing" --type=feature

# Automatically creates Jira issue:
# PROJ-123: Add payment processing
# Status: To Do
# Description: [Synced from AIPM]

# Update in Jira: PROJ-123 → In Progress
# Automatically updates AIPM work item → in_progress

# Complete task in AIPM
apm task complete 42

# Automatically updates Jira issue: Add comment "Task #42 done"
```

### Example 3: CI/CD Automation

```bash
# Setup GitHub Actions integration
apm integrations github setup \
  --repo="company/project" \
  --token="$GITHUB_TOKEN"

# Subscribe to deployment trigger
apm integrations github subscribe \
  --event="task.done" \
  --filter="task.type == 'DEPLOYMENT'" \
  --workflow="deploy.yml"

# When deployment task completes:
# 1. AIPM publishes event: task.done
# 2. GitHub integration receives event
# 3. Triggers deploy.yml workflow
# 4. GitHub Actions runs deployment
# 5. Reports status back to AIPM

# All automatic, no manual triggers
```

---

## Related Documents

- **ADR-005**: Multi-Provider Session Management (session events)
- **ADR-007**: Human-in-the-Loop Workflows (review events)
- **ADR-008**: Data Privacy and Security (event redaction)

---

## Decision Log

| Date | Decision | Rationale |
|------|----------|-----------|
| 2025-10-12 | Event bus pattern | Decoupled, extensible integrations |
| 2025-10-12 | Webhook-based external integrations | Standard, flexible, widely supported |
| 2025-10-12 | Pre-built integrations for common tools | Faster adoption, better UX |
| 2025-10-12 | HMAC signatures for webhooks | Security, authenticity verification |
| 2025-10-12 | Retry with exponential backoff | Reliability, fault tolerance |

---

**Status:** Proposed (awaiting review)
**Next Steps:**
1. Review with AIPM core team
2. Prototype event bus
3. Build Slack integration (most requested)
4. Approve and begin implementation

**Owner:** AIPM Integrations Team
**Reviewers:** TBD
**Last Updated:** 2025-10-12
