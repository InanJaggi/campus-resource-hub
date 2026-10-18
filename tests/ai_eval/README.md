# AI Chatbot Evaluation Tests

This directory contains tests for the AI-powered chatbot functionality that uses Google Gemini API.

## Overview

The chatbot provides intelligent assistance to users, helping them navigate the Campus Resource Hub, understand features, and complete tasks. These tests verify that the chatbot:

- Responds correctly to user queries
- Properly handles navigation highlighting
- Detects tutorial requests
- Uses current page context appropriately
- Handles errors gracefully

## Test File

### `test_chatbot.py`

Comprehensive test suite for the chatbot endpoint (`/chatbot/chat`). Tests include:

#### Basic Functionality
- **`test_chatbot_endpoint_exists`**: Verifies the chatbot endpoint is accessible
- **`test_chatbot_requires_message`**: Ensures message parameter is required
- **`test_chatbot_handles_empty_message`**: Rejects empty messages
- **`test_chatbot_response_format`**: Validates JSON response structure

#### Context Awareness
- **`test_chatbot_includes_current_page_context`**: Verifies current page is passed to AI
- **`test_chatbot_handles_navigation_questions`**: Tests navigation question detection

#### Feature Detection
- **`test_chatbot_highlight_detection`**: Tests that navigation highlighting works correctly
- **`test_chatbot_tutorial_detection`**: Tests tutorial trigger detection
- **`test_chatbot_no_highlight_for_how_to_questions`**: Ensures highlighting only occurs for navigation questions, not "how to" questions

#### Error Handling
- **`test_chatbot_handles_api_error`**: Tests graceful handling of API errors
- **`test_chatbot_missing_api_key`**: Verifies behavior when API key is missing

#### Response Quality
- **`test_chatbot_response_includes_timestamp`**: Ensures responses include timestamps

## Running the Tests

### Prerequisites

1. Ensure `GEMINI_API_KEY` is set in your environment or `.env` file
2. Install test dependencies: `pip install pytest`

### Run All AI Evaluation Tests

```bash
# From project root
pytest tests/ai_eval/ -v
```

### Run Specific Test

```bash
pytest tests/ai_eval/test_chatbot.py::test_chatbot_highlight_detection -v
```

### Run with Coverage

```bash
pytest tests/ai_eval/ --cov=src/controllers/chatbot --cov-report=html
```

## Test Mocking

The tests use `unittest.mock` to mock the Gemini API calls, allowing tests to run without actual API calls. This:
- Reduces test execution time
- Eliminates API costs during testing
- Makes tests more reliable and deterministic
- Allows testing of error scenarios

## Integration Testing

For full integration testing with the actual Gemini API, you can:

1. Set `GEMINI_API_KEY` in your environment
2. Run tests without mocking (modify test file to skip mocks)
3. Note: This will make actual API calls and may incur costs

## Expected Behavior

The chatbot should:
- ✅ Respond to all valid queries with helpful answers
- ✅ Only highlight navigation elements when questions explicitly ask "where is..." or "how do I find..."
- ✅ NOT highlight navigation for "how do I..." questions when user is already on relevant page
- ✅ Detect tutorial requests and return appropriate tutorial names
- ✅ Include current page context in responses
- ✅ Handle API errors gracefully with user-friendly messages
- ✅ Return properly formatted JSON with reply, highlight, tutorial, and timestamp fields

## Troubleshooting

### Tests Fail with "API key not configured"
- Ensure `GEMINI_API_KEY` is set in `.env` file or environment
- Check that the test is using the mocked version (should not require real API key)

### Tests Fail with Import Errors
- Ensure you're running from project root
- Verify virtual environment is activated
- Run `pip install -r requirements.txt` to install dependencies

### Mock Not Working
- Verify `unittest.mock` is imported correctly
- Check that patch decorators are applied to test functions
- Ensure mock return values match expected API response format
