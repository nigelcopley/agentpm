# ADR-011: Cost Tracking and Resource Management

**Status:** Proposed
**Date:** 2025-10-12
**Deciders:** AIPM Core Team
**Technical Story:** Track AI usage costs and optimize resource expenditure

---

## Context

### The AI Cost Problem

AI coding assistants are **expensive at scale**:

**Claude Code Pricing (Example):**
- Input tokens: $3 per million tokens
- Output tokens: $15 per million tokens
- Caching: Reduces cost but still significant

**Real-World Costs:**

```
Multi-Tenant E-Commerce Project (20 weeks):

Session 1: Architecture Planning (2h)
├─ Input: 150K tokens (context)
├─ Output: 50K tokens (decisions, ADRs)
├─ Cost: $0.45 input + $0.75 output = $1.20

Session 2-100: Implementation (200h total)
├─ Average input per session: 100K tokens
├─ Average output per session: 30K tokens
├─ Sessions: 100
├─ Cost: 100 × ($0.30 + $0.45) = $75.00

Sub-Agent Calls (1,000 calls)
├─ Average per call: 20K input, 2K output
├─ Cost: $0.06 + $0.03 = $0.09 per call
├─ Total: 1,000 × $0.09 = $90.00

Evidence Capture (500 web fetches)
├─ Using Claude to analyze pages
├─ Average: 10K input, 1K output
├─ Cost: 500 × ($0.03 + $0.015) = $22.50

Total Project Cost: $188.70

If using multiple providers (Claude + Cursor + Copilot):
Total Cost: $400-600 for 20-week project
```

**Enterprise Concerns:**

1. **Budget Control**: How much will AI assistance cost?
2. **Cost Optimization**: Are we using AI efficiently?
3. **ROI Analysis**: Is AI cost worth the time savings?
4. **Provider Comparison**: Which AI provider is most cost-effective?
5. **Resource Limits**: Prevent runaway costs

**Current Problem:**

```
No cost tracking in AIPM
├─ Don't know how much AI costs per project
├─ Can't optimize usage
├─ Can't justify AI investment (no ROI data)
├─ Can't compare providers by cost
└─ Risk of surprise bills
```

---

## Decision

We will implement a **Cost Tracking and Resource Management System** with:

1. **Token Usage Tracking**: Record all AI provider API calls
2. **Cost Calculation**: Convert tokens to costs per provider pricing
3. **Budget Management**: Set and enforce cost budgets
4. **Cost Analytics**: Analyze costs by work item, agent, provider
5. **Optimization Recommendations**: Identify cost-saving opportunities

### Architecture

```
┌──────────────────────────────────────────────────────────┐
│                Cost Tracking System                       │
│                                                          │
│  ┌────────────────────────────────────────────────────┐ │
│  │ API Call Tracking                                  │ │
│  │                                                    │ │
│  │  Every AI provider call captured:                  │ │
│  │  ├─ Provider (Claude, Cursor, Codex)              │ │
│  │  ├─ Input tokens, Output tokens                    │ │
│  │  ├─ Cached tokens (if applicable)                  │ │
│  │  ├─ Model used (Sonnet, GPT-4, etc.)              │ │
│  │  ├─ Session, work item, task context              │ │
│  │  └─ Timestamp, duration                            │ │
│  └────────────────────┬───────────────────────────────┘ │
│                       │                                  │
│  ┌────────────────────▼───────────────────────────────┐ │
│  │ Cost Calculation Engine                            │ │
│  │                                                    │ │
│  │  Provider Pricing Models:                          │ │
│  │  ├─ Claude: $3/M input, $15/M output              │ │
│  │  ├─ GPT-4 Turbo: $10/M input, $30/M output        │ │
│  │  ├─ Gemini Pro: $0.50/M input, $1.50/M output     │ │
│  │  └─ Codex: $0.02/M tokens                         │ │
│  │                                                    │ │
│  │  Calculate: tokens × price = cost                  │ │
│  └────────────────────┬───────────────────────────────┘ │
│                       │                                  │
│  ┌────────────────────▼───────────────────────────────┐ │
│  │ Cost Analytics & Reporting                         │ │
│  │                                                    │ │
│  │  • Cost per work item                             │ │
│  │  • Cost per agent                                  │ │
│  │  • Cost per session                                │ │
│  │  • Cost trends over time                          │ │
│  │  • ROI analysis (cost vs. time saved)             │ │
│  │  • Provider cost comparison                        │ │
│  │  • Optimization recommendations                    │ │
│  └────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────┘
```

