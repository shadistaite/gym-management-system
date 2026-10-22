# Security Testing and Vulnerability Evidence

## Purpose

This folder documents the security vulnerabilities tested in the Gym Management System, their fixes, and the automated test results.

## Testing Environment

| Item | Details |
|---|---|
| Language | Python 3.9 |
| Framework | FastAPI |
| Database | SQLite |
| Test framework | pytest |
| Environment | Local macOS |

## Vulnerability Overview

| ID | Vulnerability | Component | Status |
|---|---|---|---|
| CWE-20 | Improper Input Validation | API Service | Input validation tests passed |
| CWE-89 | SQL Injection | Gym Service | Four security tests passed |
| CWE-862 | Missing Authorization | API and Gym Services | Four authorization tests passed |
| Composition | Cross-service trust | All three services | Risk documented; dedicated test pending |

## Testing Process

Each vulnerability was investigated before the fix was implemented to identify the problem and observe its behaviour.

The testing process is:

1. Test the application to identify and reproduce the vulnerability.
2. Record the observed behaviour and identify the cause.
3. Implement a security fix.
4. Repeat the test to check that the problem is resolved.
5. Add or update automated regression tests.
6. Record the test results.

All tests are performed in a controlled local environment.

## Run the Tests

Run the complete test suite from the project root:

```bash
python -m pytest tests/ -v