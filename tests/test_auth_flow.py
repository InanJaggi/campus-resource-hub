import pytest
from src.app import create_app
from src.extensions import db


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


def test_register_login_and_protected(app, client):
    # register
    r = client.post("/auth/register", data={
        "name": "Alice",
        "email": "alice@example.com",
        "role": "student",
        "password": "password123",
        "csrf_token": ""  # CSRF disabled in test config
    }, follow_redirects=True)
    assert r.status_code == 200

    # login
    r = client.post("/auth/login", data={
        "email": "alice@example.com",
        "password": "password123",
        "csrf_token": ""  # CSRF disabled in test config
    }, follow_redirects=True)
    assert r.status_code == 200

    # access protected page (my bookings)
    r = client.get("/bookings")
    assert r.status_code == 200


