# Detection Pack Security Requirements

**Document Version**: 1.0.0
**Status**: Security Analysis
**Work Item**: #148
**Task**: #977
**Created**: 2025-10-24
**Architecture Reference**: [Detection Pack Architecture](/Users/nigelcopley/.project_manager/aipm-v2/docs/architecture/detection-pack-architecture.md)

---

## Executive Summary

This document defines comprehensive security and compliance requirements for the APM (Agent Project Manager) Detection Pack Enhancement. The detection system will perform static analysis, dependency graph generation, SBOM creation, and architecture fitness testing on potentially untrusted codebases. This introduces significant security risks that must be mitigated through defense-in-depth security controls.

**Risk Level**: HIGH - The system parses and analyzes arbitrary source code, which presents code execution, path traversal, resource exhaustion, and data exfiltration risks.

**Security Posture**: Zero-trust architecture with multiple security layers (validation, sandboxing, resource limits, audit logging).

---

## 1. Threat Model

### 1.1 Assets to Protect

**Critical Assets**:
1. **Host System**: The machine running AIPM detection commands
2. **AIPM Database**: Project metadata, cached analysis results, sensitive configurations
3. **User Data**: Project source code, credentials, proprietary algorithms
4. **System Resources**: CPU, memory, disk I/O, network bandwidth
5. **CI/CD Pipeline**: Automated build and deployment systems

**Asset Criticality**:
- Host system compromise: CRITICAL (complete system takeover)
- Database compromise: HIGH (metadata exposure, cache poisoning)
- User data exposure: HIGH (intellectual property theft, credential leakage)
- Resource exhaustion: MEDIUM (denial of service, pipeline delays)

### 1.2 Threat Actors

**External Attackers**:
- **Malicious Package Authors**: Supply chain attacks via poisoned dependencies
- **Repository Attackers**: Compromised open-source repositories
- **Competitors**: Industrial espionage through malicious test projects

**Internal Threats**:
- **Accidental Misuse**: Developers scanning untrusted code without precautions
- **Insider Threats**: Malicious employees attempting privilege escalation
- **Configuration Errors**: Insecure deployment configurations

**Automated Threats**:
- **CI/CD Exploitation**: Attackers targeting automated analysis pipelines
- **Bot Attacks**: Automated exploitation of detection vulnerabilities

### 1.3 Attack Vectors

#### AV-001: Code Execution via AST Parsing

**Attack Scenario**:
```python
# Malicious Python file with crafted AST payload
# Attacker exploits vulnerable AST parsing
__import__('os').system('rm -rf /')  # Executed during parse if using eval()
```

**Threat**: Arbitrary code execution during static analysis
**Impact**: CRITICAL - Complete system compromise
**Likelihood**: HIGH - Common vulnerability in analysis tools
**MITIGATIONS**: See SEC-001, SEC-002

#### AV-002: Path Traversal via File Access

**Attack Scenario**:
```python
# Malicious project structure
project/
├── ../../../../etc/passwd  # Symlink to system files
└── analysis_target.py
```

**Threat**: Unauthorized file system access outside project directory
**Impact**: HIGH - Sensitive file disclosure, configuration exposure
**Likelihood**: MEDIUM - Requires crafted project structure
**MITIGATIONS**: See SEC-003

#### AV-003: Resource Exhaustion (DoS)

**Attack Scenario**:
```python
# Malicious file with infinite complexity
def recursive_hell():
    while True:
        for i in range(999999):
            for j in range(999999):
                yield from recursive_hell()
```

**Threat**: Memory exhaustion, CPU starvation, disk space consumption
**Impact**: MEDIUM - Denial of service, CI/CD pipeline failure
**Likelihood**: HIGH - Easy to craft malicious inputs
**MITIGATIONS**: See SEC-004, SEC-005

#### AV-004: Graph Injection Attacks

**Attack Scenario**:
```python
# Malicious dependency graph with billions of nodes
# Causes memory exhaustion when building NetworkX graph
for i in range(10**9):
    graph.add_node(f"node_{i}")
```

**Threat**: Memory exhaustion through graph complexity
**Impact**: MEDIUM - Service disruption, analysis failure
**Likelihood**: MEDIUM - Requires understanding of graph limits
**MITIGATIONS**: See SEC-006

#### AV-005: Cache Poisoning

**Attack Scenario**:
```python
# Attacker provides malicious cached AST
# Database cache stores poisoned analysis results
# Subsequent analyses use compromised cache
```

**Threat**: Persistent compromise through cached malicious data
**Impact**: HIGH - Analysis integrity compromise, false security reports
**Likelihood**: LOW - Requires database write access
**MITIGATIONS**: See SEC-007

#### AV-006: Dependency Confusion

**Attack Scenario**:
```python
# Malicious package with same name as internal library
# SBOM generation pulls metadata from attacker-controlled source
# License scanner fetches malicious content
```

**Threat**: Supply chain attack through dependency metadata
**Impact**: MEDIUM - Incorrect SBOM, license compliance issues
**Likelihood**: MEDIUM - Known attack vector
**MITIGATIONS**: See SEC-008

#### AV-007: Sensitive Data Exfiltration

**Attack Scenario**:
```python
# Analysis captures credentials from code
API_KEY = "sk_live_abc123..."  # Stored in AST cache
# Attacker with cache access extracts production credentials
```

**Threat**: Credential leakage through analysis artifacts
**Impact**: CRITICAL - Production credential exposure
**Likelihood**: HIGH - Common pattern in codebases
**MITIGATIONS**: See SEC-009, SEC-010

#### AV-008: Malicious Fitness Policies

**Attack Scenario**:
```python
# Malicious fitness policy with code execution
validation_logic = "exec('__import__(\"os\").system(\"whoami\")')"
```

