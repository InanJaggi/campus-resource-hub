import pytest
from src.app import create_app
from src.extensions import db
from src.data_access.resources import create_resource, search_resources
from src.data_access.users import create_user


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
    yield app


def test_dal_crud(app):
    with app.app_context():
        from datetime import time
        u = create_user("x@example.com", "X", "hash", role="staff")
        r = create_resource(
            title="Microscope", 
            description="Optics", 
            category="lab", 
            location="B-2", 
            capacity=1, 
            owner_id=u.id, 
            status="published",
            opening_time=time(7, 0),
            closing_time=time(23, 59),
            booking_type="restricted"
        )
        results = search_resources("scope", "lab")
        assert len(results) == 1
        assert results[0].title == "Microscope"


