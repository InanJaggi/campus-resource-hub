import pytest
from datetime import datetime, timedelta, time
from src.app import create_app
from src.extensions import db, bcrypt
from src.models.models import User, Resource, Booking


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
        # seed user and resource
        u = User(email="owner@example.com", name="Owner", role="staff", password_hash=bcrypt.generate_password_hash("x").decode())
        db.session.add(u)
        db.session.flush()
        r = Resource(
            title="Room 101", 
            description="Study room", 
            category="study", 
            location="Bldg A", 
            capacity=4, 
            owner_id=u.id, 
            status="published",
            opening_time=time(7, 0),  # 7 AM
            closing_time=time(23, 59),  # 11:59 PM
            booking_type="restricted"
        )
        db.session.add(r)
        db.session.commit()
    yield app


@pytest.fixture()
def client(app):
    return app.test_client()


def test_conflict_detection(app, client):
    # register + login as student
    client.post("/auth/register", data={"name": "Bob", "email": "bob@example.com", "password": "pwd", "csrf_token": ""}, follow_redirects=True)
    client.post("/auth/login", data={"email": "bob@example.com", "password": "pwd", "csrf_token": ""}, follow_redirects=True)

    # get resource id
    from src.models.models import Resource
    with app.app_context():
        resource = Resource.query.filter_by(title="Room 101").first()

    # Round to 15-minute intervals
    now = datetime.utcnow()
    start = (now + timedelta(hours=1)).replace(minute=0, second=0, microsecond=0)
    end = start + timedelta(hours=2)

    # Format for form input (datetime-local format)
    start_str = start.strftime("%Y-%m-%dT%H:%M")
    end_str = end.strftime("%Y-%m-%dT%H:%M")

    # first booking request
    r = client.post(f"/bookings/new/{resource.id}", data={
        "start": start_str, 
        "end": end_str,
        "csrf_token": ""
    }, follow_redirects=True)
    assert r.status_code == 200

    # approve as owner: need login as owner
    client.get("/auth/logout", follow_redirects=True)
    client.post("/auth/login", data={"email": "owner@example.com", "password": "x", "csrf_token": ""}, follow_redirects=True)
    with app.app_context():
        b = Booking.query.first()
    r = client.post(f"/bookings/{b.id}/approve", data={"csrf_token": ""}, follow_redirects=True)
    assert r.status_code == 200

    # new overlapping booking should be rejected at creation time
    client.get("/auth/logout", follow_redirects=True)
    client.post("/auth/login", data={"email": "bob@example.com", "password": "pwd", "csrf_token": ""}, follow_redirects=True)
    
    # Overlapping time (30 minutes into the first booking)
    overlap_start = start + timedelta(minutes=30)
    overlap_start = overlap_start.replace(minute=0 if overlap_start.minute < 15 else (15 if overlap_start.minute < 30 else (30 if overlap_start.minute < 45 else 45)), second=0, microsecond=0)
    overlap_end = overlap_start + timedelta(hours=2)
    
    overlap_start_str = overlap_start.strftime("%Y-%m-%dT%H:%M")
    overlap_end_str = overlap_end.strftime("%Y-%m-%dT%H:%M")
    
    r2 = client.post(f"/bookings/new/{resource.id}", data={
        "start": overlap_start_str, 
        "end": overlap_end_str,
        "csrf_token": ""
    }, follow_redirects=True)
    assert r2.status_code == 200
    assert b"Time slot not available" in r2.data or b"waitlist" in r2.data.lower()


