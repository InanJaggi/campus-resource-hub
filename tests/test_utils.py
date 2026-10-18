"""
Unit tests for utility functions
Tests small, isolated functions without external dependencies where possible
"""
import pytest
from datetime import datetime, timedelta
from src.utils.file_upload import allowed_file
from src.app import create_app
from src.extensions import db
from src.models.models import User, Resource, Booking
from src.data_access.bookings import has_conflict
from src.data_access.resources import search_resources
from src.data_access.users import get_user_by_email


def test_allowed_file_basic():
    """Test that allowed file extensions return True"""
    assert allowed_file("image.png") == True
    assert allowed_file("photo.jpg") == True
    assert allowed_file("picture.jpeg") == True
    assert allowed_file("graphic.gif") == True
    assert allowed_file("icon.webp") == True


def test_allowed_file_case_insensitive():
    """Test that file extension check is case-insensitive"""
    assert allowed_file("IMAGE.PNG") == True
    assert allowed_file("Photo.JPG") == True
    assert allowed_file("picture.JPEG") == True
    assert allowed_file("graphic.GIF") == True


def test_allowed_file_invalid_extensions():
    """Test that disallowed file extensions return False"""
    assert allowed_file("document.pdf") == False
    assert allowed_file("script.js") == False
    assert allowed_file("data.csv") == False
    assert allowed_file("video.mp4") == False
    assert allowed_file("file.txt") == False


def test_allowed_file_no_extension():
    """Test that files without extensions return False"""
    assert allowed_file("filename") == False
    assert allowed_file("file.") == False
    assert allowed_file("") == False


def test_allowed_file_invalid_type():
    """Test that non-string input raises an error or returns False"""
    # None raises TypeError (not iterable)
    with pytest.raises(TypeError):
        allowed_file(None)
    # Numbers raise TypeError (not iterable for 'in' operator)
    with pytest.raises(TypeError):
        allowed_file(123)
    # Empty list returns False ('.' not in list, short-circuits)
    assert allowed_file([]) == False


@pytest.fixture()
def app():
    app = create_app({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "WTF_CSRF_ENABLED": False,
        "SECRET_KEY": "test",
    })
    with app.app_context():
        db.create_all()
        # Create test data
        from datetime import time
        from src.extensions import bcrypt
        owner = User(email="owner@example.com", name="Owner", role="staff", 
                    password_hash=bcrypt.generate_password_hash("x").decode())
        db.session.add(owner)
        db.session.flush()
        resource = Resource(
            title="Test Room",
            description="Test room description",
            category="study",
            location="Building A",
            capacity=10,
            owner_id=owner.id,
            status="published",
            opening_time=time(7, 0),
            closing_time=time(23, 59),
            booking_type="open"
        )
        db.session.add(resource)
        db.session.commit()
    yield app


def test_has_conflict_no_conflict(app):
    """Test that has_conflict returns False when no conflicts exist"""
    with app.app_context():
        resource = Resource.query.first()
        now = datetime.utcnow()
        start = (now + timedelta(hours=1)).replace(minute=0, second=0, microsecond=0)
        end = start + timedelta(hours=1)
        
        assert has_conflict(resource.id, start, end) == False


def test_has_conflict_with_conflict(app):
    """Test that has_conflict returns True when a conflict exists"""
    with app.app_context():
        from src.extensions import bcrypt
        resource = Resource.query.first()
        user = User(email="user@example.com", name="User", role="student",
                   password_hash=bcrypt.generate_password_hash("x").decode())
        db.session.add(user)
        db.session.flush()
        
        now = datetime.utcnow()
        start = (now + timedelta(hours=1)).replace(minute=0, second=0, microsecond=0)
        end = start + timedelta(hours=1)
        
        # Create an approved booking
        booking = Booking(resource_id=resource.id, user_id=user.id, 
                         start_time=start, end_time=end, status="approved")
        db.session.add(booking)
        db.session.commit()
        
        # Test overlapping time
        overlap_start = start + timedelta(minutes=30)
        overlap_end = overlap_start + timedelta(hours=1)
        
        assert has_conflict(resource.id, overlap_start, overlap_end) == True


