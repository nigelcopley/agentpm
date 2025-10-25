# ADR-008: Data Privacy and Security

**Status:** Proposed
**Date:** 2025-10-12
**Deciders:** AIPM Core Team
**Technical Story:** Protect sensitive data in context, evidence, documents, and session logs

---

## Context

### The Sensitive Data Problem

AIPM captures and stores extensive information:
- **Evidence**: Web pages (may contain API keys in examples)
- **Documents**: Architecture docs (may include credentials)
- **Session Logs**: Full activity (may capture sensitive operations)
- **Code References**: File paths and line numbers (may point to secrets)
- **Decisions**: Implementation details (may include configuration)

**Risk Scenarios:**

```
Scenario 1: Evidence Capture
├─ AI agent researches "Stripe API integration"
├─ Captures evidence from blog post
├─ Blog post includes: "Use test key: sk_test_abc123..."
├─ Evidence stored in database with API key ❌
└─ API key now in plain text in AIPM database

Scenario 2: Session Logging
├─ Developer working on production deployment
├─ Session logs capture: "Set AWS_SECRET_ACCESS_KEY=..."
├─ Full command stored in session history ❌
└─ Production credentials in session database

Scenario 3: Document Registration
├─ Agent creates deployment guide
├─ Guide includes: "Database URL: postgresql://user:pass@host..."
├─ Document registered with full content hash ❌
└─ Connection string in document metadata

Scenario 4: Code References
├─ Context includes file: config/secrets.py:45
├─ Agent loads secrets file to understand context ❌
├─ Secrets in AI provider's conversation history
└─ Sensitive data exposed to external AI service
```

**Compliance Requirements:**
- **GDPR**: Protect PII, right to deletion
- **SOC 2**: Secure data handling, access controls
- **HIPAA**: Protected health information (if healthcare)
- **PCI DSS**: Payment card data (if e-commerce)
- **ISO 27001**: Information security management

---

## Decision

We will implement a **Multi-Layer Data Protection System** with:

1. **Sensitive Data Detection**: Auto-detect secrets, PII, credentials
2. **Redaction System**: Automatically redact sensitive data before storage
3. **Encryption at Rest**: Encrypt sensitive fields in database
4. **Access Control**: Role-based access to sensitive information
5. **Audit Logging**: Track all access to sensitive data
6. **Data Lifecycle**: Automatic purging of sensitive data

### Architecture

```
┌──────────────────────────────────────────────────────────┐
│              Data Protection Layers                       │
│                                                          │
│  Layer 1: Detection (before storage)                    │
│  ┌────────────────────────────────────────────────────┐ │
│  │ SensitiveDataDetector                              │ │
│  │  • API keys, tokens, passwords                     │ │
│  │  • Email addresses, phone numbers (PII)            │ │
│  │  • Credit card numbers, SSNs                       │ │
│  │  • Connection strings, credentials                 │ │
│  │  • IP addresses, hostnames                         │ │
│  └──────────────────┬─────────────────────────────────┘ │
│                     │                                    │
│  Layer 2: Redaction (before storage)                    │
│  ┌──────────────────▼─────────────────────────────────┐ │
│  │ DataRedactionService                               │ │
│  │  • Replace: sk_test_abc123 → [REDACTED:API_KEY]   │ │
│  │  • Replace: user@email.com → [REDACTED:EMAIL]     │ │
│  │  • Replace: postgresql://u:p@host → [REDACTED:URL]│ │
│  │  • Store hash for verification (not original)     │ │
│  └──────────────────┬─────────────────────────────────┘ │
│                     │                                    │
│  Layer 3: Encryption (at rest)                          │
│  ┌──────────────────▼─────────────────────────────────┐ │
│  │ EncryptionService (AES-256)                        │ │
│  │  • Encrypt before database write                   │ │
│  │  • Decrypt on authorized read                      │ │
│  │  • Key management (env vars, vault)               │ │
│  └──────────────────┬─────────────────────────────────┘ │
│                     │                                    │
│  Layer 4: Access Control                                │
│  ┌──────────────────▼─────────────────────────────────┐ │
│  │ AccessControlService (RBAC)                        │ │
│  │  • Agent access levels (read/write/admin)          │ │
│  │  • Human roles (developer, reviewer, admin)        │ │
│  │  • Audit all access to sensitive data             │ │
│  └──────────────────┬─────────────────────────────────┘ │
│                     │                                    │
│  Layer 5: Lifecycle Management                          │
│  ┌──────────────────▼─────────────────────────────────┐ │
│  │ DataLifecycleService                               │ │
│  │  • Auto-purge after retention period               │ │
│  │  • Export for data subject requests (GDPR)        │ │
│  │  • Secure deletion (overwrite, not just unlink)   │ │
│  └────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────┘
```

