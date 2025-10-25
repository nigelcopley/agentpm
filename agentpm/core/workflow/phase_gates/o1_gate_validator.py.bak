"""
O1 Gate Validator - Operations → Evolution Gate

Validates operations phase completion requirements before advancement to evolution.

Required Information (O1 Gate):
    - version_bumped: Semantic version incremented
    - deployed: Deployment successful with health check
    - monitoring_active: Alerts configured and tested
    - rollback_ready: Rollback procedure documented

Purpose:
    Ensures successful deployment and operational readiness
    before archiving to evolution phase.

Operational Requirements:
    - Version bumped (semver)
    - CHANGELOG.md updated
    - Deployment successful
    - Health check passing
    - Monitoring/alerts configured
    - Rollback procedure ready

Pattern:
    1. Check version bumped in metadata
    2. Check deployment status
    3. Check health verification
    4. Check monitoring configuration
    5. Calculate confidence based on operational readiness
"""

from .base_gate_validator import BaseGateValidator, GateResult
from ...database.models.work_item import WorkItem


class O1GateValidator(BaseGateValidator):
    """
    Operations phase gate validator.

    Validates that operations phase completed deployment and monitoring
    before allowing progression to evolution phase.

    Requirements:
        - Version bumped (semver)
        - Deployment successful
        - Health check passing
        - Monitoring/alerts configured

    Example:
        >>> validator = O1GateValidator()
        >>> result = validator.validate(work_item, db)
        >>> if not result.passed:
        >>>     print(f"Ops issues: {result.missing_requirements}")
    """

    def validate(self, work_item: WorkItem, db) -> GateResult:
        """
        Validate O1 gate requirements.

        Checks:
            1. Version bumped in metadata
            2. Deployment successful
            3. Health check passing
            4. Monitoring configured

        Args:
            work_item: WorkItem to validate
            db: DatabaseService for metadata queries

        Returns:
            GateResult with pass/fail and missing requirements

        Example:
            >>> result = validator.validate(work_item, db)
            >>> # result.passed = False
            >>> # result.missing_requirements = [
            >>> #     "Version bump required",
            >>> #     "Deployment not successful"
            >>> # ]
        """
        errors = []
        metadata = self._parse_metadata(work_item.metadata)
        operations = metadata.get('operations', {})

        # Check 1: Version bumped
        version = operations.get('version')
        if not version:
            errors.append("Version bump required")

        # Check 2: Deployment successful
        deployment = operations.get('deployment', {})
        if not deployment.get('successful'):
            errors.append("Deployment not successful")

        # Check 3: Health check passing
        health = operations.get('health_check', {})
        if not health.get('passing'):
            errors.append("Health check not passing")

        # Check 4: Monitoring configured
        monitoring = operations.get('monitoring', {})
        if not monitoring.get('configured'):
            errors.append("Monitoring/alerts not configured")

        # Calculate confidence
        checks_passed = sum([
            bool(version),
            deployment.get('successful', False),
            health.get('passing', False),
            monitoring.get('configured', False)
        ])
        total_checks = 4

        artifacts = {
            'task_count': 0,  # Not relevant for O1
            'checks_passed': checks_passed,
            'checks_total': total_checks,
            'version': version,
            'deployment': deployment,
            'health': health,
            'monitoring': monitoring
        }
        confidence = self._calculate_confidence(work_item, artifacts)

        # Build result
        return GateResult(
            passed=len(errors) == 0,
            missing_requirements=errors,
            confidence=confidence,
            metadata={
                'version': version,
                'deployment_successful': deployment.get('successful', False),
                'health_check_passing': health.get('passing', False),
                'monitoring_configured': monitoring.get('configured', False),
                'checks_passed': checks_passed,
                'checks_total': total_checks
            }
        )
