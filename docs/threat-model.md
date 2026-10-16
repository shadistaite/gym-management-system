# Threat Model — Gym Management System

## 1. Main Threats (STRIDE)

| Threat | Example | Protection |
|---|---|---|
| Spoofing | Someone uses another user's account | Password hashing and JWT validation |
| Tampering | Someone changes booking data | Input validation and authorization |
| Repudiation | A user denies making a booking | Record important actions |
| Information Disclosure | Someone views another user's bookings | Permission checks |
| Denial of Service | Someone sends too many requests | Limit requests and validate input |
| Elevation of Privilege | A member tries to use admin features | Role checks |

## 2. Access-Control Matrix

| Action | Member | Admin |
|---|---|---|
| View classes | Yes | Yes |
| Make bookings | Yes | Yes |
| View own bookings | Yes | Yes |
| View another user's bookings | No | No |
| Create classes | No | Yes |
| Generate own summary | Yes | Yes |

## 3. Trust Boundaries

- **User to API Service:** Login details, tokens, and input must be checked.
- **API Service to Gym Service:** Requests must be checked before accessing classes or bookings.
- **API Service to Processing Service:** Only allowed summary requests should be accepted.
- **Processing Service to Gym Service:** Requests for booking data must be authorized.
- **Services to Database:** Queries must be safe, and private data must be protected.

## 4. Planned Vulnerabilities

| Vulnerability | Planned fix |
|---|---|
| CWE-20: Improper Input Validation | Validate user input |
| CWE-89: SQL Injection | Use parameterized queries |
| CWE-862: Missing Authorization | Check permissions before allowing access |
| Service composition vulnerability | Verify permissions across service boundaries |

I will test each vulnerability, apply the fix, and run tests to check that unauthorized actions are blocked.