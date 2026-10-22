# CWE-89: SQL Injection

## Vulnerability

**Component:** Gym Service  
**CWE:** CWE-89

SQL injection occurs when user input is inserted directly into an SQL query. An attacker could manipulate the query to access or modify data without permission.

## Before Fix

An unsafe SQL query could allow malicious input to change the query's logic.

Example input:

```text
' OR '1'='1
```

If inserted directly into an SQL statement, this input could return unintended records.

## Fix

The Gym Service uses parameterized SQL queries to separate user input from SQL commands.

Example from the application:

```python
db.execute(
    "SELECT id, capacity FROM classes WHERE id = ?",
    (request.class_id,),
)
```

This ensures that the supplied value is treated as data rather than executable SQL.

## After Fix

The tests in `tests/test_sql_injection.py` produced the following results:

| Test | Result |
|---|---|
| SQL injection string does not change database query | PASS |
| Class listing does not expose SQL injection input | PASS |
| Booking query does not accept username as SQL | PASS |
| Class listing requires authentication | PASS |

**Test result:** 4 passed in 0.27 seconds.

Run the tests with:

```bash
python -m pytest tests/test_sql_injection.py -v
```

## Conclusion

The Gym Service uses parameterized SQL queries, and all four security tests passed. The tests verify that the supplied SQL-like input does not alter the tested query, that booking ownership is enforced, and that authentication is required.