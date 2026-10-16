# SSDLC Plan — Gym Management System

## 1. Requirements Phase

### Purpose
Build a small gym class booking system that protects users' bookings
and supports class management by an administrator.

### Functional Requirements
- Users can authenticate.
- Members can view gym classes.
- Members can create and view their own bookings.
- Administrators can create gym classes.
- Users cannot access another member's private bookings.
- The system can generate booking summaries.

### Components
1. API Service: authenticates users and coordinates requests.
2. Gym Service: manages classes and bookings and enforces permissions.
3. Processing Service: generates booking summaries using a separate helper package.

The three services will run as separate processes and communicate
through HTTP APIs.

### Assets
- User credentials and authentication tokens.
- Private booking records.
- Gym class information.
- Administrator privileges.
- Helper package and installed dependencies.

### Main Threats and Controls
- Unauthorized access: verify identity, ownership, and permissions.
- Invalid input: validate request data.
- SQL injection: use parameterized database queries.
- Cross-service authorization failures: independently verify authority
  at protected service boundaries.
- Untrusted dependencies: pin and review dependencies.

### Security Principles
- Least privilege.
- Complete mediation.
- Fail-safe defaults.

## 2. Implementation and Build Phase

- Implement three independent Python services.
- Define explicit HTTP interfaces between services.
- Create a separately installable helper package.
- Use established libraries for password hashing and authentication.
- Keep dependencies declared and pinned.
- Run static analysis and dependency vulnerability checks.
- Document build and run commands.

Gate: all services build and start successfully; unexpected dependencies
are investigated and rejected.

## 3. Testing Phase

- Seed two ordinary users and one administrator.
- Test normal booking and class-management functionality.
- Test that one member cannot access another member's bookings.
- Demonstrate three vulnerabilities selected from the course catalogue.
- Demonstrate one additional vulnerability caused by service composition.
- Preserve evidence of vulnerable behavior and its remediation.
- Test the final security controls with regression tests.
- Save functional, authorization, and security analysis results.

Gate: required functional and security tests pass, and confirmed
security violations are fixed.

## 4. Release, Deployment and Operation Phase

For a production release, the system would require:
- Secure secret and credential management.
- HTTPS and restricted network access.
- Hardened service and database permissions.
- Dependency updates and vulnerability monitoring.
- Centralized security logging and monitoring.
- Backup, recovery, and incident-response procedures.

Gate: production deployment would require a separate security review.

## 5. CI/CD

Jenkins will validate builds, run static and dependency analysis,
start a fresh test environment, execute functional and authorization
tests, and save reports as build artifacts.

The pipeline will fail if required tests fail or if findings meet
the documented release-blocking criteria.

## 6. Evidence and Traceability

Security requirements will be linked to implementation decisions,
automated tests, Git commits, and Jenkins reports.

This plan will be committed before feature implementation and updated
when justified by new findings.