**Threat**: Code execution through policy evaluation
**Impact**: CRITICAL - Arbitrary code execution
**Likelihood**: MEDIUM - Requires policy write access
**MITIGATIONS**: See SEC-011

---

## 2. Security Requirements

### SEC-001: Safe AST Parsing (Code Execution Prevention)

**Requirement**: MUST use safe AST parsing methods that do not execute code
**Priority**: CRITICAL
**Enforcement**: BLOCK

**Implementation Controls**:

1. **Use Safe Parsing APIs Only**:
   ```python
   # SAFE: Python built-in ast module
   import ast
   tree = ast.parse(source_code)  # No code execution

   # UNSAFE: Avoid these
   eval(source_code)      # NEVER - executes code
   exec(source_code)      # NEVER - executes code
   compile(source_code, mode='exec')  # DANGEROUS - can execute
   ```

2. **Disable Code Compilation**:
   - Never compile AST nodes to bytecode
   - Never use `mode='exec'` or `mode='eval'` in compile()
   - Avoid dynamic imports during parsing

3. **Sandbox Parser Execution**:
   - Parse in isolated process if possible
   - Use seccomp/AppArmor on Linux
   - Consider containerization for CI/CD

**Testing Requirements**:
- Test with malicious Python files containing:
  - `__import__('os').system('whoami')`
  - `eval(input())`
  - `exec(open('/etc/passwd').read())`
- Verify NO code execution occurs during parsing
- Monitor for subprocess creation during tests

**Acceptance Criteria**:
- [ ] No eval(), exec(), or compile() used in parsing code
- [ ] Static analysis confirms no dynamic execution paths
- [ ] Security tests pass with malicious input files
- [ ] Code review confirms safe parsing only

---

### SEC-002: Subprocess Safety (External Tool Execution)

**Requirement**: If external tools are invoked (e.g., `radon`, `bandit`), MUST sanitize inputs and validate outputs
**Priority**: HIGH
**Enforcement**: BLOCK

**Implementation Controls**:

1. **Input Sanitization**:
   ```python
   import shlex
   import subprocess

   # SAFE: Whitelist-based validation
   ALLOWED_TOOLS = {'radon', 'bandit', 'mypy'}

   def safe_execute_tool(tool: str, file_path: str):
       if tool not in ALLOWED_TOOLS:
           raise ValueError(f"Tool {tool} not allowed")

       # Validate file path is within project
       file_path = safe_relative_path(PROJECT_ROOT, file_path)

       # Use list args (not shell=True)
       result = subprocess.run(
           [tool, file_path],
           capture_output=True,
           timeout=30,  # Timeout protection
           shell=False,  # Never shell=True
           check=False
       )
       return result.stdout
   ```

2. **Output Validation**:
   - Validate tool outputs match expected format
   - Reject outputs with suspicious content
   - Limit output size (max 10MB)

3. **Timeout Protection**:
   - Set subprocess timeout (30 seconds default)
   - Kill subprocess on timeout
   - Log timeout events

**Testing Requirements**:
- Test with malicious file paths: `../../etc/passwd`
- Test with shell injection attempts: `file.py; rm -rf /`
- Verify timeout kills long-running processes
- Verify subprocess never gains elevated privileges

**Acceptance Criteria**:
- [ ] All subprocess calls use `shell=False`
- [ ] Input validation prevents path traversal
- [ ] Timeouts configured for all subprocess calls
- [ ] Security tests verify injection resistance

---

### SEC-003: Path Traversal Prevention (File System Access)

**Requirement**: MUST validate all file paths are within project directory and reject symlinks to sensitive locations
**Priority**: CRITICAL
**Enforcement**: BLOCK

**Implementation Controls**:

1. **Path Validation Function**:
   ```python
   from pathlib import Path

   def safe_relative_path(base: Path, target: Path) -> Path:
       """
       Ensure target is within base directory.

       Prevents:
       - Directory traversal (../..)
       - Absolute paths (/etc/passwd)
       - Symlinks outside project
       """
       base = base.resolve()
       target_resolved = target.resolve()

       # Check target is under base
       try:
           target_resolved.relative_to(base)
       except ValueError:
           raise SecurityError(
               f"Path traversal detected: {target} outside {base}"
           )

       # Check for symlinks escaping project
       if target_resolved.is_symlink():
           link_target = target_resolved.readlink()
           if link_target.is_absolute():
               raise SecurityError(
                   f"Absolute symlink not allowed: {target} -> {link_target}"
               )
           # Recursively validate symlink target
           return safe_relative_path(base, link_target)

       return target_resolved
   ```

2. **Symlink Handling**:
   - Resolve symlinks before access
   - Reject absolute symlinks
   - Reject symlinks pointing outside project
   - Log all symlink access attempts

3. **File System Boundaries**:
   - Never access files outside project root
   - Exception: System libraries (read-only, validated)
   - Block access to sensitive directories:
     - `/etc/*`
     - `/home/*/.ssh/*`
     - `/home/*/.aws/*`
     - `/root/*`

**Testing Requirements**:
- Test path traversal: `../../../../../../etc/passwd`
- Test absolute paths: `/etc/passwd`
- Test symlink attacks: `ln -s /etc/passwd malicious.py`
- Test Unicode normalization attacks: `..%2F..%2Fetc%2Fpasswd`

**Acceptance Criteria**:
- [ ] All file access uses `safe_relative_path()` validation
- [ ] Symlinks outside project are rejected
- [ ] Path traversal attempts are blocked and logged
- [ ] Security tests verify path traversal prevention

---

### SEC-004: Resource Limits (DoS Prevention)

**Requirement**: MUST enforce resource limits to prevent denial of service attacks
**Priority**: HIGH
**Enforcement**: BLOCK

**Implementation Controls**:

