# Security Testing and Vulnerability Evidence

## 1. Purpose

This folder contains the security testing documentation for the Gym Management System.

Each vulnerability report records the vulnerability, the affected component, the test procedure, the observed behaviour before remediation, the security fix, and the results after remediation.

The purpose is to provide traceable evidence that security weaknesses have been investigated, addressed, and tested.

## 2. Testing Environment

| Item | Details |
|---|---|
| Application | Gym Management System |
| Programming language | Python |
| Web framework | FastAPI |
| Database | SQLite |
| Test framework | pytest |
| Development environment | Local macOS environment |
| Python version | Python 3.9 |
| Test execution | Local automated tests |

## 3. Vulnerability Overview

| ID | Vulnerability | Affected component | Status |
|---|---|---|---|
| CWE-20 | Improper Input Validation | API Service | Input rejection tests passed; vulnerable version demonstration pending |
| CWE-89 | SQL Injection | Gym Service | Controlled demonstration and regression evidence pending |
| CWE-862 | Missing Authorization | API Service and Gym Service | Authorization tests passed; vulnerable version demonstration pending |
| Composition vulnerability | Cross-service trust and authorization failure | API, Gym, and Processing Services | Existing security tests passed; dedicated demonstration pending |

Statuses must be updated as testing progresses. A vulnerability must not be marked as demonstrated until the relevant test has actually reproduced it.

## 4. Required Evidence for Each Vulnerability

Each vulnerability report should contain:

1. Vulnerability name and identifier.
2. Affected component and endpoint.
3. Test date, time, and timezone.
4. Security objective.
5. Test input or attack scenario.
6. Expected behaviour.
7. Actual behaviour before remediation.
8. Root cause.
9. Security fix and relevant code changes.
10. Actual behaviour after remediation.
11. Automated regression test and command.
12. Test output or other evidence.
13. Git commit containing the fix, where applicable.
14. Conclusion and any remaining limitations.

## 5. Before-and-After Testing Process

Each vulnerability will be investigated using the following process:

1. Preserve the current implementation in Git.
2. Reproduce the vulnerability in an isolated local test or controlled revision.
3. Record the actual input, response, and result.
4. Identify the root cause.
5. Implement or verify the security fix.
6. Repeat the same test against the fixed implementation.
7. Add or update an automated regression test.
8. Record the test results and relevant Git commit.
9. Update the corresponding vulnerability report.

Deliberately vulnerable code must not be left in the final application.

All demonstrations must be performed in a controlled local environment.

## 6. Test Execution

Run the complete test suite from the project root:

```bash
python -m pytest tests/ -v
```

Run a specific test file:

```bash
python -m pytest tests/test_input_validation.py -v
```

Test results must be recorded from actual executions. Do not invent results, timestamps, or commit identifiers.

## 7. Secure Design Principles

The testing supports the following secure design principles.

### Least Privilege

Ordinary members must not perform administrative operations or access another member's private booking information.

### Complete Mediation

Each service must check authentication and authorization before performing a protected operation. Internal service requests must not automatically be trusted.

### Fail-Safe Defaults

Missing credentials, invalid tokens, unauthorized operations, and invalid input must be rejected by default.

## 8. Related Documentation

The security testing evidence should remain consistent with:

- `docs/ssdlc-plan.md`
- `docs/architecture.md`
- `docs/asset-register.md`
- `docs/threat-model.md`

The final implementation, tests, and documentation should describe the same security controls and trust boundaries.