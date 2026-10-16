# System Architecture — Gym Management System

## 1. Overview
The system lets members view gym classes, make bookings, and view their own bookings. Admins can create classes.

## 2. Components
The system has three separate Python services that communicate through HTTP:

- **API Service:** Handles login, issues JWT authentication tokens, and receives user requests.
- **Gym Service:** Manages classes and bookings and checks user permissions.
- **Processing Service:** Creates booking summaries using my own helper package, `gym-summary-utils`.

The helper package will be installed separately and used by the Processing Service.

## 3. Architecture Diagram

```mermaid
flowchart TD
    U["User"]
    A["API Service"]
    G["Gym Service"]
    P["Processing Service"]
    D[("Database")]
    H["gym-summary-utils"]

    U -->|HTTP requests with JWT| A
    A -->|HTTP requests| G
    A -->|Summary requests| P
    G --> D
    P -->|Request booking data| G
    P --> H

    style U padding:20px
    style A padding:30px
    style G padding:30px
    style P padding:30px
    style D padding:20px
    style H padding:20px
```

The three services run as separate processes. The database and helper package are not counted as application components.

## 4. Authentication Flow

```mermaid
flowchart TD
    A["User enters username<br/>and password"]
    B["API Service checks credentials"]
    C{"Credentials valid?"}
    D["Issue JWT token"]
    E["Reject login"]
    F["User sends request with token"]
    G["Service validates token<br/>and checks permissions"]
    H["Return requested data"]
    I["Reject request"]

    A --> B
    B --> C
    C -->|Yes| D
    C -->|No| E
    D --> F
    F --> G
    G -->|Authorized| H
    G -->|Not authorized| I

    style A padding:20px
    style B padding:30px
    style C padding:25px
    style D padding:25px
    style E padding:25px
    style F padding:30px
    style G padding:35px
    style H padding:25px
    style I padding:25px
```

After logging in, the user receives a JWT token. Later requests include this token. The relevant service must validate the token and check the user's permissions before allowing access.

## 5. Trust Boundaries

- **User → API:** Check login details, tokens, and input.
- **API → Gym Service:** Check permissions before allowing access to bookings or classes.
- **API → Processing Service:** Check that users are allowed to request summaries.
- **Services → Database:** Use parameterized queries and protect private data.
- **Processing Service → Helper Package:** Track the dependency and check for known vulnerabilities.

Services must not automatically trust requests just because they come from another service.

## 6. Users and Permissions

The system has two roles:

| Action | Member | Admin |
|---|---|---|
| View classes | Yes | Yes |
| Make bookings | Yes | Yes |
| View own bookings | Yes | Yes |
| View another user's bookings | No | No |
| Create classes | No | Yes |
| Generate own summary | Yes | Yes |

Test accounts:
- Alice — member
- Bob — member
- Admin — administrator

## 7. Security Principles

- **Least privilege:** Members cannot use admin-only features.
- **Complete mediation:** Check permissions whenever protected data is accessed.
- **Fail-safe defaults:** Reject requests when authorization is missing or invalid.

I will test these principles using automated tests.

## 8. Scope

This is a local security assignment, not a public production system. No graphical interface is required; I can test the application using HTTP requests and automated tests.

The project will demonstrate three vulnerabilities from the course catalogue and one additional vulnerability caused by the services working together. I will document the vulnerabilities, fix them, and test that the fixes work.