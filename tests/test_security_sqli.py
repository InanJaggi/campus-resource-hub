import pytest
from src.app import create_app
from src.extensions import db
from src.models.models import User


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


@pytest.fixture()
def client(app):
    return app.test_client()


def test_sql_injection_protection(client):
    # Try to inject in login field (harmless due to ORM filters)
    r = client.post("/auth/login", data={
        "email": "x' OR '1'='1", 
        "password": "whatever",
        "csrf_token": ""
    }, follow_redirects=True)
    # Should not 500, simply invalid creds
    assert r.status_code == 200
    assert b"Invalid" in r.data or b"credentials" in r.data.lower()