1. **File Size Limits**:
   ```python
   MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB per file
   MAX_PROJECT_SIZE = 500 * 1024 * 1024  # 500MB total
   MAX_FILES = 10_000  # Max files to analyze

   def validate_file_size(file_path: Path):
       size = file_path.stat().st_size
       if size > MAX_FILE_SIZE:
           raise ResourceLimitError(
               f"File too large: {size} bytes (max {MAX_FILE_SIZE})"
           )
   ```

2. **Graph Complexity Limits**:
   ```python
   MAX_GRAPH_NODES = 10_000
   MAX_GRAPH_EDGES = 50_000
   MAX_GRAPH_DEPTH = 100

   def validate_graph_size(graph: DependencyGraph):
       if len(graph.nodes) > MAX_GRAPH_NODES:
           raise ResourceLimitError(
               f"Graph too large: {len(graph.nodes)} nodes"
           )
       if len(graph.edges) > MAX_GRAPH_EDGES:
           raise ResourceLimitError(
               f"Too many edges: {len(graph.edges)}"
           )
   ```

3. **Memory Limits**:
   ```python
   import resource

   # Set memory limit (1GB for analysis process)
   resource.setrlimit(
       resource.RLIMIT_AS,
       (1024 * 1024 * 1024, 1024 * 1024 * 1024)
   )
   ```

4. **Timeout Limits**:
   ```python
   ANALYSIS_TIMEOUT = 120  # 2 minutes per analysis
   PARSE_TIMEOUT = 30  # 30 seconds per file

   @timeout(PARSE_TIMEOUT)
   def parse_file(file_path: Path):
       # Parsing with timeout protection
       pass
   ```

**Testing Requirements**:
- Test with 10MB+ files (should reject)
- Test with 100,000 file projects (should reject or subsample)
- Test with deeply recursive structures (should timeout)
- Monitor memory usage during testing

**Acceptance Criteria**:
- [ ] File size limits enforced
- [ ] Graph complexity limits enforced
- [ ] Memory limits prevent OOM crashes
- [ ] Timeouts prevent indefinite hangs

---

### SEC-005: Complexity Analysis Limits

**Requirement**: MUST limit complexity of code constructs analyzed to prevent algorithmic complexity attacks
**Priority**: MEDIUM
**Enforcement**: WARNING

**Implementation Controls**:

1. **AST Depth Limits**:
   ```python
   MAX_AST_DEPTH = 50  # Max nesting depth

   def check_ast_depth(node, depth=0):
       if depth > MAX_AST_DEPTH:
           raise ComplexityError(
               f"AST too deep: {depth} levels (max {MAX_AST_DEPTH})"
           )
       for child in ast.iter_child_nodes(node):
           check_ast_depth(child, depth + 1)
   ```

2. **Cyclomatic Complexity Limits**:
   ```python
   MAX_COMPLEXITY = 100  # McCabe complexity

   def validate_complexity(complexity: int):
       if complexity > MAX_COMPLEXITY:
           logger.warning(
               f"High complexity detected: {complexity} "
               f"(max {MAX_COMPLEXITY})"
           )
           # Warning only, don't block analysis
   ```

3. **Import Chain Limits**:
   ```python
   MAX_IMPORT_DEPTH = 20  # Max import chain depth

   def trace_imports(module, visited=None, depth=0):
       if depth > MAX_IMPORT_DEPTH:
           raise ComplexityError("Import chain too deep")
       # Track imports recursively
   ```

**Testing Requirements**:
- Test with deeply nested code (50+ levels)
- Test with high cyclomatic complexity (>100)
- Test with circular import chains

**Acceptance Criteria**:
- [ ] AST depth limits prevent stack overflow
- [ ] Complexity warnings generated for high-complexity code
- [ ] Import chain limits prevent infinite loops

---

### SEC-006: Graph Security (NetworkX Safety)

**Requirement**: MUST validate graph structures before NetworkX operations to prevent graph-based attacks
**Priority**: HIGH
**Enforcement**: BLOCK

**Implementation Controls**:

1. **Pre-Construction Validation**:
   ```python
   def build_safe_graph(nodes: Set[str], edges: List[DependencyEdge]):
       # Validate before building NetworkX graph
       if len(nodes) > MAX_GRAPH_NODES:
           raise SecurityError(f"Too many nodes: {len(nodes)}")

       if len(edges) > MAX_GRAPH_EDGES:
           raise SecurityError(f"Too many edges: {len(edges)}")

       # Check for malicious edge patterns
       for edge in edges:
           if edge.source not in nodes or edge.target not in nodes:
               raise SecurityError("Invalid edge: references unknown node")

       # Build graph safely
       G = nx.DiGraph()
       G.add_nodes_from(nodes)
       G.add_edges_from([(e.source, e.target) for e in edges])
       return G
   ```

2. **Algorithm Timeout Protection**:
   ```python
   @timeout(10)
   def detect_cycles_safe(graph: nx.DiGraph):
       # NetworkX cycle detection with timeout
       return list(nx.simple_cycles(graph))
   ```

3. **Memory-Aware Operations**:
   ```python
   def analyze_graph_safe(graph: nx.DiGraph):
       # Check graph size before expensive operations
       if len(graph) > 1000:
           # Skip expensive algorithms for large graphs
           logger.warning("Skipping complex analysis for large graph")
           return None

       # Perform analysis
       return nx.betweenness_centrality(graph)
   ```

**Testing Requirements**:
- Test with 100,000+ node graphs (should reject)
- Test with fully connected graphs (n*(n-1) edges)
- Test with circular dependency graphs
- Monitor memory during graph operations

**Acceptance Criteria**:
- [ ] Graph size validated before construction
- [ ] Expensive algorithms have timeout protection
- [ ] Large graphs handled gracefully (reject or subsample)

---

### SEC-007: Cache Integrity (Tamper Prevention)

