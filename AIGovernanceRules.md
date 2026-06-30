# AIOS - AI Governance Rules

## 1. Overview

This document defines the governance rules for AI operations within AIOS. These rules ensure that AI agents operate safely, transparently, and under human supervision at all times. All AI-generated code must comply with the project's [Coding Standards](CodingStandards.md) and follow the principles outlined in our [Documentation Standards](DocumentationStandards.md).

**Last Updated**: 2026-06-29
**Version**: 2.0
**Maintainers**: AIOS Core Team

## 2. Core Principles

### 2.1 Human Sovereignty
AI agents are tools that assist humans. Humans always retain final decision-making authority. No AI agent may take irreversible action without explicit human approval.

### 2.2 Transparency
All AI operations must be auditable. Every action taken by an AI agent must be logged with full context including inputs, reasoning, and outputs.

### 2.3 Least Privilege
AI agents operate with the minimum permissions necessary to complete their assigned tasks. Agents cannot escalate their own privileges.

### 2.4 Reversibility
All AI actions should be reversible where possible. Destructive operations require explicit human confirmation.

### 2.5 Accountability
Every AI action is attributable to a specific agent, task, and triggering user. No autonomous action occurs without traceability.

## 3. Approval Workflows

### 3.1 Approval Tiers

| Tier | Action Type | Approval Required | Examples |
|------|------------|-------------------|----------|
| 1 - Auto | Read operations, queries | None | Search memory, read files, check status |
| 2 - Notify | Write operations within project | Notification only | Create files, edit code, store memory |
| 3 - Confirm | Significant changes | Explicit confirmation | Delete files, modify configurations, install plugins |
| 4 - Multi | Destructive or external actions | Multiple confirmations | Push to remote, delete project, send data externally |

### 3.2 Approval Flow

```
Agent Request
    │
    ▼
�─────────────────┐
│ Evaluate Tier   │
└────────┬────────┘
          │
     ┌────┴────┐
     ▼         ▼
   Tier 1-2   Tier 3-4
     │         │
     ▼         ▼
   Execute   Present to
   with      User for
   logging   approval
               │
          ┌────�────┐
          ▼         ▼
       Approved   Rejected
          │         │
          ▼         ▼
       Execute   Log and
       + Log     notify
```

### 3.3 Approval UI Requirements

- Clear description of what the AI wants to do
- Risk assessment indicator
- Preview of changes (for code/file operations)
- Option to modify before approving
- Option to reject with feedback
- Timeout for response (default: 5 minutes)
- Default action on timeout: Reject

## 4. Prohibited Actions

### 4.1 Never Without Explicit Approval

1. **External Communication**: Sending data to external URLs, APIs, or services
2. **Production Deployment**: Deploying to production environments
3. **Data Deletion**: Deleting databases, backups, or user data
4. **Configuration Changes**: Modifying system or security configurations
5. **User Management**: Creating, modifying, or deleting user accounts
6. **Network Operations**: Opening ports, modifying firewall rules
7. **Package Publishing**: Publishing to package registries (npm, PyPI)
8. **Git Push**: Pushing to remote repositories
9. **Secret Rotation**: Changing encryption keys or API credentials
10. **Plugin Installation**: Installing plugins from untrusted sources

### 4.2 Never Under Any Circumstances

1. **Bypass Security**: Attempting to bypass security controls or sandboxing
2. **Self-Modification**: Modifying the AIOS codebase or configuration
3. **Privilege Escalation**: Attempting to gain elevated permissions
4. **Data Exfiltration**: Copying user data to external locations
5. **Cryptocurrency Mining**: Using system resources for unauthorized computation
6. **Credential Harvesting**: Attempting to read secrets outside authorized scope
7. **Prompt Injection**: Embedding instructions in data to manipulate other agents
8. **Denial of Service**: Intentionally consuming excessive resources
9. **Log Tampering**: Modifying or deleting audit logs
10. **Identity Spoofing**: Impersonating users or other agents

