import pytest
from bs4 import BeautifulSoup
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


def _soup(resp):
    return BeautifulSoup(resp.data.decode("utf-8"), "html.parser")


def test_index_has_semantic_landmarks(client):
    r = client.get("/")
    assert r.status_code == 200
    s = _soup(r)
    # nav landmark
    nav = s.find("nav", {"role": "navigation"})
    assert nav is not None
    # main region
    main = s.find("main", {"id": "main"})
    assert main is not None
    assert main.get("tabindex") == "-1"


def test_login_form_has_labels_and_inputs(client):
    r = client.get("/auth/login")
    assert r.status_code == 200
    s = _soup(r)
    labels = s.find_all("label")
    assert any(l.get("for") == "email" for l in labels)
    assert any(l.get("for") == "password" for l in labels)
    # Inputs present and typed
    assert s.find("input", {"id": "email", "type": "email"}) is not None
    assert s.find("input", {"id": "password", "type": "password"}) is not None