**Requirement**: MUST protect cached analysis results from tampering
**Priority**: HIGH
**Enforcement**: BLOCK

**Implementation Controls**:

1. **Cache Hashing**:
   ```python
   import hashlib
   import hmac

   def cache_with_integrity(data: str, file_hash: str) -> dict:
       """Store cached data with integrity protection"""
       cache_entry = {
           'data': data,
           'file_hash': file_hash,
           'timestamp': datetime.now(),
       }

       # Generate HMAC for integrity
       cache_json = json.dumps(cache_entry, sort_keys=True)
       hmac_key = get_cache_hmac_key()  # From secure config
       integrity_hash = hmac.new(
           hmac_key.encode(),
           cache_json.encode(),
           hashlib.sha256
       ).hexdigest()

       cache_entry['integrity_hash'] = integrity_hash
       return cache_entry

   def verify_cache_integrity(cache_entry: dict) -> bool:
       """Verify cached data has not been tampered with"""
       stored_hash = cache_entry.pop('integrity_hash')
       cache_json = json.dumps(cache_entry, sort_keys=True)

       hmac_key = get_cache_hmac_key()
       expected_hash = hmac.new(
           hmac_key.encode(),
           cache_json.encode(),
           hashlib.sha256
       ).hexdigest()

       return hmac.compare_digest(stored_hash, expected_hash)
   ```

2. **File Hash Verification**:
   ```python
   def get_cache_safe(file_path: Path) -> Optional[ASTGraph]:
       # Calculate current file hash
       current_hash = hashlib.sha256(file_path.read_bytes()).hexdigest()

       # Retrieve cache
       cache_entry = db.query_cache(file_path)
       if not cache_entry:
           return None

       # Verify file hash matches
       if cache_entry['file_hash'] != current_hash:
           logger.warning(f"Cache invalid: file modified {file_path}")
           return None

       # Verify cache integrity
       if not verify_cache_integrity(cache_entry):
           logger.error(f"Cache tampered: {file_path}")
           db.delete_cache(file_path)
           return None

       return cache_entry['data']
   ```

3. **Cache Expiration**:
   ```python
   CACHE_TTL = 86400  # 24 hours

   def is_cache_expired(cache_timestamp: datetime) -> bool:
       age = (datetime.now() - cache_timestamp).total_seconds()
       return age > CACHE_TTL
   ```

**Testing Requirements**:
- Test cache tampering detection (modify cached data)
- Test file modification invalidates cache
- Test cache expiration (24 hour TTL)
- Test HMAC key rotation

**Acceptance Criteria**:
- [ ] All cached data includes integrity hash
- [ ] Tampered cache entries are detected and rejected
- [ ] File modification invalidates cache
- [ ] Cache expires after 24 hours

---

### SEC-008: Dependency Verification (Supply Chain Security)

**Requirement**: MUST verify package metadata authenticity before SBOM generation
**Priority**: MEDIUM
**Enforcement**: WARNING

**Implementation Controls**:

1. **Package Signature Verification**:
   ```python
   def verify_package_signature(package_name: str, version: str):
       """Verify package integrity using PyPI signatures"""
       # Query PyPI for package metadata
       metadata = query_pypi_api(package_name, version)

       # Verify GPG signature if available
       if 'signatures' in metadata:
           verify_gpg_signature(metadata['signatures'])
       else:
           logger.warning(
               f"No signature for {package_name}=={version}"
           )
   ```

2. **License Source Validation**:
   ```python
   TRUSTED_LICENSE_SOURCES = {
       'pypi': 'https://pypi.org',
       'github': 'https://github.com',
       'spdx': 'https://spdx.org/licenses/'
   }

   def fetch_license_safe(url: str) -> str:
       # Validate URL is from trusted source
       parsed = urllib.parse.urlparse(url)
       trusted = any(
           parsed.netloc.endswith(domain)
           for domain in TRUSTED_LICENSE_SOURCES.values()
       )

       if not trusted:
           raise SecurityError(
               f"Untrusted license source: {url}"
           )

       # Fetch with timeout and size limit
       response = requests.get(url, timeout=10)
       if len(response.content) > 1024 * 1024:  # 1MB
           raise SecurityError("License file too large")

       return response.text
   ```

3. **Dependency Confusion Prevention**:
   ```python
   def resolve_package_source(package_name: str):
       """Prefer internal/private packages over public"""
       # Check internal registry first
       if exists_in_internal_registry(package_name):
           return 'internal'

       # Then check public PyPI
       if exists_on_pypi(package_name):
           return 'pypi'

       raise PackageNotFoundError(package_name)
   ```

**Testing Requirements**:
- Test with unsigned packages (should warn)
- Test with packages from untrusted sources (should reject)
- Test dependency confusion scenarios

**Acceptance Criteria**:
- [ ] Package signatures verified when available
- [ ] License sources validated before fetching
- [ ] Internal packages prioritized over public
- [ ] Warnings generated for unverified packages

---

### SEC-009: Sensitive Data Redaction (Credential Protection)

**Requirement**: MUST redact sensitive data from analysis artifacts before storage
**Priority**: CRITICAL
**Enforcement**: BLOCK

**Implementation Controls**:

1. **Sensitive Data Detection**:
   ```python
   import re

   SENSITIVE_PATTERNS = {
       'api_key': re.compile(r'(sk|pk)_(test|live)_[a-zA-Z0-9]{24,}'),
       'aws_key': re.compile(r'AKIA[0-9A-Z]{16}'),
       'jwt': re.compile(r'eyJ[a-zA-Z0-9_-]+\.[a-zA-Z0-9_-]+\.'),
       'password': re.compile(r'(password|passwd|pwd)\s*[:=]\s*["\']?([^"\'\s]+)'),
       'connection_string': re.compile(
           r'(postgres|mysql|mongodb)://[^\s]+'
       ),
       'private_key': re.compile(r'-----BEGIN.*PRIVATE KEY-----'),
   }

   def detect_sensitive_data(text: str) -> List[Match]:
       matches = []
       for data_type, pattern in SENSITIVE_PATTERNS.items():
           for match in pattern.finditer(text):
               matches.append({
                   'type': data_type,
                   'start': match.start(),
                   'end': match.end(),
                   'value': match.group()
               })
       return matches
   ```