## 5. Self-Improvement Governance

### 5.1 Self-Improvement Rules

AIOS may observe its own performance and propose improvements under these rules:

1. **Observation**: System may track metrics and identify patterns
2. **Proposal**: System may generate improvement proposals
3. **Human Review**: All proposals must be reviewed by a human
4. **Explicit Approval**: Changes only applied after explicit approval
5. **Gradual Rollout**: Changes applied incrementally with monitoring
6. **Rollback Ready**: All changes can be reverted immediately
7. **Audit Trail**: All improvement decisions fully logged

### 5.2 Self-Improvement Approval Process

```
┌──────────────────┐
│ System observes  │
│ pattern/metric   │
└────────┬─────────┘
          │
          ▼
┌──────────────────┐
│ Generate         │
│ improvement      │
│ proposal         │
└────────�─────────┘
          │
          ▼
┌──────────────────┐
│ Queue for human  │
│ review           │
└────────┬─────────�
          │
          ▼
┌──────────────────┐
│ Human reviews    │
│ proposal +       │
│ evidence         │
└────────�─────────┘
          │
     �────┴────┐
     ▼         ▼
  Approved   Rejected
     │         │
     ▼         ▼
  Apply with  Log reason
  monitoring  for rejection
     │
     ▼
  Monitor for
  duration
     │
     ▼
  Evaluate
  results
```

### 5.3 Prohibited Self-Improvements

- Modifying approval workflows or governance rules
- Adjusting its own permission levels
- Modifying audit logging behavior
- Changing model routing to bypass cost controls
- Modifying security configurations
- Altering other agents' prompts or capabilities
- Disabling safety mechanisms

## 6. Content Safety

### 6.1 Input Validation

All inputs to AI agents must be validated according to the following security requirements:
- File paths validated against allowed directories using path traversal prevention
- URLs validated against allowlists with HTTPS enforcement
- Code scanned for obvious injection patterns and malicious payloads
- Size limits enforced on all inputs (max 10MB per request)
- Content type validation with strict MIME type checking
- Input sanitization for prompt injection prevention using latest OWASP guidelines
- Unicode normalization to prevent homograph attacks
- Rate limiting on input processing to prevent abuse

### 6.2 Output Validation

All outputs from AI agents must be validated against project standards:
- Code scanned for security vulnerabilities (bandit for Python, ESLint security for TypeScript)
- File operations validated against sandbox with strict permission controls
- Commands validated against allowlist with parameter sanitization
- URLs in output checked against blocklist and verified for safety
- Sensitive data patterns detected and redacted (PII, credentials, tokens)
- Code quality validated against project linting rules (Ruff, ESLint with strict mode)
- Type annotations verified for completeness (mypy strict mode for Python)
- Memory usage validation for generated code
- Performance impact assessment for resource-intensive operations

### 6.3 Prompt Injection Defense

AIOS implements multi-layered prompt injection defense:

```
�─────────────────┐
│ Input Received  │
└────────┬────────┘
          │
          ▼
┌─────────────────�
│ Content         │
│ Classification  │
│ + Risk Scoring  │
└────────┬────────┘
          │
     ┌────┴────�
     ▼         ▼
   Safe      Suspicious
     │         │
     ▼         ▼
   Process   Quarantine
   normally  + deep scan
               │
          ┌────┴────�
          ▼         ▼
       Clean     Malicious
          │         │
          ▼         ▼
       Process   Reject +
       with      log +
       warnings  alert
```

**Additional Security Measures**:
- Context-aware injection detection
- Behavioral analysis for anomaly detection
- Regular updates to injection pattern database
- Machine learning-based threat detection

## 7. Resource Governance

### 7.1 Resource Limits

