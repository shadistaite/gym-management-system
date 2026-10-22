# CWE-20: Improper Input Validation

## Vulnerability

**Component:** API Service  
**Endpoint:** `POST /classes`  
**CWE:** CWE-20

The API must validate class information before processing it. Invalid capacity values could cause incorrect data to enter the system.

## Before Fix

The API accepted invalid capacity values because the input was not restricted to the permitted range.

Test input:

```json
{
  "name": "Test Class",
  "instructor": "Test Instructor",
  "capacity": -5
}
```

**Security issue:** A negative capacity could be accepted, resulting in invalid class data.

## Fix

Pydantic validation restricts class capacity to between 1 and 100:

```python
capacity: int = Field(gt=0, le=100)
```

Invalid values are rejected with HTTP 422.

## After Fix

The automated tests verify that invalid capacity values are rejected.

| Test | Expected result |
|---|---|
| Capacity is zero | HTTP 422 |
| Capacity is negative | HTTP 422 |
| Capacity exceeds 100 | HTTP 422 |

**Test file:** `tests/test_input_validation.py`

Run the tests:

```bash
python -m pytest tests/test_input_validation.py -v
```

**Recorded result:** 4 tests passed.

## Conclusion

Server-side input validation prevents invalid class data from being accepted. Automated tests verify that invalid values are rejected.