2. **Redaction Before Storage**:
   ```python
   def redact_sensitive_data(text: str) -> str:
       """Redact sensitive data before storing in cache/database"""
       matches = detect_sensitive_data(text)

       # Sort reverse to avoid offset issues
       matches.sort(key=lambda m: m['start'], reverse=True)

       redacted = text
       for match in matches:
           # Generate hash for verification (not storage)
           value_hash = hashlib.sha256(
               match['value'].encode()
           ).hexdigest()[:8]

           # Replace with placeholder
           placeholder = f"[REDACTED:{match['type'].upper()}:{value_hash}]"
           redacted = (
               redacted[:match['start']] +
               placeholder +
               redacted[match['end']:]
           )

           # Log redaction event
           logger.warning(
               f"Redacted {match['type']} from analysis artifact"
           )

       return redacted
   ```

3. **File Exclusion Patterns**:
   ```python
   SENSITIVE_FILE_PATTERNS = [
       r'\.env(\..+)?$',
       r'credentials?\.(json|yaml|yml)$',
       r'secrets?\.(json|yaml|yml)$',
       r'.*\.(pem|key|p12|pfx)$',
       r'\.aws/credentials$',
       r'\.ssh/id_.*$',
   ]

   def is_sensitive_file(file_path: Path) -> bool:
       """Check if file should be excluded from analysis"""
       file_name = file_path.name
       for pattern in SENSITIVE_FILE_PATTERNS:
           if re.match(pattern, file_name, re.IGNORECASE):
               logger.warning(f"Excluding sensitive file: {file_path}")
               return True
       return False
   ```

**Testing Requirements**:
- Test with files containing API keys (should redact)
- Test with .env files (should exclude)
- Test with private keys (should redact)
- Verify no credentials stored in cache/database

**Acceptance Criteria**:
- [ ] Sensitive patterns detected before storage
- [ ] Credentials redacted from all analysis artifacts
- [ ] Sensitive files excluded from analysis
- [ ] Redaction events logged for audit

---

### SEC-010: Cache Encryption (Data Protection at Rest)

**Requirement**: SHOULD encrypt sensitive cached data at rest
**Priority**: MEDIUM
**Enforcement**: WARNING

**Implementation Controls**:

1. **Field-Level Encryption**:
   ```python
   from cryptography.fernet import Fernet

   def get_encryption_key() -> bytes:
       """Get encryption key from environment or key vault"""
       key = os.environ.get('AIPM_CACHE_ENCRYPTION_KEY')
       if not key:
           logger.warning("No encryption key configured")
           return None
       return key.encode()

   def encrypt_cache_field(plaintext: str) -> str:
       """Encrypt sensitive cache field"""
       key = get_encryption_key()
       if not key:
           return plaintext  # No encryption if key not configured

       cipher = Fernet(key)
       encrypted = cipher.encrypt(plaintext.encode())
       return base64.b64encode(encrypted).decode()

   def decrypt_cache_field(ciphertext: str) -> str:
       """Decrypt cache field on authorized read"""
       key = get_encryption_key()
       if not key:
           return ciphertext

       cipher = Fernet(key)
       encrypted = base64.b64decode(ciphertext.encode())
       decrypted = cipher.decrypt(encrypted)
       return decrypted.decode()
   ```

2. **Encryption Key Management**:
   ```bash
   # Generate encryption key
   python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"

   # Store in environment
   export AIPM_CACHE_ENCRYPTION_KEY="<generated_key>"

   # Or use key vault (AWS KMS, HashiCorp Vault)
   ```

**Testing Requirements**:
- Test encryption/decryption round-trip
- Test with missing encryption key (should warn)
- Verify encrypted data in database

**Acceptance Criteria**:
- [ ] Encryption key management documented
- [ ] Sensitive cache fields encrypted when key available
- [ ] Decryption only on authorized access
- [ ] Key rotation supported

---

### SEC-011: Policy Validation (Safe Policy Execution)

**Requirement**: MUST validate fitness policies before execution to prevent code injection
**Priority**: CRITICAL
**Enforcement**: BLOCK

**Implementation Controls**:

1. **Policy Sandboxing**:
   ```python
   import ast

   ALLOWED_OPERATIONS = {
       'Add', 'Sub', 'Mult', 'Div', 'Mod',  # Math
       'Eq', 'NotEq', 'Lt', 'LtE', 'Gt', 'GtE',  # Comparison
       'And', 'Or', 'Not',  # Boolean
   }

   def validate_policy_ast(policy_code: str):
       """Validate policy contains only safe operations"""
       try:
           tree = ast.parse(policy_code)
       except SyntaxError as e:
           raise PolicyValidationError(f"Invalid policy syntax: {e}")

       # Check for dangerous operations
       for node in ast.walk(tree):
           if isinstance(node, ast.Call):
               # Block function calls (prevents exec, eval, etc.)
               raise PolicyValidationError(
                   "Function calls not allowed in policies"
               )

           if isinstance(node, ast.Import):
               raise PolicyValidationError(
                   "Imports not allowed in policies"
               )

           if isinstance(node, (ast.Exec, ast.Eval)):
               raise PolicyValidationError(
                   "exec/eval not allowed in policies"
               )
   ```