### Sensitive Data Detection

```python
class SensitiveDataDetector:
    """
    Detect sensitive data using regex patterns and ML models.
    """

    # Regex patterns for common sensitive data
    PATTERNS = {
        "api_key": r"(sk|pk)_(test|live)_[a-zA-Z0-9]{24,}",
        "aws_key": r"AKIA[0-9A-Z]{16}",
        "jwt_token": r"eyJ[a-zA-Z0-9_-]{10,}\.[a-zA-Z0-9_-]{10,}\.",
        "password": r"(password|passwd|pwd)\s*[:=]\s*['\"]?([^'\"\\s]+)",
        "connection_string": r"(postgres|mysql|mongodb):\/\/[^\\s]+",
        "email": r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
        "credit_card": r"\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b",
        "ssn": r"\b\d{3}-\d{2}-\d{4}\b",
        "ip_address": r"\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b",
        "private_key": r"-----BEGIN (RSA |EC )?PRIVATE KEY-----"
    }

    def detect(self, text: str) -> List[SensitiveDataMatch]:
        """
        Detect all sensitive data in text.

        Returns: List of matches with type, position, confidence
        """

        matches = []

        for data_type, pattern in self.PATTERNS.items():
            for match in re.finditer(pattern, text, re.IGNORECASE):
                matches.append(SensitiveDataMatch(
                    data_type=data_type,
                    value=match.group(),
                    start=match.start(),
                    end=match.end(),
                    confidence=0.95,  # Regex = high confidence
                    severity=self._get_severity(data_type)
                ))

        return matches

    def _get_severity(self, data_type: str) -> str:
        """
        Classify sensitivity level.

        Critical: Immediate security risk (API keys, passwords)
        High: Privacy risk (email, SSN, credit card)
        Medium: Operational info (IP address, hostname)
        Low: Business info (company name)
        """

        severity_map = {
            "api_key": "critical",
            "aws_key": "critical",
            "password": "critical",
            "private_key": "critical",
            "jwt_token": "critical",
            "connection_string": "critical",
            "credit_card": "high",
            "ssn": "high",
            "email": "high",
            "ip_address": "medium"
        }

        return severity_map.get(data_type, "low")
```

### Data Redaction Service

```python
class DataRedactionService:
    """
    Redact sensitive data before storage.

    Replaces sensitive values with placeholders.
    Stores hash (not original) for verification.
    """

    def redact(self, text: str) -> RedactedText:
        """
        Redact all sensitive data from text.

        Example:
        Input:  "Use API key sk_test_abc123 for Stripe"
        Output: "Use API key [REDACTED:API_KEY:hash_xyz] for Stripe"

        Benefits:
        - Original value not stored
        - Can verify if value changes (hash comparison)
        - Context preserved (know it was an API key)
        """

        detector = SensitiveDataDetector()
        matches = detector.detect(text)

        # Sort by position (reverse) to avoid offset issues
        matches.sort(key=lambda m: m.start, reverse=True)

        redacted_text = text
        redactions = []

        for match in matches:
            # Generate hash of sensitive value (for verification)
            value_hash = hashlib.sha256(match.value.encode()).hexdigest()[:8]

            # Create redaction placeholder
            placeholder = f"[REDACTED:{match.data_type.upper()}:{value_hash}]"

            # Replace in text
            redacted_text = (
                redacted_text[:match.start] +
                placeholder +
                redacted_text[match.end:]
            )

            # Record redaction
            redactions.append(Redaction(
                data_type=match.data_type,
                value_hash=value_hash,  # Hash only (not original)
                start=match.start,
                end=match.end,
                placeholder=placeholder,
                severity=match.severity
            ))

        return RedactedText(
            original_text=None,  # Don't store original
            redacted_text=redacted_text,
            redactions=redactions,
            redaction_count=len(redactions)
        )

    def verify_redaction(self, redacted_text: str, test_value: str) -> bool:
        """
        Check if a value was redacted from text.

        Use case: Verify credentials were properly redacted
        """

        test_hash = hashlib.sha256(test_value.encode()).hexdigest()[:8]
        return f":{test_hash}]" in redacted_text
```

### Encryption Service