| Resource | Per-Agent Limit | System Total |
|----------|----------------|--------------|
| CPU | 25% | 80% |
| RAM | 2 GB | 8 GB |
| Disk I/O | 100 MB/s | 500 MB/s |
| Network | 10 MB/s | 50 MB/s |
| API calls/minute | 60 | 300 |
| Token usage/hour | 100K | 500K |
| Execution time | 5 minutes | 30 minutes |

### 7.2 Resource Monitoring

- Real-time resource usage tracking per agent
- Automatic throttling when limits approached
- Graceful termination when limits exceeded
- Resource usage included in audit logs
- User notifications for unusual resource patterns

## 8. Audit Requirements

### 8.1 What Must Be Logged

Every AI agent action must log:
- Timestamp (UTC)
- Agent ID and role
- Triggering user or event
- Action type and parameters
- Input summary (full input if <1MB, hash otherwise)
- Output summary
- Resources consumed
- Duration
- Success/failure status
- Error details (if applicable)
- Approval chain (who approved what)

### 8.2 Audit Log Retention

| Log Type | Retention | Storage |
|----------|-----------|---------|
| Agent actions | 1 year | SQLite + exportable |
| Security events | 2 years | SQLite + exportable |
| System events | 90 days | SQLite |
| User actions | 1 year | SQLite + exportable |
| Self-improvement | Permanent | SQLite + exportable |

### 8.3 Audit Log Access

- Users can view logs for their own projects
- Admins can view all logs
- Logs are read-only after creation
- Logs can be exported in standard formats (JSON, CSV)
- Logs cannot be deleted by users (only expired by policy)

## 9. Model Governance

### 9.1 Approved Model Criteria

Models must meet these criteria for inclusion:
- Open source license (OSI-approved) or commercially viable licensing
- Available for use within project budget constraints
- Reproducible outputs (temperature 0 produces consistent results)
- No training on known malicious content
- Provider has acceptable privacy policy and data handling practices
- Consistent code generation quality (passes project linting and type checking)
- Support for structured outputs where applicable
- Regular security updates and maintenance
- Compliance with AI ethics guidelines
- Support for latest AI safety features

### 9.2 Model Blacklist

Models are blacklisted if:
- Known to produce malicious code or security vulnerabilities
- History of prompt injection vulnerabilities
- Non-transparent training data or practices
- Known bias issues without mitigation
- Provider has unacceptable practices or legal issues
- Failure to meet minimum performance benchmarks
- Incompatibility with project security requirements
- Lack of proper documentation or support

### 9.3 Model Evaluation

Before adding a new model provider:
1. Security review of provider API and infrastructure
2. Output quality evaluation on comprehensive test suite
3. Bias assessment across diverse datasets
4. Performance benchmarking against current models
5. Privacy impact assessment with legal review
6. Community review period (minimum 2 weeks)
7. Cost analysis and budget impact assessment
8. Integration testing with existing AIOS infrastructure
9. Documentation review and validation
10. Approval by AIOS governance committee

## 10. Incident Response

### 10.1 Incident Categories

| Category | Description | Response Time |
|----------|-------------|---------------|
| Critical | Security breach, data loss | Immediate |
| High | System instability, agent malfunction | < 1 hour |
| Medium | Performance degradation, unexpected behavior | < 4 hours |
| Low | Minor bugs, UI issues | < 24 hours |

### 10.2 Response Process

1. **Detection**: Automated monitoring or user report
2. **Triage**: Categorize severity and assign responder
3. **Containment**: Isolate affected components
4. **Investigation**: Determine root cause
5. **Remediation**: Fix and verify
6. **Post-Mortem**: Document and learn
7. **Prevention**: Implement safeguards

## 11. Compliance

### 11.1 AI Ethics

- No AI agent may discriminate based on protected characteristics
- AI outputs must be clearly identified as AI-generated
- Users must be informed when AI is assisting them
- AI must not impersonate specific individuals
- AI must acknowledge uncertainty rather than hallucinate
- AI-generated code must follow project naming conventions and style guidelines