### Cost Tracking Model

```python
@dataclass
class AIProviderCall:
    """
    Record of a single AI provider API call.

    Captured automatically by provider adapters.
    """

    # Identification
    id: str
    session_id: int
    work_item_id: Optional[int]
    task_id: Optional[int]
    agent_id: Optional[str]

    # Provider details
    provider: Literal["claude", "openai", "google", "github"]
    model: str  # "claude-sonnet-4", "gpt-4-turbo", etc.
    endpoint: str  # API endpoint called

    # Token usage
    input_tokens: int
    output_tokens: int
    cached_tokens: int  # Prompt caching savings
    total_tokens: int

    # Cost
    input_cost: Decimal  # In USD
    output_cost: Decimal
    total_cost: Decimal

    # Context
    call_type: Literal[
        "main_orchestrator",  # Main AI session
        "sub_agent",          # Sub-agent delegation
        "evidence_capture",   # Web analysis
        "document_analysis"   # Doc processing
    ]

    # Timing
    timestamp: datetime
    duration_ms: int  # API call duration

    # Metadata
    context_size: int  # How much context provided
    response_size: int  # How much generated

@dataclass
class CostBudget:
    """
    Budget limits for AI usage.
    """

    id: str
    project_id: int
    work_item_id: Optional[int]  # Budget for specific work item

    # Budget limits
    daily_limit: Decimal
    weekly_limit: Decimal
    monthly_limit: Decimal
    total_limit: Optional[Decimal]  # Total project budget

    # Alerts
    alert_threshold: float  # Alert at 80% of budget
    hard_stop_threshold: float  # Stop at 100% of budget

    # Current usage
    current_daily: Decimal
    current_weekly: Decimal
    current_monthly: Decimal
    current_total: Decimal

    # Status
    budget_exceeded: bool
    last_alert: Optional[datetime]
```

### Cost Calculation Service

```python
class CostCalculationService:
    """
    Calculate costs based on provider pricing models.

    Pricing updated monthly (providers change pricing).
    """

    # Provider pricing (per million tokens)
    PRICING = {
        "claude": {
            "claude-sonnet-4": {
                "input": 3.00,
                "output": 15.00,
                "cached_input": 0.30  # 10x cheaper
            },
            "claude-opus-4": {
                "input": 15.00,
                "output": 75.00,
                "cached_input": 1.50
            }
        },
        "openai": {
            "gpt-4-turbo": {
                "input": 10.00,
                "output": 30.00
            },
            "gpt-4": {
                "input": 30.00,
                "output": 60.00
            }
        },
        "google": {
            "gemini-pro": {
                "input": 0.50,
                "output": 1.50
            },
            "gemini-ultra": {
                "input": 2.00,
                "output": 6.00
            }
        },
        "github": {
            "codex": {
                "input": 0.02,  # Per 1K tokens
                "output": 0.02
            }
        }
    }

    def calculate_cost(
        self,
        provider: str,
        model: str,
        input_tokens: int,
        output_tokens: int,
        cached_tokens: int = 0
    ) -> Decimal:
        """
        Calculate cost for AI provider call.

        Returns: Cost in USD (to 4 decimal places)
        """

        pricing = self.PRICING.get(provider, {}).get(model)

        if not pricing:
            logger.warning(f"Unknown pricing for {provider}/{model}")
            return Decimal("0.0")

        # Calculate input cost
        regular_input = max(0, input_tokens - cached_tokens)
        input_cost = (regular_input / 1_000_000) * Decimal(str(pricing["input"]))

        # Calculate cached input cost (if applicable)
        if cached_tokens > 0 and "cached_input" in pricing:
            cached_cost = (cached_tokens / 1_000_000) * Decimal(str(pricing["cached_input"]))
            input_cost += cached_cost

        # Calculate output cost
        output_cost = (output_tokens / 1_000_000) * Decimal(str(pricing["output"]))

        total_cost = input_cost + output_cost

        return total_cost.quantize(Decimal("0.0001"))  # 4 decimal places
```

### Budget Management Service