```python
class EncryptionService:
    """
    Encrypt sensitive fields at rest.

    Fields to encrypt:
    - Evidence excerpts (may contain secrets)
    - Decision rationale (may include sensitive details)
    - Session logs (may capture commands with credentials)
    - Document summaries (may include sensitive info)
    """

    def __init__(self, encryption_key: str):
        """
        Initialize with encryption key from environment.

        Key management:
        - Environment variable: AIPM_ENCRYPTION_KEY
        - Or external vault: AWS KMS, HashiCorp Vault
        - Rotation supported (dual-key period)
        """
        self.key = encryption_key.encode()
        self.cipher = Fernet(self.key)

    def encrypt(self, plaintext: str) -> str:
        """
        Encrypt text before database storage.

        Returns: Base64-encoded encrypted string
        """
        encrypted = self.cipher.encrypt(plaintext.encode())
        return base64.b64encode(encrypted).decode()

    def decrypt(self, ciphertext: str) -> str:
        """
        Decrypt text when authorized user/agent accesses.

        Returns: Original plaintext
        """
        encrypted = base64.b64decode(ciphertext.encode())
        decrypted = self.cipher.decrypt(encrypted)
        return decrypted.decode()

# Database model with encryption
class EncryptedEvidence(Base):
    __tablename__ = "evidence_entries"

    excerpt = Column(String)  # Encrypted at rest

    @hybrid_property
    def excerpt_plaintext(self):
        """Decrypt on read (if authorized)"""
        if not self.excerpt:
            return None
        return encryption_service.decrypt(self.excerpt)

    @excerpt_plaintext.setter
    def excerpt_plaintext(self, value: str):
        """Encrypt on write"""
        if value:
            # Detect sensitive data
            matches = detector.detect(value)
            if matches:
                # Redact first
                redacted = redaction_service.redact(value)
                value = redacted.redacted_text

            # Then encrypt
            self.excerpt = encryption_service.encrypt(value)
```

### File Exclusion Patterns

```python
class SensitiveFileFilter:
    """
    Prevent sensitive files from being included in context.

    Files to exclude:
    - .env, .env.local, .env.production
    - credentials.json, secrets.yaml
    - private keys (*.pem, *.key)
    - OAuth tokens, session files
    - Database dumps, backups
    """

    EXCLUDED_PATTERNS = [
        r"\.env(\..+)?$",
        r"credentials?\.(json|yaml|yml)$",
        r"secrets?\.(json|yaml|yml)$",
        r".*\.(pem|key|p12|pfx)$",
        r"\.aws/credentials$",
        r"\.ssh/id_.*$",
        r"\.netrc$",
        r".*_backup\.(sql|dump)$",
        r"\.password.*$"
    ]

    def is_sensitive_file(self, file_path: str) -> bool:
        """
        Check if file should be excluded from context.

        Returns: True if file is sensitive
        """

        file_name = Path(file_path).name

        for pattern in self.EXCLUDED_PATTERNS:
            if re.match(pattern, file_name, re.IGNORECASE):
                return True

        return False

    def filter_context_files(self, files: List[str]) -> List[str]:
        """
        Remove sensitive files from context file list.

        Also logs exclusions for audit.
        """

        filtered = []
        excluded = []

        for file_path in files:
            if self.is_sensitive_file(file_path):
                excluded.append(file_path)
                audit_log.record(
                    action="EXCLUDE_SENSITIVE_FILE",
                    entity_type="file",
                    data={"path": file_path, "reason": "sensitive_pattern_match"}
                )
            else:
                filtered.append(file_path)

        if excluded:
            logger.warning(f"Excluded {len(excluded)} sensitive files from context")

        return filtered
```

### GDPR Compliance