2. **Restricted Evaluation**:
   ```python
   def execute_policy_safe(policy: Policy, context: dict) -> bool:
       """Execute policy in restricted environment"""
       # Validate policy first
       validate_policy_ast(policy.validation_logic)

       # Create restricted globals (no builtins)
       safe_globals = {
           '__builtins__': {},
           'context': context,  # Read-only context
       }

       # Execute with timeout
       try:
           with timeout(5):  # 5 second max
               result = eval(
                   policy.validation_logic,
                   safe_globals,
                   {}
               )
               return bool(result)
       except Exception as e:
           logger.error(f"Policy execution failed: {e}")
           return False
   ```

3. **Policy Approval Workflow**:
   ```python
   def create_policy(policy: Policy, author: str):
       """Create policy with approval workflow"""
       # New policies start as draft
       policy.status = 'draft'
       policy.author = author
       policy.created_at = datetime.now()

       # Validate policy
       validate_policy_ast(policy.validation_logic)

       # Require review before enabling
       policy.enabled = False

       db.add(policy)
       db.commit()

       logger.info(
           f"Policy {policy.policy_id} created by {author}, "
           f"awaiting review"
       )
   ```

**Testing Requirements**:
- Test with malicious policies containing `eval()`
- Test with policies containing imports
- Test with policies containing function calls
- Verify timeout kills long-running policies

**Acceptance Criteria**:
- [ ] Policy validation prevents code injection
- [ ] Policy execution is sandboxed
- [ ] Policy approval workflow enforced
- [ ] Execution timeout prevents hangs

---

## 3. Input Validation Requirements

### INV-001: CLI Input Validation

**Requirement**: Validate all CLI inputs before processing
**Priority**: HIGH

**Validation Rules**:

```python
def validate_cli_inputs(
    project_path: str,
    output_format: str,
    filters: List[str]
):
    # Project path validation
    path = Path(project_path)
    if not path.exists():
        raise ValueError(f"Project path does not exist: {project_path}")

    if not path.is_dir():
        raise ValueError(f"Project path is not a directory: {project_path}")

    # Output format validation (whitelist)
    ALLOWED_FORMATS = {'json', 'yaml', 'xml', 'table', 'cyclonedx', 'spdx'}
    if output_format not in ALLOWED_FORMATS:
        raise ValueError(
            f"Invalid format: {output_format}. "
            f"Allowed: {ALLOWED_FORMATS}"
        )

    # Filter validation (prevent injection)
    for filter_expr in filters:
        if not re.match(r'^[a-zA-Z0-9_\-\.]+$', filter_expr):
            raise ValueError(
                f"Invalid filter expression: {filter_expr}. "
                f"Only alphanumeric, dash, underscore allowed"
            )
```

**Acceptance Criteria**:
- [ ] All CLI inputs validated before use
- [ ] Invalid inputs rejected with clear errors
- [ ] Injection attempts detected and blocked

---

### INV-002: File Content Validation

**Requirement**: Validate file content before parsing
**Priority**: MEDIUM

**Validation Rules**:

```python
def validate_file_content(file_path: Path):
    # Check file size
    size = file_path.stat().st_size
    if size > MAX_FILE_SIZE:
        raise FileSizeError(f"File too large: {size} bytes")

    # Check file encoding (prevent binary files)
    try:
        content = file_path.read_text(encoding='utf-8')
    except UnicodeDecodeError:
        logger.warning(f"Skipping binary file: {file_path}")
        return None

    # Check for null bytes (indicator of binary)
    if '\x00' in content:
        logger.warning(f"Skipping file with null bytes: {file_path}")
        return None

    # Check line count (prevent memory bombs)
    lines = content.count('\n')
    if lines > 100_000:
        raise ComplexityError(f"File too many lines: {lines}")

    return content
```

**Acceptance Criteria**:
- [ ] File size validated before reading
- [ ] Binary files skipped gracefully
- [ ] Malformed files handled safely

---

## 4. Compliance Requirements

### COMP-001: GDPR Compliance (Data Privacy)

**Requirement**: Comply with GDPR data protection requirements
**Priority**: HIGH (if operating in EU)

**Implementation Controls**:

1. **Data Minimization**:
   - Only collect necessary code metadata
   - Don't store full source code in cache (store hashes)
   - Purge old analysis results (30-day retention)

2. **Right to Erasure**:
   ```bash
   # Provide data deletion command
   apm detect cache clear --project <path>
   apm detect cache purge --older-than 30d
   ```

3. **Data Protection by Design**:
   - Encrypt cache at rest (SEC-010)
   - Redact sensitive data (SEC-009)
   - Audit all data access

**Acceptance Criteria**:
- [ ] Data retention policy implemented (30 days)
- [ ] Cache deletion commands available
- [ ] Sensitive data redacted before storage
- [ ] Privacy policy documented

---

### COMP-002: License Compliance (SBOM)

**Requirement**: Accurately detect and report software licenses
**Priority**: MEDIUM

**Implementation Controls**:

1. **License Detection Sources**:
   ```python
   LICENSE_SOURCES = [
       'package_metadata',  # setup.py, package.json
       'license_files',     # LICENSE, COPYING
       'spdx_database',     # Official SPDX list
       'github_api',        # GitHub license API
   ]

   def detect_license_multi_source(package: str) -> LicenseInfo:
       # Try all sources, prefer metadata
       for source in LICENSE_SOURCES:
           license = detect_license_from_source(package, source)
           if license:
               return license

       return LicenseInfo(
           package_name=package,
           license_type=LicenseType.UNKNOWN,
           confidence=0.0
       )
   ```

2. **License Compatibility Checks**:
   ```python
   def check_license_compatibility(licenses: List[LicenseInfo]):
       """Check for incompatible license combinations"""
       # Example: GPL + proprietary = incompatible
       has_gpl = any(l.license_type == 'GPL-3.0' for l in licenses)
       has_proprietary = any(l.license_type == 'Proprietary' for l in licenses)

       if has_gpl and has_proprietary:
           logger.error(
               "License conflict: GPL and Proprietary licenses detected"
           )
   ```

