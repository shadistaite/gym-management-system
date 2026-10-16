# SSDLC Plan — Gym Management System

## 1. Requirements
Build a simple gym booking system where users can log in, view classes, make bookings, and view their own bookings. Admins can create classes.

The system has three separate Python services:
- **API Service:** Handles login and user requests.
- **Gym Service:** Manages classes and bookings.
- **Processing Service:** Creates booking summaries using my own helper package.

The services communicate through HTTP.

**Assets:** User accounts, passwords, tokens, bookings, admin permissions, and dependencies.

**Main threats:** Unauthorized access, invalid input, SQL injection, service communication problems, and vulnerable dependencies.

**Access control:** Members can manage their own bookings. Only admins can create classes. Users cannot access other members' bookings.

**STRIDE:** I will consider spoofing, tampering, repudiation, information disclosure, denial of service, and elevation of privilege.

**Security documents:** The architecture document describes the components and trust boundaries. The asset register lists important assets and their protection. A separate threat model will document STRIDE threats, the access-control matrix, security controls, and tests.

## 2. Implementation and Build
Build the services, create and separately install the helper package, use password hashing, and run static and dependency checks.

**Gate:** All services start successfully and dependencies are checked.

## 3. Testing
Create two member accounts and one admin account. Test the features, demonstrate three course vulnerabilities and one vulnerability caused by the services working together, then fix them and test the fixes.

**Gate:** Required functionality works and security tests pass.

## 4. Release and Operation
This is a local security project, not a production system. A real deployment would also need HTTPS, secure secrets, monitoring, backups, and regular dependency updates.

## 5. CI/CD
Jenkins will run on pushes and pull requests. It will build the application, run static and dependency checks, execute tests, and save reports. Required test failures and release-blocking security findings will fail the pipeline.

## 6. Evidence
I will use Git commits, test results, security reports, and Jenkins results to show what I implemented and how I fixed the vulnerabilities.