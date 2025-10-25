"""
Context Freshness Detection - Staleness Tracking

Detects when context becomes stale and needs refresh:
- Tracks context age (days since last update)
- Detects code changes after context generation
- Generates staleness warnings with severity levels
- Calculates freshness penalties for confidence scoring

Pattern: Age-based detection with actionable warnings
"""

from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from dataclasses import dataclass


@dataclass
class FreshnessWarning:
    """
    Warning about stale context.

    Attributes:
        severity: 'info', 'warning', or 'critical'
        message: Human-readable warning message
        action: Recommended action to resolve
        days_old: Context age in days
    """
    severity: str
    message: str
    action: str
    days_old: int


class ContextFreshness:
    """
    Track and detect context staleness.

    Staleness indicators:
    - Plugin facts > 30 days old (warning)
    - Amalgamations > 7 days old (info)
    - Amalgamations > 30 days old (warning)
    - Code changed after last generation (critical)
    """

    # Freshness thresholds (days)
    INFO_THRESHOLD = 7
    WARNING_THRESHOLD = 30
    CRITICAL_THRESHOLD = 90

    def __init__(
        self,
        last_context_update: datetime,
        project_path: Optional[Path] = None
    ):
        """
        Initialize freshness tracker.

        Args:
            last_context_update: When context was last updated
            project_path: Optional path to check git commit times
        """
        self.last_context_update = last_context_update
        self.project_path = project_path
        self.context_age_days = (datetime.now() - last_context_update).days

    def is_stale(self) -> bool:
        """
        Check if context is stale (> 30 days old).

        Returns:
            True if context needs refresh
        """
        return self.context_age_days > self.WARNING_THRESHOLD

    def is_critical(self) -> bool:
        """
        Check if context is critically stale (> 90 days old).

        Returns:
            True if context is dangerously outdated
        """
        return self.context_age_days > self.CRITICAL_THRESHOLD

    def get_freshness_factor(self) -> float:
        """
        Get freshness factor for confidence scoring (0.0-1.0).

        Freshness penalties:
        - 0-7 days: 1.0 (perfect)
        - 8-30 days: 0.8 (good)
        - 31-90 days: 0.5 (stale)
        - 90+ days: 0.2 (very stale)

        Returns:
            Freshness score (0.0-1.0)
        """
        if self.context_age_days <= self.INFO_THRESHOLD:
            return 1.0
        elif self.context_age_days <= self.WARNING_THRESHOLD:
            return 0.8
        elif self.context_age_days <= self.CRITICAL_THRESHOLD:
            return 0.5
        else:
            return 0.2

    def get_staleness_warnings(self) -> List[FreshnessWarning]:
        """
        Generate warnings for stale context.

        Returns:
            List of FreshnessWarning objects with severity and actions
        """
        warnings = []

        if self.context_age_days > self.CRITICAL_THRESHOLD:
            warnings.append(FreshnessWarning(
                severity='critical',
                message=f'Context is {self.context_age_days} days old (critically outdated)',
                action='Run `apm analyze` immediately to refresh context',
                days_old=self.context_age_days
            ))
        elif self.context_age_days > self.WARNING_THRESHOLD:
            warnings.append(FreshnessWarning(
                severity='warning',
                message=f'Context is {self.context_age_days} days old (stale)',
                action='Consider running `apm analyze` to refresh context',
                days_old=self.context_age_days
            ))
        elif self.context_age_days > self.INFO_THRESHOLD:
            warnings.append(FreshnessWarning(
                severity='info',
                message=f'Context is {self.context_age_days} days old',
                action='Optional: Run `apm analyze` for latest changes',
                days_old=self.context_age_days
            ))

        # Check for code changes (if project path provided)
        if self.project_path:
            code_changed_warning = self._check_code_changes()
            if code_changed_warning:
                warnings.append(code_changed_warning)

        return warnings

    def _check_code_changes(self) -> Optional[FreshnessWarning]:
        """
        Check if code changed after last context update.

        Uses git to detect commits after context update timestamp.

        Returns:
            FreshnessWarning if code changed, None otherwise
        """
        if not self.project_path or not (self.project_path / '.git').exists():
            return None

        try:
            import subprocess

            # Get last commit timestamp
            result = subprocess.run(
                ['git', 'log', '-1', '--format=%ct'],
                cwd=self.project_path,
                capture_output=True,
                text=True,
                timeout=5
            )

            if result.returncode != 0:
                return None

            last_commit_timestamp = int(result.stdout.strip())
            last_commit = datetime.fromtimestamp(last_commit_timestamp)

            if last_commit > self.last_context_update:
                commits_since = subprocess.run(
                    ['git', 'rev-list', '--count',
                     f"--since={self.last_context_update.isoformat()}", 'HEAD'],
                    cwd=self.project_path,
                    capture_output=True,
                    text=True,
                    timeout=5
                )

                count = int(commits_since.stdout.strip()) if commits_since.returncode == 0 else 0

                return FreshnessWarning(
                    severity='warning',
                    message=f'Code changed ({count} commits since context update)',
                    action='Run `apm analyze` to update context with latest code',
                    days_old=self.context_age_days
                )

        except (subprocess.TimeoutExpired, ValueError, FileNotFoundError):
            # Git not available or error - skip check
            pass

        return None

    def get_freshness_summary(self) -> Dict[str, Any]:
        """
        Get freshness summary for display.

        Returns:
            Dictionary with age, score, warnings
        """
        return {
            'age_days': self.context_age_days,
            'is_stale': self.is_stale(),
            'is_critical': self.is_critical(),
            'freshness_score': self.get_freshness_factor(),
            'warnings': [
                {
                    'severity': w.severity,
                    'message': w.message,
                    'action': w.action
                }
                for w in self.get_staleness_warnings()
            ]
        }