```python
class GDPRComplianceService:
    """
    GDPR compliance: Right to access, rectification, erasure, portability.
    """

    def export_user_data(self, user_email: str) -> DataExport:
        """
        Export all data related to a user (GDPR Article 20).

        Includes:
        - All decisions made by this user
        - All evidence captured by this user
        - All sessions by this user
        - All documents authored by this user
        - All learnings recorded by this user
        """

        data_export = {
            "user": user_email,
            "exported_at": datetime.now().isoformat(),
            "decisions": db.query(Decision).filter(Decision.made_by == user_email).all(),
            "evidence": db.query(EvidenceEntry).filter(Evidence.captured_by == user_email).all(),
            "sessions": db.query(Session).filter(Session.user == user_email).all(),
            "documents": db.query(Document).filter(Document.author == user_email).all(),
            "learnings": db.query(Learning).filter(Learning.agent_id == user_email).all()
        }

        # Export as JSON
        export_path = f"/tmp/aipm-gdpr-export-{user_email}-{datetime.now():%Y%m%d}.json"
        Path(export_path).write_text(json.dumps(data_export, default=str, indent=2))

        return DataExport(
            user=user_email,
            path=export_path,
            record_count=sum(len(v) for v in data_export.values() if isinstance(v, list)),
            exported_at=datetime.now()
        )

    def delete_user_data(self, user_email: str, confirm: bool = False) -> DeletionResult:
        """
        Delete all user data (GDPR Article 17 - Right to Erasure).

        Requires explicit confirmation (confirm=True).

        WARNING: This is irreversible.
        """

        if not confirm:
            # Dry run: Show what would be deleted
            counts = {
                "decisions": db.query(Decision).filter(Decision.made_by == user_email).count(),
                "evidence": db.query(Evidence).filter(Evidence.captured_by == user_email).count(),
                "sessions": db.query(Session).filter(Session.user == user_email).count(),
                "documents": db.query(Document).filter(Document.author == user_email).count(),
                "learnings": db.query(Learning).filter(Learning.agent_id == user_email).count()
            }

            return DeletionResult(
                dry_run=True,
                would_delete=counts,
                warning="This will permanently delete all data. Use --confirm to proceed."
            )

        # Actual deletion (confirmed)
        deleted = {}

        # Delete in order (respecting foreign keys)
        deleted["evidence"] = db.query(Evidence).filter(Evidence.captured_by == user_email).delete()
        deleted["learnings"] = db.query(Learning).filter(Learning.agent_id == user_email).delete()
        deleted["decisions"] = db.query(Decision).filter(Decision.made_by == user_email).delete()
        deleted["documents"] = db.query(Document).filter(Document.author == user_email).delete()
        deleted["sessions"] = db.query(Session).filter(Session.user == user_email).delete()

        db.commit()

        # Audit the deletion
        audit_log.record(
            actor=user_email,
            action="GDPR_DATA_DELETION",
            entity_type="user_data",
            data={"deleted_counts": deleted}
        )

        return DeletionResult(
            dry_run=False,
            deleted=deleted,
            total_records_deleted=sum(deleted.values())
        )
```

### Access Control System

```python
class AccessControlService:
    """
    Role-based access control for sensitive data.
    """

    ROLES = {
        "agent": {
            "read": ["decisions", "evidence", "learnings", "documents"],
            "write": ["decisions", "evidence", "learnings"],
            "admin": []
        },
        "developer": {
            "read": ["decisions", "evidence", "learnings", "documents", "sessions"],
            "write": ["decisions", "documents", "learnings"],
            "admin": []
        },
        "reviewer": {
            "read": ["decisions", "evidence", "documents"],
            "write": ["decisions.review"],
            "admin": []
        },
        "admin": {
            "read": "*",
            "write": "*",
            "admin": "*"
        }
    }

    def check_access(
        self,
        actor: str,
        actor_type: Literal["agent", "human"],
        action: Literal["read", "write", "admin"],
        resource_type: str
    ) -> bool:
        """
        Check if actor can perform action on resource.

        Example:
        check_access(
            actor="aipm-python-cli-developer",
            actor_type="agent",
            action="read",
            resource_type="decisions"
        )
        # Returns: True (agents can read decisions)

        check_access(
            actor="aipm-python-cli-developer",
            actor_type="agent",
            action="admin",
            resource_type="database"
        )
        # Returns: False (agents can't admin database)
        """

        role = self._get_role(actor, actor_type)
        permissions = self.ROLES.get(role, {})

        # Check if action is allowed for this resource
        allowed_resources = permissions.get(action, [])

        if "*" in allowed_resources:
            return True  # Admin has access to everything

        return resource_type in allowed_resources

    def require_access(self, actor: str, action: str, resource: str):
        """
        Decorator/assertion for access control.

        Raises AccessDeniedError if not authorized.
        """

        if not self.check_access(actor, self._get_actor_type(actor), action, resource):
            audit_log.record(
                actor=actor,
                action="ACCESS_DENIED",
                entity_type=resource,
                data={"attempted_action": action}
            )

            raise AccessDeniedError(
                f"{actor} not authorized to {action} {resource}"
            )
```

---

## Consequences

### Positive

1. **Security Protection**
   - Secrets automatically redacted
   - Sensitive data encrypted at rest
   - Unauthorized access prevented