**Acceptance Criteria**:
- [ ] Multiple license sources checked
- [ ] License compatibility validated
- [ ] Unknown licenses flagged for review
- [ ] SBOM includes license confidence scores

---

### COMP-003: SOC2 Compliance (Audit Logging)

**Requirement**: Maintain audit trail for security-relevant events
**Priority**: MEDIUM

**Implementation Controls**:

1. **Audit Events**:
   ```python
   AUDIT_EVENTS = {
       'CACHE_ACCESS': 'Cached analysis result accessed',
       'CACHE_WRITE': 'Analysis result cached',
       'CACHE_DELETE': 'Cache entry deleted',
       'SENSITIVE_DATA_DETECTED': 'Sensitive data detected in analysis',
       'SENSITIVE_FILE_EXCLUDED': 'Sensitive file excluded from analysis',
       'POLICY_EXECUTED': 'Fitness policy executed',
       'SECURITY_ERROR': 'Security error occurred',
   }

   def audit_log(event: str, details: dict):
       logger.info(
           f"AUDIT: {event}",
           extra={
               'event_type': event,
               'timestamp': datetime.now().isoformat(),
               'details': details
           }
       )
   ```

2. **Audit Log Retention**:
   - Retain audit logs for 1 year
   - Export to SIEM if available
   - Tamper-evident storage (append-only)

**Acceptance Criteria**:
- [ ] All security events logged
- [ ] Audit logs retained for 1 year
- [ ] Audit log format structured (JSON)
- [ ] Audit logs include actor, action, timestamp, outcome

---

## 5. Testing Strategy

### 5.1 Security Testing Approach

**Testing Levels**:

1. **Unit Tests** (90%+ coverage):
   - Test each security control in isolation
   - Mock malicious inputs
   - Verify expected failures

2. **Integration Tests**:
   - Test security controls working together
   - End-to-end attack scenarios
   - Performance impact testing

3. **Security Tests** (dedicated):
   - Fuzzing with malformed inputs
   - Penetration testing
   - Vulnerability scanning

4. **Regression Tests**:
   - Test all known vulnerabilities
   - Verify security controls remain effective
   - Automated in CI/CD

### 5.2 Test Cases

#### Test Suite: SEC-001 (Safe AST Parsing)

```python
def test_ast_parsing_no_code_execution():
    """Verify AST parsing does not execute code"""
    malicious_code = """
import os
os.system('echo "EXPLOITED" > /tmp/exploit')
"""

    # Parse should not execute code
    service = StaticAnalysisService(db, project_path)
    ast_graph = service._parse_file(malicious_file)

    # Verify exploit file was NOT created
    assert not Path('/tmp/exploit').exists()
```

#### Test Suite: SEC-003 (Path Traversal)

```python
def test_path_traversal_prevention():
    """Verify path traversal is blocked"""
    project_root = Path('/tmp/test_project')

    # Attempt path traversal
    malicious_paths = [
        '../../../../../../etc/passwd',
        '/etc/passwd',
        '../../../home/user/.ssh/id_rsa',
    ]

    for path in malicious_paths:
        with pytest.raises(SecurityError):
            safe_relative_path(project_root, Path(path))
```

#### Test Suite: SEC-004 (Resource Limits)

```python
def test_file_size_limit():
    """Verify large files are rejected"""
    # Create 20MB file (over 10MB limit)
    large_file = Path('/tmp/large.py')
    large_file.write_text('x' * (20 * 1024 * 1024))

    service = StaticAnalysisService(db, project_path)

    with pytest.raises(ResourceLimitError):
        service._parse_file(large_file)
```

#### Test Suite: SEC-009 (Sensitive Data Redaction)

```python
def test_api_key_redaction():
    """Verify API keys are redacted before caching"""
    source_code = """
API_KEY = "sk_test_EXAMPLE_KEY_NOT_REAL_123456789"
"""

    # Redact before caching
    redacted = redact_sensitive_data(source_code)

    # Verify key not in redacted text
    assert 'sk_test_' not in redacted
    assert '[REDACTED:API_KEY:' in redacted

    # Verify redaction logged
    assert 'Redacted api_key' in caplog.text
```

### 5.3 Fuzzing Strategy

**Fuzzing Targets**:
- AST parser with malformed Python/JS/TS files
- File path validation with Unicode, null bytes, special chars
- Graph construction with edge cases (empty, circular, huge)
- Policy validation with injection attempts

**Fuzzing Tools**:
- `atheris` (Python fuzzing framework)
- `hypothesis` (property-based testing)
- Custom fuzz generators

**Example Fuzzing Test**:
```python
import atheris
import sys

def TestOneInput(data):
    """Fuzz AST parser"""
    try:
        service = StaticAnalysisService(db, project_path)
        # Write fuzz input to temp file
        fuzz_file = Path('/tmp/fuzz_input.py')
        fuzz_file.write_bytes(data)

        # Parse (should never crash)
        service._parse_file(fuzz_file)
    except Exception as e:
        # Expected exceptions OK
        if not isinstance(e, (SyntaxError, SecurityError, ResourceLimitError)):
            raise  # Unexpected exception = bug

atheris.Setup(sys.argv, TestOneInput)
atheris.Fuzz()
```

---

## 6. Security Checklist

**Pre-Release Security Validation**:

### Code Review Checklist

- [ ] No use of `eval()`, `exec()`, or `compile()` in parsing code
- [ ] All subprocess calls use `shell=False`
- [ ] All file access uses `safe_relative_path()` validation
- [ ] Resource limits enforced (file size, graph size, timeouts)
- [ ] Sensitive data redaction applied before storage
- [ ] Cache integrity protection implemented
- [ ] Policy validation prevents code injection
- [ ] Input validation applied to all CLI arguments
- [ ] Error messages don't leak sensitive information
- [ ] Logging includes security-relevant events