```python
class BudgetManagementService:
    """
    Enforce cost budgets and prevent overspend.
    """

    def check_budget(
        self,
        project_id: int,
        work_item_id: Optional[int],
        estimated_cost: Decimal
    ) -> BudgetCheckResult:
        """
        Check if operation within budget.

        Called BEFORE making AI provider call.
        Prevents overspend.
        """

        # Get applicable budget
        budget = self._get_budget(project_id, work_item_id)

        if not budget:
            return BudgetCheckResult(approved=True, reason="No budget set")

        # Check daily limit
        if budget.current_daily + estimated_cost > budget.daily_limit:
            return BudgetCheckResult(
                approved=False,
                reason=f"Daily budget exceeded (${budget.current_daily:.2f} / ${budget.daily_limit:.2f})",
                current=budget.current_daily,
                limit=budget.daily_limit
            )

        # Check monthly limit
        if budget.current_monthly + estimated_cost > budget.monthly_limit:
            return BudgetCheckResult(
                approved=False,
                reason=f"Monthly budget exceeded",
                current=budget.current_monthly,
                limit=budget.monthly_limit
            )

        # Alert if approaching limit
        utilization = (budget.current_daily / budget.daily_limit)
        if utilization >= budget.alert_threshold and not self._alerted_recently(budget):
            self._send_budget_alert(budget, utilization)

        return BudgetCheckResult(approved=True)

    def record_usage(
        self,
        project_id: int,
        work_item_id: Optional[int],
        cost: Decimal
    ):
        """
        Record actual cost after AI call.

        Updates budget counters.
        """

        budget = self._get_budget(project_id, work_item_id)

        if budget:
            budget.current_daily += cost
            budget.current_weekly += cost
            budget.current_monthly += cost
            budget.current_total += cost

            # Check if exceeded
            if budget.current_daily >= budget.daily_limit:
                budget.budget_exceeded = True
                self._send_budget_exceeded_alert(budget)

            db.commit()
```

### Cost Analytics

```python
class CostAnalyticsService:
    """
    Analyze AI costs and provide optimization recommendations.
    """

    def analyze_work_item_costs(self, work_item_id: int) -> CostAnalysis:
        """
        Analyze costs for a work item.

        Returns:
        - Total cost
        - Cost by agent
        - Cost by session
        - Cost by provider
        - Token efficiency metrics
        - Optimization opportunities
        """

        calls = db.query(AIProviderCall).filter(
            AIProviderCall.work_item_id == work_item_id
        ).all()

        total_cost = sum(call.total_cost for call in calls)

        # Cost by agent
        by_agent = {}
        for call in calls:
            if call.agent_id:
                by_agent[call.agent_id] = by_agent.get(call.agent_id, 0) + call.total_cost

        # Token efficiency
        total_tokens = sum(call.total_tokens for call in calls)
        cost_per_token = total_cost / total_tokens if total_tokens > 0 else 0

        # Caching effectiveness
        total_cached = sum(call.cached_tokens for call in calls)
        cache_savings = self._calculate_cache_savings(calls)

        # Recommendations
        recommendations = []

        # High-cost agents
        high_cost_agents = [
            agent for agent, cost in by_agent.items()
            if cost > total_cost * 0.3  # Agent using >30% of budget
        ]
        if high_cost_agents:
            recommendations.append(
                f"Optimize {high_cost_agents[0]}: Using {by_agent[high_cost_agents[0]]/total_cost:.0%} of budget"
            )

        # Sub-agent opportunities
        main_orchestrator_cost = sum(
            call.total_cost for call in calls
            if call.call_type == "main_orchestrator"
        )
        if main_orchestrator_cost / total_cost > 0.7:
            recommendations.append(
                "Use more sub-agents: Main orchestrator using 70%+ of tokens"
            )

        return CostAnalysis(
            work_item_id=work_item_id,
            total_cost=total_cost,
            total_tokens=total_tokens,
            cost_per_token=cost_per_token,
            by_agent=by_agent,
            cache_savings=cache_savings,
            recommendations=recommendations
        )

    def calculate_roi(
        self,
        work_item_id: int,
        estimated_human_hours: float,
        hourly_rate: Decimal
    ) -> ROIAnalysis:
        """
        Calculate ROI of AI assistance.

        Compares:
        - AI cost (actual)
        - Human cost (estimated if done manually)
        - Time saved
        - Quality improvement
        """

        # Get actual AI cost
        analysis = self.analyze_work_item_costs(work_item_id)
        ai_cost = analysis.total_cost

        # Calculate human cost (estimated)
        human_cost = Decimal(str(estimated_human_hours)) * hourly_rate

        # Get actual time spent (from sessions)
        sessions = db.query(Session).filter(
            Session.work_item_id == work_item_id
        ).all()
        actual_hours = sum(s.duration.total_seconds() / 3600 for s in sessions)

        # Calculate savings
        time_saved_hours = estimated_human_hours - actual_hours
        cost_saved = human_cost - ai_cost
        roi_percentage = (cost_saved / ai_cost * 100) if ai_cost > 0 else 0

        return ROIAnalysis(
            work_item_id=work_item_id,
            ai_cost=ai_cost,
            human_cost=human_cost,
            cost_saved=cost_saved,
            time_saved_hours=time_saved_hours,
            roi_percentage=roi_percentage,
            break_even_hourly_rate=ai_cost / Decimal(str(actual_hours)) if actual_hours > 0 else 0
        )
```