### 11.2 Data Privacy

- User code and data remain on local machine by default
- Explicit consent required for any external transmission
- Data classification labels respected at all times
- Right to deletion honored for all user data
- No training on user data without explicit opt-in
- Audit logs treated as sensitive data with appropriate access controls

### 11.3 Open Source Compliance

- All AI-generated code checked for license compatibility
- Attribution maintained for AI-assisted contributions
- No copyleft contamination of proprietary projects
- SBOM (Software Bill of Materials) maintained
- AI-generated code includes appropriate license headers where required

## 12. Code Quality Governance

### 12.1 AI-Generated Code Standards

All AI-generated code must comply with the project's [Coding Standards](CodingStandards.md) and meet these enhanced requirements:

**Python Code Requirements**:
- Must pass mypy strict mode with no errors
- Must pass Ruff linting with all security rules enabled
- All functions must have complete type annotations (no `Any` types)
- Public APIs must have Google-style docstrings with examples
- Error handling must use project-defined exception hierarchy
- Import ordering must follow project conventions (Ruff isort)
- Must use async/await patterns where applicable
- Must follow Pydantic v2 patterns for data validation

**TypeScript Code Requirements**:
- Must pass ESLint with strict type checking enabled
- All functions must have explicit return types
- Components must use proper React patterns (hooks, functional components)
- State management must follow project conventions (Zustand)
- Must use proper TypeScript advanced types where applicable
- Must follow project component composition patterns

**General Requirements**:
- Code must be self-documenting with clear variable and function names
- No hardcoded values (use configuration or constants)
- Proper separation of concerns and single responsibility principle
- Must be testable with clear input/output boundaries
- Performance considerations documented for complex operations

### 12.2 Code Review for AI-Generated Code

AI-generated code undergoes enhanced review process:
- Must pass all automated checks (linting, type checking, security scanning)
- Must include appropriate test coverage (minimum 80% for new code)
- Must follow project naming conventions and architectural patterns
- Must include proper error handling with user-friendly messages
- Must be documented according to project standards
- Must include performance benchmarks for resource-intensive operations
- Must undergo security review for potential vulnerabilities
- Must be validated against project's accessibility standards
- Must include proper logging and monitoring integration
- Must be reviewed for AI-specific issues (hallucinations, edge cases)

## 13. Governance Review

### 13.1 Review Process

- Governance rules reviewed quarterly by maintainers and security team
- Community input solicited for significant changes (30-day comment period)
- All changes to governance require maintainer approval and security review
- Changes announced to community before taking effect (2-week notice)
- Previous versions maintained for reference with clear changelog
- Governance rules updated to reflect changes in coding standards and security best practices

### 13.2 Version Control

- All governance changes tracked in version control
- Clear documentation of rationale for changes
- Impact assessment for all modifications
- Rollback procedures for problematic changes
- Regular audits of governance effectiveness

### 13.3 Compliance Monitoring

- Automated compliance checking where possible
- Regular audits of AI agent adherence to governance rules
- Metrics collection for governance effectiveness
- Continuous improvement based on incident learnings
- Annual comprehensive governance review

## 14. AI Ethics and Responsibility

### 14.1 Ethical AI Use

- AI agents must not be used for malicious purposes
- AI outputs must be clearly identified as AI-generated
- Users must be informed of AI limitations and potential biases
- AI must not be used to replace human judgment in critical decisions
- Regular bias testing and mitigation for AI models

### 14.2 Transparency Requirements

- Clear disclosure of AI involvement in code generation
- Documentation of AI model versions and configurations
- Open communication about AI capabilities and limitations
- Regular reporting on AI system performance and issues

### 14.3 Human Oversight

- Meaningful human control over AI operations
- Ability to override or stop AI actions at any time
- Regular human review of AI-generated outputs
- Clear escalation paths for AI-related issues
