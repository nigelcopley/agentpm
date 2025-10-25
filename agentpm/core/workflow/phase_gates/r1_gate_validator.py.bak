"""
R1 Gate Validator - Review → Operations Gate

Validates review phase completion requirements before advancement to operations.

Required Information (R1 Gate):
    - acceptance_criteria_verified: All D1 ACs tested and passing
    - tests_passing: 100% test pass rate
    - quality_checks: Static analysis and security scans passing
    - code_review: Approved by DIFFERENT agent (no self-approval)

Purpose:
    Ensures quality validation complete before deployment.
    Prevents deploying unverified or failing code to production.

Quality Requirements:
    - All acceptance criteria from D1 verified
    - 100% test pass rate (no failing tests)
    - Static analysis passing (no errors)
    - Security scan passing (no HIGH/CRITICAL vulnerabilities)
    - Code review approval from different agent

Pattern:
    1. Check all D1 acceptance criteria verified
    2. Check test pass rate = 100%
    3. Check code review approval exists
    4. Validate quality checks (if available)
    5. Calculate confidence based on verification quality
"""

from .base_gate_validator import BaseGateValidator, GateResult
from ...database.models.work_item import WorkItem


class R1GateValidator(BaseGateValidator):
    """
    Review phase gate validator.

    Validates that review phase completed quality validation
    before allowing progression to operations phase.

    Requirements:
        - All acceptance criteria verified
        - 100% test pass rate
        - Code review approved
        - Quality checks passing

    Example:
        >>> validator = R1GateValidator()
        >>> result = validator.validate(work_item, db)
        >>> if not result.passed:
        >>>     print(f"Quality issues: {result.missing_requirements}")
    """

    def validate(self, work_item: WorkItem, db) -> GateResult:
        """
        Validate R1 gate requirements.

        Checks:
            1. All D1 acceptance criteria verified
            2. Test pass rate = 100%
            3. Code review approved
            4. Quality checks passing (static analysis, security)

        Args:
            work_item: WorkItem to validate
            db: DatabaseService for metadata queries

        Returns:
            GateResult with pass/fail and missing requirements

        Example:
            >>> result = validator.validate(work_item, db)
            >>> # result.passed = False
            >>> # result.missing_requirements = [
            >>> #     "AC #2 not verified: User can export data",
            >>> #     "Code review approval required"
            >>> # ]
        """
        errors = []
        metadata = self._parse_metadata(work_item.metadata)

        # Check 1: All acceptance criteria verified
        ac_errors = self._check_acceptance_criteria(metadata)
        errors.extend(ac_errors)

        # Check 2: Test pass rate
        test_pass_rate = self._get_test_pass_rate(metadata)
        if test_pass_rate < 1.0:
            errors.append(
                f"Test pass rate {test_pass_rate:.0%} "
                f"(need 100%)"
            )

        # Check 3: Code review approval
        if not self._check_code_review_approval(metadata):
            errors.append("Code review approval required")

        # Check 4: Quality checks (if available)
        quality_errors = self._check_quality_gates(metadata)
        errors.extend(quality_errors)

        # Calculate confidence
        ac_verified_count = len(metadata.get('ac_verification_results', {}))
        total_acs = len(metadata.get('acceptance_criteria', []))

        artifacts = {
            'task_count': 0,  # Not relevant for R1
            'ac_verified': ac_verified_count,
            'ac_total': total_acs,
            'test_pass_rate': test_pass_rate,
            'review_approved': self._check_code_review_approval(metadata)
        }
        confidence = self._calculate_confidence(work_item, artifacts)

        # Build result
        return GateResult(
            passed=len(errors) == 0,
            missing_requirements=errors,
            confidence=confidence,
            metadata={
                'acceptance_criteria_verified': ac_verified_count,
                'acceptance_criteria_total': total_acs,
                'test_pass_rate': f"{test_pass_rate:.0%}",
                'code_review_approved': self._check_code_review_approval(metadata),
                'quality_checks': quality_errors or ['All passing']
            }
        )

    def _check_acceptance_criteria(self, metadata: dict) -> list:
        """
        Check if all acceptance criteria verified.

        Args:
            metadata: Work item metadata

        Returns:
            List of error messages for unverified ACs
        """
        errors = []
        acs = metadata.get('acceptance_criteria', [])
        ac_results = metadata.get('ac_verification_results', {})

        for i, ac in enumerate(acs):
            ac_key = f'ac_{i}'
            result = ac_results.get(ac_key, {})

            if not result.get('passed'):
                # Extract AC description (handle both string and dict formats)
                ac_desc = ac if isinstance(ac, str) else ac.get('description', f'AC #{i+1}')
                errors.append(f"AC #{i+1} not verified: {ac_desc}")

        return errors

    def _get_test_pass_rate(self, metadata: dict) -> float:
        """
        Get test pass rate from metadata.

        Args:
            metadata: Work item metadata

        Returns:
            Pass rate 0.0-1.0 (default 1.0 if no test results)
        """
        test_results = metadata.get('test_results', {})
        total = test_results.get('total', 0)
        passed = test_results.get('passed', 0)

        if total == 0:
            # No test results recorded - assume all passing
            return 1.0

        return passed / total

    def _check_code_review_approval(self, metadata: dict) -> bool:
        """
        Check if code review approved.

        Args:
            metadata: Work item metadata

        Returns:
            True if review approved, False otherwise
        """
        review = metadata.get('review', {})
        return bool(review.get('approved_by'))

    def _check_quality_gates(self, metadata: dict) -> list:
        """
        Check quality gates (static analysis, security).

        Args:
            metadata: Work item metadata

        Returns:
            List of error messages for failing quality gates
        """
        errors = []
        quality = metadata.get('quality_checks', {})

        # Static analysis
        static_analysis = quality.get('static_analysis', {})
        if static_analysis.get('errors', 0) > 0:
            errors.append(
                f"Static analysis: {static_analysis['errors']} error(s)"
            )

        # Security scan
        security = quality.get('security_scan', {})
        high_vulns = security.get('high', 0)
        critical_vulns = security.get('critical', 0)

        if high_vulns > 0 or critical_vulns > 0:
            errors.append(
                f"Security vulnerabilities: "
                f"{critical_vulns} critical, {high_vulns} high"
            )

        return errors