### Testing Checklist

- [ ] Security unit tests pass (90%+ coverage)
- [ ] Integration tests include attack scenarios
- [ ] Fuzzing completed for all parsers
- [ ] Penetration testing performed
- [ ] No critical vulnerabilities in security scan
- [ ] Performance impact acceptable (<10% overhead)

### Documentation Checklist

- [ ] Security requirements documented
- [ ] Threat model documented
- [ ] Security controls documented
- [ ] Incident response plan documented
- [ ] Security best practices documented for users

### Deployment Checklist

- [ ] Encryption keys configured (if using SEC-010)
- [ ] Resource limits configured appropriately
- [ ] Audit logging enabled
- [ ] Security monitoring configured
- [ ] Backup and recovery tested
- [ ] Incident response plan communicated

---

## 7. Incident Response

### 7.1 Security Incident Classification

**Severity Levels**:

1. **CRITICAL**: Code execution, system compromise, credential exposure
2. **HIGH**: Data exfiltration, privilege escalation, DoS
3. **MEDIUM**: Information disclosure, cache tampering
4. **LOW**: Warning bypassed, non-sensitive information disclosure

### 7.2 Incident Response Plan

**Response Steps**:

1. **Detection** (automated monitoring):
   - Security error logs
   - Anomalous resource usage
   - Failed security control checks
   - Audit log anomalies

2. **Containment** (immediate):
   - Kill affected processes
   - Disable affected features
   - Isolate compromised systems
   - Block attack vectors

3. **Investigation**:
   - Review audit logs
   - Analyze malicious inputs
   - Assess scope of compromise
   - Identify root cause

4. **Remediation**:
   - Patch vulnerability
   - Restore from clean backup
   - Rotate compromised credentials
   - Update security controls

5. **Post-Incident**:
   - Document incident details
   - Update threat model
   - Improve detection
   - Train team on lessons learned

### 7.3 Emergency Contacts

- **Security Lead**: [TBD]
- **Incident Response Team**: [TBD]
- **External Security Consultants**: [TBD]

---

## 8. Compliance Matrix

| Requirement | Security Control | Test Coverage | Status |
|-------------|------------------|---------------|--------|
| **Code Execution Prevention** | SEC-001, SEC-002 | 95% | Required |
| **Path Traversal Prevention** | SEC-003 | 90% | Required |
| **Resource Limits** | SEC-004, SEC-005 | 85% | Required |
| **Graph Security** | SEC-006 | 80% | Required |
| **Cache Integrity** | SEC-007 | 90% | Required |
| **Supply Chain Security** | SEC-008 | 70% | Recommended |
| **Data Protection** | SEC-009, SEC-010 | 95% | Required |
| **Policy Safety** | SEC-011 | 90% | Required |
| **Input Validation** | INV-001, INV-002 | 85% | Required |
| **GDPR Compliance** | COMP-001 | N/A | Conditional |
| **License Compliance** | COMP-002 | 75% | Recommended |
| **Audit Logging** | COMP-003 | 80% | Recommended |

---

## 9. Risk Assessment Summary

| Risk | Likelihood | Impact | Priority | Mitigation |
|------|------------|--------|----------|------------|
| Code execution via AST parsing | HIGH | CRITICAL | P0 | SEC-001, SEC-002 |
| Path traversal file access | MEDIUM | HIGH | P0 | SEC-003 |
| Resource exhaustion DoS | HIGH | MEDIUM | P1 | SEC-004, SEC-005 |
| Cache poisoning | LOW | HIGH | P1 | SEC-007 |
| Credential exposure | HIGH | CRITICAL | P0 | SEC-009, SEC-010 |
| Graph complexity DoS | MEDIUM | MEDIUM | P2 | SEC-006 |
| Supply chain attack | MEDIUM | MEDIUM | P2 | SEC-008 |
| Policy injection | MEDIUM | CRITICAL | P0 | SEC-011 |

**Overall Risk Level**: HIGH (mitigated to MEDIUM with all controls implemented)

---

## 10. Security Metrics

**Measurement Criteria**:

1. **Vulnerability Detection**:
   - Mean time to detect (MTTD): <24 hours
   - False positive rate: <5%
   - Security test coverage: >90%

2. **Incident Response**:
   - Mean time to respond (MTTR): <4 hours
   - Mean time to remediate: <48 hours
   - Post-incident report completion: <1 week

3. **Compliance**:
   - Security control effectiveness: >95%
   - Audit finding closure rate: 100%
   - Training completion rate: 100%

---

## Document Metadata

**Version**: 1.0.0
**Status**: Security Requirements - Ready for Review
**Author**: Security Engineering Agent
**Reviewers**: [TBD - Security Lead, System Architect, QA Lead]
**Approvers**: [TBD - CISO, Engineering Director]

**Related Documents**:
- [Detection Pack Architecture](/Users/nigelcopley/.project_manager/aipm-v2/docs/architecture/detection-pack-architecture.md)
- [ADR-008: Data Privacy and Security](/Users/nigelcopley/.project_manager/aipm-v2/docs/decisions/adr/ADR-008-data-privacy-and-security.md)
- [Security, Privacy & Compliance Principles](/Users/nigelcopley/.project_manager/aipm-v2/docs/governance/other/security-privacy-compliance.md)

**Change Log**:
- 2025-10-24: Initial security requirements document (v1.0.0)

**Next Steps**:
1. Security review by security team
2. Architecture review for feasibility
3. Implementation planning for security controls
4. Security testing strategy finalization
5. Approval and integration into implementation plan

---

**END OF DOCUMENT**