---

## Consequences

### Positive

1. **Cost Visibility**
   - Know exactly how much AI costs
   - Track costs over time
   - Budget vs. actual reporting

2. **Cost Control**
   - Set budgets to prevent overspend
   - Alerts before exceeding limits
   - Hard stops if needed

3. **ROI Justification**
   - Quantify AI value
   - Compare AI cost vs. human cost
   - Make data-driven decisions

4. **Optimization**
   - Identify expensive agents/sessions
   - Optimize token usage
   - Choose cost-effective providers

5. **Provider Comparison**
   - Compare costs across providers
   - Switch to cheaper provider if equivalent
   - Negotiate better pricing with data

### Negative

1. **Tracking Overhead**
   - Record every AI call (adds latency)
   - Calculate costs in real-time
   - Storage for cost data

2. **Pricing Complexity**
   - Provider pricing changes
   - Different models, different prices
   - Must keep pricing current

3. **Budget Friction**
   - Hard budgets may block legitimate work
   - Developers may avoid AI to save costs
   - Could reduce productivity

4. **Privacy Concerns**
   - Token tracking reveals what AI is used for
   - Could be used for employee monitoring
   - Needs clear usage policies

### Mitigation Strategies

1. **Efficient Tracking**
   - Async cost recording (no blocking)
   - Batch cost calculations
   - Cache pricing data

2. **Auto-Update Pricing**
   - Fetch provider pricing monthly
   - Alert when pricing changes
   - Version pricing data

3. **Smart Budgets**
   - Soft limits (alert) vs hard limits (block)
   - Automatic budget increases (within bounds)
   - Seasonal/project-based budgets

4. **Privacy Protection**
   - Aggregate cost reporting (not individual)
   - No surveillance (cost tracking ≠ monitoring)
   - Clear policies in documentation

---

## Implementation Plan

### Phase 1: Cost Tracking (Week 1-2)

```yaml
Week 1: Data Model & Collection
  Tasks:
    - Create AIProviderCall model
    - Integrate with provider adapters
    - Track all AI calls
    - Cost calculation implementation

  Deliverables:
    - Migration: 0021_add_cost_tracking.py
    - agentpm/core/costs/tracking.py
    - Provider adapter integration

  Success Criteria:
    - All AI calls tracked
    - Costs calculated accurately
    - < 5ms overhead per call

Week 2: Budget System
  Tasks:
    - Create CostBudget model
    - Implement BudgetManagementService
    - Budget enforcement
    - Alert system

  Deliverables:
    - Budget models and service
    - CLI: apm budget set/show/alert
    - Alert system

  Success Criteria:
    - Can set budgets
    - Enforcement works
    - Alerts sent appropriately
```

### Phase 2: Analytics & Reporting (Week 3-4)

```yaml
Week 3: Cost Analytics
  Tasks:
    - Implement CostAnalyticsService
    - Cost breakdowns (by agent, session, provider)
    - Trend analysis
    - Optimization recommendations

  Deliverables:
    - agentpm/core/costs/analytics.py
    - CLI: apm costs analyze
    - Cost reports

  Success Criteria:
    - Accurate cost breakdowns
    - Useful recommendations
    - Trends visible

Week 4: ROI Analysis
  Tasks:
    - Implement ROI calculator
    - Time tracking integration
    - Cost vs. benefit reporting
    - Justification reports

  Deliverables:
    - ROI analysis system
    - CLI: apm costs roi
    - Executive reports

  Success Criteria:
    - ROI calculated correctly
    - Reports convince stakeholders
    - Data-driven decisions
```

---

## Usage Examples

### Example 1: Setting Budgets

```bash
# Set project budget
apm budget set --project \
  --daily=50 \
  --monthly=1000 \
  --alert-at=0.8

# Output:
✅ Budget set for project
  Daily limit: $50.00
  Monthly limit: $1,000.00
  Alert threshold: 80% ($40/day, $800/month)

# Set work item budget
apm budget set --work-item=5 \
  --total=100 \
  --alert-at=0.9

# Output:
✅ Budget set for Work Item #5
  Total limit: $100.00
  Alert threshold: 90% ($90.00)
```