def test_has_conflict_pending_not_conflict(app):
    """Test that pending bookings don't cause conflicts"""
    with app.app_context():
        from src.extensions import bcrypt
        resource = Resource.query.first()
        user = User(email="user2@example.com", name="User2", role="student",
                   password_hash=bcrypt.generate_password_hash("x").decode())
        db.session.add(user)
        db.session.flush()
        
        now = datetime.utcnow()
        start = (now + timedelta(hours=1)).replace(minute=0, second=0, microsecond=0)
        end = start + timedelta(hours=1)
        
        # Create a pending booking (should not conflict)
        booking = Booking(resource_id=resource.id, user_id=user.id,
                         start_time=start, end_time=end, status="pending")
        db.session.add(booking)
        db.session.commit()
        
        # Test overlapping time - should not conflict because booking is pending
        overlap_start = start + timedelta(minutes=30)
        overlap_end = overlap_start + timedelta(hours=1)
        
        assert has_conflict(resource.id, overlap_start, overlap_end) == False


def test_search_resources_by_keyword(app):
    """Test searching resources by keyword"""
    with app.app_context():
        # Create additional resources
        owner = User.query.first()
        from datetime import time
        resource2 = Resource(
            title="Meeting Room",
            description="Large meeting space",
            category="study",
            location="Building B",
            capacity=20,
            owner_id=owner.id,
            status="published",
            opening_time=time(7, 0),
            closing_time=time(23, 59),
            booking_type="open"
        )
        db.session.add(resource2)
        db.session.commit()
        
        # Search by keyword in title
        results = search_resources(keyword="Test")
        assert len(results) == 1
        assert results[0].title == "Test Room"
        
        # Search by keyword in description
        results = search_resources(keyword="meeting")
        assert len(results) == 1
        assert results[0].title == "Meeting Room"


def test_search_resources_by_category(app):
    """Test searching resources by category"""
    with app.app_context():
        owner = User.query.first()
        from datetime import time
        resource2 = Resource(
            title="Lab Equipment",
            description="Microscope",
            category="lab",
            location="Lab 1",
            capacity=1,
            owner_id=owner.id,
            status="published",
            opening_time=time(7, 0),
            closing_time=time(23, 59),
            booking_type="open"
        )
        db.session.add(resource2)
        db.session.commit()
        
        # Search by category
        results = search_resources(category="lab")
        assert len(results) == 1
        assert results[0].category == "lab"
        assert results[0].title == "Lab Equipment"


def test_search_resources_keyword_and_category(app):
    """Test searching resources by both keyword and category"""
    with app.app_context():
        owner = User.query.first()
        from datetime import time
        resource2 = Resource(
            title="Study Room A",
            description="Quiet study space",
            category="study",
            location="Library",
            capacity=4,
            owner_id=owner.id,
            status="published",
            opening_time=time(7, 0),
            closing_time=time(23, 59),
            booking_type="open"
        )
        db.session.add(resource2)
        db.session.commit()
        
        # Search by both keyword and category
        results = search_resources(keyword="Study", category="study")
        assert len(results) >= 1
        assert all(r.category == "study" for r in results)
        assert any("Study" in r.title or "Study" in r.description for r in results)


def test_get_user_by_email_exists(app):
    """Test retrieving a user by email when user exists"""
    with app.app_context():
        user = get_user_by_email("owner@example.com")
        assert user is not None
        assert user.email == "owner@example.com"
        assert user.name == "Owner"


def test_get_user_by_email_not_exists(app):
    """Test retrieving a user by email when user doesn't exist"""
    with app.app_context():
        user = get_user_by_email("nonexistent@example.com")
        assert user is None


def test_get_user_by_email_case_sensitive(app):
    """Test that email lookup is case-sensitive (database constraint)"""
    with app.app_context():
        # Email lookup should be exact match
        user = get_user_by_email("OWNER@EXAMPLE.COM")
        # Depending on database collation, this might or might not match
        # SQLite is case-sensitive by default, so this should return None
        assert user is None or user.email == "OWNER@EXAMPLE.COM"

