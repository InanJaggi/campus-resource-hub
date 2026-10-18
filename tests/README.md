# Test Suite

This directory contains the test suite for the Campus Resource Hub application.

## Running Tests

### Run All Tests (Recommended)

Use the master test runner for a user-friendly, colored output:

```bash
python tests/run_all_tests.py
```

This will:
- Run all test files sequentially
- Display colored output (green for success, red for failure)
- Provide a summary at the end
- Show which tests passed and which failed

### Run Individual Test Files

You can also run individual test files using pytest:

```bash
# Run a specific test file
pytest tests/test_auth_flow.py -v

# Run all tests
pytest tests/ -v

# Run with more verbose output
pytest tests/ -vv
```

## Test Files

### Unit Tests
- **test_utils.py**: Unit tests for utility functions (file upload, booking conflict detection, search, user retrieval)
  - Tests small, isolated functions without external dependencies
  - Includes tests for `allowed_file()`, `has_conflict()`, `search_resources()`, `get_user_by_email()`
  - Minimum 5 unit tests as required

### Integration Tests
- **test_auth_flow.py**: Tests user registration, login, and protected route access
- **test_dal.py**: Tests Data Access Layer CRUD operations
- **test_booking_conflict.py**: Tests booking conflict detection and prevention
- **test_waitlist.py**: Tests waitlist enrollment and automatic promotion
- **test_security_sqli.py**: Tests SQL injection protection
- **test_accessibility.py**: Tests WCAG accessibility compliance (semantic HTML, form labels, etc.)

## Manual Testing

- **MANUAL_TEST_PLAN.md**: Manual test plan with 6 test cases (3 positive, 3 negative) for the booking system
- **TESTING_REFLECTION.md**: Reflection on testing process, defects found, and areas for improvement

## Test Configuration

All tests use:
- In-memory SQLite database (no file system changes)
- CSRF protection disabled for testing
- Automatic database setup and teardown
- Isolated test fixtures

## Requirements

Make sure you have all dependencies installed:

```bash
pip install -r requirements.txt
```

The test suite requires:
- pytest
- beautifulsoup4 (for accessibility tests)
- All application dependencies

