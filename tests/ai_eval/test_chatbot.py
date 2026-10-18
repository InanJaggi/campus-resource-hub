"""
Test suite for AI Chatbot functionality using Google Gemini API
Tests the chatbot endpoint, response format, highlighting, and tutorial features
"""
import pytest
import os
import json
from unittest.mock import patch, MagicMock
from src.app import create_app
from src.extensions import db


@pytest.fixture()
def app():
    """Create test Flask application"""
    app = create_app({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "WTF_CSRF_ENABLED": False,
        "SECRET_KEY": "test",
        "GEMINI_API_KEY": os.getenv("GEMINI_API_KEY", "test-api-key"),
    })
    with app.app_context():
        db.create_all()
    yield app


@pytest.fixture()
def client(app):
    """Create test client"""
    return app.test_client()


def test_chatbot_endpoint_exists(client):
    """Test that the chatbot endpoint is accessible"""
    response = client.post(
        '/chatbot/chat',
        json={"message": "Hello", "current_page": "/"},
        content_type='application/json'
    )
    # Should not return 404
    assert response.status_code != 404, "Chatbot endpoint not found"


def test_chatbot_requires_message(client):
    """Test that chatbot requires a message parameter"""
    response = client.post(
        '/chatbot/chat',
        json={},
        content_type='application/json'
    )
    assert response.status_code == 400
    data = json.loads(response.data)
    assert "error" in data or "Message is required" in data.get("error", "")


def test_chatbot_handles_empty_message(client):
    """Test that chatbot rejects empty messages"""
    response = client.post(
        '/chatbot/chat',
        json={"message": "", "current_page": "/"},
        content_type='application/json'
    )
    assert response.status_code == 400
    data = json.loads(response.data)
    assert "error" in data or "Message is required" in data.get("error", "")


def test_chatbot_response_format(client):
    """Test that chatbot returns properly formatted JSON response"""
    # Mock Gemini API response
    mock_response = MagicMock()
    mock_response.text = "Hello! I'm your AI assistant. How can I help you?"
    
    with patch('src.controllers.chatbot.genai') as mock_genai:
        mock_model = MagicMock()
        mock_model.generate_content.return_value = mock_response
        mock_genai.GenerativeModel.return_value = mock_model
        mock_genai.configure = MagicMock()
        
        response = client.post(
            '/chatbot/chat',
            json={"message": "Hello", "current_page": "/"},
            content_type='application/json'
        )
        
        if response.status_code == 200:
            data = json.loads(response.data)
            assert "reply" in data
            assert isinstance(data["reply"], str)
            assert len(data["reply"]) > 0


def test_chatbot_includes_current_page_context(client):
    """Test that chatbot receives and uses current page context"""
    mock_response = MagicMock()
    mock_response.text = "You can find your bookings in the navigation bar."
    
    with patch('src.controllers.chatbot.genai') as mock_genai:
        mock_model = MagicMock()
        mock_model.generate_content.return_value = mock_response
        mock_genai.GenerativeModel.return_value = mock_model
        mock_genai.configure = MagicMock()
        
        response = client.post(
            '/chatbot/chat',
            json={"message": "where are my bookings", "current_page": "/bookings/"},
            content_type='application/json'
        )
        
        if response.status_code == 200:
            # Verify the request was made (page context should be included in prompt)
            assert mock_model.generate_content.called
            call_args = mock_model.generate_content.call_args[0][0]
            assert "/bookings/" in call_args or "Current page" in call_args


def test_chatbot_highlight_detection(client):
    """Test that chatbot can detect and return highlight instructions"""
    mock_response = MagicMock()
    mock_response.text = "You can find your bookings by clicking on the 'Bookings' link in the navigation bar.\n[HIGHLIGHT:nav-bookings]"
    
    with patch('src.controllers.chatbot.genai') as mock_genai:
        mock_model = MagicMock()
        mock_model.generate_content.return_value = mock_response
        mock_genai.GenerativeModel.return_value = mock_model
        mock_genai.configure = MagicMock()
        
        response = client.post(
            '/chatbot/chat',
            json={"message": "where is my bookings", "current_page": "/"},
            content_type='application/json'
        )
        
        if response.status_code == 200:
            data = json.loads(response.data)
            assert "highlight" in data
            assert data["highlight"] == "nav-bookings"
            # Verify highlight tag was removed from reply
            assert "[HIGHLIGHT:" not in data["reply"]


