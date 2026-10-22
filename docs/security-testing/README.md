# Security Testing and Vulnerability Evidence

## Purpose

This folder documents the security vulnerabilities assessed in the Gym Management System, the security fixes implemented, and the automated tests used to verify the application's security.

The project uses a multi-service architecture consisting of an API Service, Gym Service, and Processing Service. Each service has security responsibilities, including authentication, authorization, input validation, and token verification.

## Testing Environment

| Item | Details |
|---|---|
| Programming language | Python 3.9 |
| Web framework | FastAPI |
| Database | SQLite |
| Test framework | pytest |
| Authentication | JWT |
| Password hashing | Argon2 |
| Development environment | macOS |
| Architecture | Three separate application services |

## Vulnerability Overview

The project addresses three catalogue vulnerabilities and one additional composition vulnerability.

| ID | Vulnerability | Component | Security Measure | Verification |
|---|---|---|---|---|
| CWE-20 | Improper Input Validation | API Service | Validates request data and rejects invalid class capacities and inputs. | Input validation tests passed. |
| CWE-89 | SQL Injection | Gym Service | Uses parameterized SQL queries instead of constructing queries from user input. | SQL injection security tests passed. |
| CWE-862 | Missing Authorization | API and Gym Services | Enforces role-based access control and ownership checks. | Authorization security tests passed. |
| Composition | Cross-service identity validation | Gym and Processing Services | Validates token usernames against a trusted user registry and checks assigned roles. | Gym Service composition regression test passed; full test suite passed. |

## Testing Process

Security testing follows these steps:

1. Identify the vulnerability and the affected component.
2. Review the relevant implementation and trust boundaries.
3. Implement or verify the security fix.
4. Write or run automated tests for the security requirement.
5. Record the observed test results.
6. Update the relevant security documentation.
7. Commit the implementation, tests, and documentation to version control.

Testing is performed in a controlled local development environment.

A vulnerability is not considered demonstrated unless a test or other recorded evidence reproduces the vulnerable behaviour. Test results in this documentation must reflect actual test executions.

## Vulnerability Reports

The following documents describe the security issues and their verification evidence:

- `CWE-20-input-validation.md` — Improper input validation.
- `CWE-89-sql-injection.md` — SQL injection.
- `CWE-862-missing-authorization.md` — Missing authorization.
- `composition-vulnerability.md` — Cross-service identity validation.

Each report describes the relevant vulnerability, the security measure implemented, and the available test evidence.

## Run the Tests

Run the complete test suite from the project root:

```bash
python -m pytest tests/ -v