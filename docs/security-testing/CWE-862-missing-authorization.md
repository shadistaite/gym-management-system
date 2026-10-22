# CWE-862: Missing Authorization

## Vulnerability

**Components:** API Service and Gym Service  
**CWE:** CWE-862

Missing authorization occurs when an application allows users to perform actions or access data they do not have permission to use.

In this application, ordinary members must not create classes or access other members' private booking information.

## Before Fix

Without proper authorization checks, a member could attempt to create a class or retrieve another user's bookings or summary.

Example request:

```http
GET /bookings/bob
Authorization: Bearer <alice_token>
```

If authorization were missing, Alice could potentially access Bob's private booking information.

## Fix

The API checks the authenticated user's role before allowing class creation. It also verifies that the requested username matches the authenticated user before returning private booking information or summaries.

The Gym Service independently checks permissions for protected operations.

Unauthorized requests are rejected with HTTP 403.

## After Fix

The tests in `tests/test_authorization_security.py` produced the following results:

| Test | Result |
|---|---|
| Member cannot create a class | PASS |
| Member cannot view another user's bookings | PASS |
| Member cannot request another user's summary | PASS |
| Admin can request class creation | PASS |

**Test result:** 4 passed in 0.39 seconds.

Run the tests with:

```bash
python -m pytest tests/test_authorization_security.py -v
```

## Conclusion

The authorization tests confirm that ordinary members are blocked from administrative actions and other users' private information, while administrators can request class creation.