2. **Compliance Ready**
   - GDPR: Data export and deletion
   - SOC 2: Audit trail and encryption
   - PCI DSS: Card data protection

3. **Audit Trail**
   - All access to sensitive data logged
   - Can answer "who accessed what, when?"
   - Compliance reporting

4. **Defense in Depth**
   - Multiple layers (detection, redaction, encryption, access control)
   - Failure of one layer doesn't expose data
   - Progressive security hardening

### Negative

1. **Performance Overhead**
   - Detection adds 10-50ms per text analysis
   - Encryption adds 5-20ms per field
   - Access control checks add 1-5ms

2. **False Positives**
   - Regex may detect non-sensitive data as sensitive
   - Example: "test@example.com" flagged as PII
   - Requires tuning and exception management

3. **Data Loss Risk**
   - Redaction removes information permanently
   - Can't recover original value
   - May lose legitimate context

4. **Complexity**
   - Multiple security systems to maintain
   - Key management overhead
   - GDPR compliance burden

### Mitigation Strategies

1. **Performance Optimization**
   - Cache detection results
   - Batch encryption operations
   - Lazy decryption (only when accessed)
   - Async security checks

2. **False Positive Management**
   - Whitelist patterns (test@example.com OK)
   - Confidence thresholds (only redact >0.9)
   - Manual override capability
   - Feedback loop for tuning

3. **Safe Redaction**
   - Store hash for verification
   - Warn users when redacting
   - Option to review before storage
   - Reversible for non-critical data (with audit)

4. **Simplified Compliance**
   - Automated GDPR workflows
   - One-click data export
   - Scheduled compliance reports
   - Self-service where possible

---

## Implementation Plan

### Phase 1: Detection & Redaction (Week 1-2)

```yaml
Week 1: Sensitive Data Detection
  Tasks:
    - Implement SensitiveDataDetector
    - Define regex patterns
    - Test detection accuracy
    - Tune confidence thresholds

  Deliverables:
    - agentpm/core/security/detector.py
    - Pattern library
    - Detection tests-BAK (>95% accuracy)

  Success Criteria:
    - Detects common secrets (API keys, passwords)
    - False positive rate <5%
    - Detection time <50ms per text

Week 2: Data Redaction
  Tasks:
    - Implement DataRedactionService
    - Redaction placeholder format
    - Integration with evidence capture
    - Integration with session logging

  Deliverables:
    - agentpm/core/security/redaction.py
    - Redaction tests-BAK
    - Evidence/session integration

  Success Criteria:
    - Redaction preserves context
    - No original sensitive data stored
    - Hashes enable verification
```

### Phase 2: Encryption & Access Control (Week 3-4)

```yaml
Week 3: Encryption at Rest
  Tasks:
    - Implement EncryptionService
    - Encrypt sensitive database fields
    - Key management system
    - Migration for existing data

  Deliverables:
    - agentpm/core/security/encryption.py
    - Database field encryption
    - Key rotation support

  Success Criteria:
    - All sensitive fields encrypted
    - Decryption only on authorized access
    - Performance <20ms overhead

Week 4: Access Control
  Tasks:
    - Implement AccessControlService
    - Define RBAC roles
    - Access control checks
    - Audit logging for access

  Deliverables:
    - agentpm/core/security/access_control.py
    - RBAC implementation
    - Access audit trail

  Success Criteria:
    - Unauthorized access prevented
    - All access logged
    - Roles enforce least privilege
```

### Phase 3: GDPR Compliance (Week 5-6)

```yaml
Week 5: Data Subject Rights
  Tasks:
    - Implement GDPRComplianceService
    - Data export functionality
    - Data deletion functionality
    - Consent management

  Deliverables:
    - agentpm/core/compliance/gdpr.py
    - CLI: apm gdpr export/delete
    - Compliance dashboard

  Success Criteria:
    - Data export works (GDPR Article 20)
    - Data deletion works (GDPR Article 17)
    - Audit trail for compliance

Week 6: Compliance Reporting
  Tasks:
    - Generate compliance reports
    - Privacy policy templates
    - Data retention policies
    - Compliance dashboard

  Deliverables:
    - Compliance report generation
    - Policy templates
    - Dashboard (CLI/web)

  Success Criteria:
    - Can generate SOC 2 reports
    - Can generate GDPR compliance reports
    - Audit-ready
```

### Phase 4: Integration & Testing (Week 7-8)