### Example 2: Cost Monitoring

```bash
apm costs show --work-item=5

# Output:
💰 Cost Analysis: Work Item #5 (Multi-Tenant Auth)

Total Cost: $45.32
├─ Input tokens: 2.4M ($7.20)
├─ Output tokens: 1.8M ($27.00)
├─ Cached tokens: 800K ($2.40)
└─ Cache savings: $8.72 (16% saved)

By Agent:
├─ aipm-database-developer: $18.50 (41%)
├─ aipm-python-cli-developer: $15.20 (34%)
├─ Sub-agents (7 calls): $8.40 (19%)
└─ Evidence capture: $3.22 (7%)

By Session:
├─ Session #101 (Architecture): $12.30
├─ Session #102 (Implementation): $20.15
└─ Session #103 (Testing): $12.87

Budget Status:
✅ Under budget: $45.32 / $100.00 (45% used)
⏱️  Sessions: 3 total, avg $15.11 per session

Optimization Opportunities:
💡 Use sub-agents more: Main orchestrator 60% of cost
💡 Enable caching: Only 33% cache hit rate
💡 Consider Gemini for analysis: 6x cheaper than Claude
```

### Example 3: ROI Analysis

```bash
apm costs roi --work-item=5 \
  --estimated-human-hours=80 \
  --hourly-rate=100

# Output:
📊 ROI Analysis: Work Item #5

AI Approach:
├─ Cost: $45.32
├─ Time: 12 hours (actual)
└─ Time saved: 68 hours (85% reduction)

Human-Only Approach (estimated):
├─ Cost: $8,000.00 (80h × $100/h)
├─ Time: 80 hours
└─ Risk: Longer, more errors

Savings:
├─ Cost savings: $7,954.68 (99.4% cheaper!)
├─ Time savings: 68 hours (85% faster)
└─ Quality: AI consistency + human review

ROI: 17,545% return on investment
Break-even rate: $3.78/hour (AI profitable if human cost >$4/hour)

Recommendation: ✅ AI extremely cost-effective for this work

Note: Assumes AI quality equivalent to human.
      Actual quality: 95% test coverage, 0 bugs in production (so far)
```

### Example 4: Provider Cost Comparison

```bash
apm costs compare-providers --work-item=5

# Output:
💰 Provider Cost Comparison: Work Item #5

Same work, different providers:

Claude Sonnet 4 (actual):
├─ Input: 2.4M tokens × $3/M = $7.20
├─ Output: 1.8M tokens × $15/M = $27.00
├─ Caching: 800K tokens × $0.30/M = $0.24
└─ Total: $34.44 (with caching)

GPT-4 Turbo (estimated):
├─ Input: 2.4M tokens × $10/M = $24.00
├─ Output: 1.8M tokens × $30/M = $54.00
├─ No caching support
└─ Total: $78.00 (2.26x more expensive)

Gemini Pro (estimated):
├─ Input: 2.4M tokens × $0.50/M = $1.20
├─ Output: 1.8M tokens × $1.50/M = $2.70
├─ No caching
└─ Total: $3.90 (8.8x cheaper!)

Recommendation:
💡 Consider Gemini Pro for cost optimization
   Trade-off: May have lower quality than Claude
   Test: Run pilot work item with Gemini
```

---

## Related Documents

- **ADR-001**: Provider Abstraction Architecture (multi-provider support)
- **ADR-002**: Context Compression Strategy (token optimization)
- **ADR-005**: Multi-Provider Session Management (provider switching)

---

## Decision Log

| Date | Decision | Rationale |
|------|----------|-----------|
| 2025-10-12 | Track all AI provider calls | Complete cost visibility |
| 2025-10-12 | Soft and hard budget limits | Flexibility + control |
| 2025-10-12 | ROI calculation built-in | Justify AI investment |
| 2025-10-12 | Provider cost comparison | Data-driven provider choice |
| 2025-10-12 | Cache tracking | Optimize caching usage |

---

**Status:** Proposed (awaiting review)
**Next Steps:**
1. Review with AIPM core team
2. Prototype cost tracking
3. Validate pricing accuracy
4. Approve and begin implementation

**Owner:** AIPM Core Team
**Reviewers:** Finance, Engineering Leadership
**Last Updated:** 2025-10-12