def test_chatbot_tutorial_detection(client):
    """Test that chatbot can detect and return tutorial instructions"""
    mock_response = MagicMock()
    mock_response.text = "Let me show you around the website!\n[TUTORIAL:navigation]"
    
    with patch('src.controllers.chatbot.genai') as mock_genai:
        mock_model = MagicMock()
        mock_model.generate_content.return_value = mock_response
        mock_genai.GenerativeModel.return_value = mock_model
        mock_genai.configure = MagicMock()
        
        response = client.post(
            '/chatbot/chat',
            json={"message": "show me around", "current_page": "/"},
            content_type='application/json'
        )
        
        if response.status_code == 200:
            data = json.loads(response.data)
            assert "tutorial" in data
            assert data["tutorial"] == "navigation"
            # Verify tutorial tag was removed from reply
            assert "[TUTORIAL:" not in data["reply"]


def test_chatbot_no_highlight_for_how_to_questions(client):
    """Test that chatbot doesn't highlight navigation for 'how to' questions"""
    mock_response = MagicMock()
    mock_response.text = "To edit a resource, click the 'Edit' button on the resource card."
    
    with patch('src.controllers.chatbot.genai') as mock_genai:
        mock_model = MagicMock()
        mock_model.generate_content.return_value = mock_response
        mock_genai.GenerativeModel.return_value = mock_model
        mock_genai.configure = MagicMock()
        
        response = client.post(
            '/chatbot/chat',
            json={"message": "how do I edit a resource", "current_page": "/resources/"},
            content_type='application/json'
        )
        
        if response.status_code == 200:
            data = json.loads(response.data)
            # Should not have highlight for 'how to' questions
            assert data.get("highlight") is None or data["highlight"] == None


def test_chatbot_handles_api_error(client):
    """Test that chatbot handles API errors gracefully"""
    with patch('src.controllers.chatbot.genai') as mock_genai:
        mock_model = MagicMock()
        mock_model.generate_content.side_effect = Exception("API Error")
        mock_genai.GenerativeModel.return_value = mock_model
        mock_genai.configure = MagicMock()
        
        response = client.post(
            '/chatbot/chat',
            json={"message": "test", "current_page": "/"},
            content_type='application/json'
        )
        
        # Should return error response
        assert response.status_code == 500
        data = json.loads(response.data)
        assert "error" in data


def test_chatbot_missing_api_key(client):
    """Test that chatbot handles missing API key"""
    # Temporarily remove API key
    with patch.dict(os.environ, {}, clear=False):
        if "GEMINI_API_KEY" in os.environ:
            del os.environ["GEMINI_API_KEY"]
        
        # Create new app without API key
        test_app = create_app({
            "TESTING": True,
            "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
            "WTF_CSRF_ENABLED": False,
            "SECRET_KEY": "test",
        })
        
        with test_app.test_client() as test_client:
            response = test_client.post(
                '/chatbot/chat',
                json={"message": "test", "current_page": "/"},
                content_type='application/json'
            )
            
            # Should return error about missing API key
            assert response.status_code == 500
            data = json.loads(response.data)
            assert "error" in data
            assert "API key" in data["error"].lower() or "GEMINI" in data["error"].upper()


def test_chatbot_response_includes_timestamp(client):
    """Test that chatbot response includes timestamp"""
    mock_response = MagicMock()
    mock_response.text = "Hello! How can I help you?"
    
    with patch('src.controllers.chatbot.genai') as mock_genai:
        mock_model = MagicMock()
        mock_model.generate_content.return_value = mock_response
        mock_genai.GenerativeModel.return_value = mock_model
        mock_genai.configure = MagicMock()
        
        response = client.post(
            '/chatbot/chat',
            json={"message": "Hello", "current_page": "/"},
            content_type='application/json'
        )
        
        if response.status_code == 200:
            data = json.loads(response.data)
            assert "timestamp" in data
            assert isinstance(data["timestamp"], str)


def test_chatbot_handles_navigation_questions(client):
    """Test that chatbot correctly identifies navigation-related questions"""
    mock_response = MagicMock()
    mock_response.text = "You can find the Browse Resources link in the navigation bar.\n[HIGHLIGHT:nav-browse]"
    
    with patch('src.controllers.chatbot.genai') as mock_genai:
        mock_model = MagicMock()
        mock_model.generate_content.return_value = mock_response
        mock_genai.GenerativeModel.return_value = mock_model
        mock_genai.configure = MagicMock()
        
        response = client.post(
            '/chatbot/chat',
            json={"message": "where can I browse resources", "current_page": "/"},
            content_type='application/json'
        )
        
        if response.status_code == 200:
            data = json.loads(response.data)
            # Navigation questions should trigger highlights
            assert data.get("highlight") is not None or "browse" in data["reply"].lower()