```yaml
Week 7: System Integration
  Tasks:
    - Integrate security across all components
    - Evidence capture with redaction
    - Session logging with filtering
    - Context assembly with file exclusion

  Deliverables:
    - Security integration across AIPM
    - Updated all services
    - Security tests-BAK

  Success Criteria:
    - All sensitive data protected
    - No security regressions
    - Performance acceptable

Week 8: Security Testing & Audit
  Tasks:
    - Penetration testing
    - Security audit
    - Compliance review
    - Documentation

  Deliverables:
    - Security test report
    - Penetration test results
    - Compliance certification (if applicable)
    - Security documentation

  Success Criteria:
    - No critical vulnerabilities
    - Compliance requirements met
    - Documentation complete
```

---

## Usage Examples

### Example 1: Automatic Redaction in Evidence

```python
# Agent captures evidence from blog post
evidence_text = """
To integrate with Stripe, use your API key:
sk_test_51abc123def456ghi789jkl012mno345pqr678stu901vwx234yz

For production, use: sk_live_51abc...
"""

# BEFORE STORAGE: Auto-detect and redact
detector = SensitiveDataDetector()
matches = detector.detect(evidence_text)
# Found: 2 API keys (severity: critical)

redaction_service = DataRedactionService()
redacted = redaction_service.redact(evidence_text)

# STORED IN DATABASE:
"""
To integrate with Stripe, use your API key:
[REDACTED:API_KEY:hash_a1b2c3d4]

For production, use: [REDACTED:API_KEY:hash_e5f6g7h8]
"""

# Original keys NEVER stored
# Context preserved (knows it's about API keys)
# Compliance maintained
```

### Example 2: File Exclusion from Context

```python
# Agent building context for authentication task
task = db.query(Task).get(task_id=42)

# Files involved in task
files = [
    "auth/jwt_service.py",
    "auth/middleware.py",
    "config/settings.py",
    "config/.env.production",  # Sensitive!
    "auth/tokens.py"
]

# SECURITY FILTER
filter_service = SensitiveFileFilter()
safe_files = filter_service.filter_context_files(files)

# Result:
# safe_files = [
#     "auth/jwt_service.py",
#     "auth/middleware.py",
#     "config/settings.py",
#     "auth/tokens.py"
# ]
# .env.production EXCLUDED (logged in audit)

# Context only includes safe files
# Agent never sees production credentials
```

### Example 3: GDPR Data Export

```bash
# User requests data export
apm gdpr export user@email.com

# Output:
# 📦 Exporting data for user@email.com...
#
# Found data:
#   • Decisions: 45
#   • Evidence entries: 120
#   • Sessions: 89
#   • Documents: 23
#   • Learnings: 156
#
# ✅ Exported to: /tmp/aipm-gdpr-export-user-20251012.json
# 📊 Total records: 433
# 🔒 Sensitive data redacted in export
#
# User can:
# - Review all data collected
# - Request corrections
# - Request deletion

# User requests deletion
apm gdpr delete user@email.com

# Output:
# ⚠️  WARNING: This will permanently delete all data for user@email.com
#
# Data to be deleted:
#   • Decisions: 45
#   • Evidence entries: 120
#   • Sessions: 89
#   • Documents: 23
#   • Learnings: 156
#
# This action is IRREVERSIBLE.
# Type email to confirm: user@email.com
# Confirm deletion? [yes/NO]: yes
#
# 🗑️  Deleting data...
# ✅ Deleted 433 records
# 📋 Audit log entry created
```

---

## Related Documents

- **ADR-004**: Evidence Storage and Retrieval (redaction integration)
- **ADR-007**: Human-in-the-Loop Workflows (security review)
- **AIPM-V2-COMPLETE-SPECIFICATION.md**: Main specification

---

## Decision Log

| Date | Decision | Rationale |
|------|----------|-----------|
| 2025-10-12 | Multi-layer security (detect, redact, encrypt, control) | Defense in depth |
| 2025-10-12 | Automatic redaction before storage | Prevent accidental exposure |
| 2025-10-12 | Sensitive file exclusion patterns | Prevent credentials in context |
| 2025-10-12 | GDPR compliance built-in | European market requirement |
| 2025-10-12 | Role-based access control | Least privilege principle |

---

**Status:** Proposed (awaiting review)
**Next Steps:**
1. Security review with security team
2. Legal review for GDPR compliance
3. Prototype sensitive data detection
4. Approve and begin implementation

**Owner:** AIPM Security Team
**Reviewers:** Security Lead, Legal Counsel
**Last Updated:** 2025-10-12
