# Asset Register

| Asset | Main threat | Protection | Test evidence |
|---|---|---|---|
| User passwords | Account theft | Password hashing | Test login with correct and incorrect passwords |
| JWT tokens | Account impersonation | Token validation | Test missing and invalid tokens |
| Booking data | Unauthorized access | Authorization checks | Test that users cannot view other users' bookings |
| Admin account | Unauthorized administration | Role checks | Test that members cannot create classes |
| Database | SQL injection | Parameterized queries | Run SQL injection tests |
| Helper package | Vulnerable dependency | Dependency scanning | Save dependency scan results |