import pytest
from datetime import datetime, timedelta
from src.app import create_app
from src.extensions import db, bcrypt
from src.models.models import User, Resource, Booking, Waitlist


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
        from datetime import time
        owner = User(email="owner@example.com", name="Owner", role="staff", password_hash=bcrypt.generate_password_hash("x").decode())
        db.session.add(owner)
        db.session.flush()
        res = Resource(
            title="Lab Scope", 
            description="Microscope", 
            category="lab", 
            location="B-2", 
            capacity=1, 
            owner_id=owner.id, 
            status="published",
            opening_time=time(7, 0),
            closing_time=time(23, 59),
            booking_type="restricted"
        )
        db.session.add(res)
        db.session.commit()
    yield app


@pytest.fixture()
def client(app):
    return app.test_client()


def test_waitlist_enroll_and_promotion(app, client):
    # student A books and gets approved by owner
    client.post("/auth/register", data={"name": "A", "email": "a@example.com", "password": "a", "csrf_token": ""}, follow_redirects=True)
    client.post("/auth/login", data={"email": "a@example.com", "password": "a", "csrf_token": ""}, follow_redirects=True)
    with app.app_context():
        res = Resource.query.filter_by(title="Lab Scope").first()
    
    # Round to 15-minute intervals and ensure minimum 30 minutes
    now = datetime.utcnow()
    start = (now + timedelta(hours=1)).replace(minute=0, second=0, microsecond=0)
    end = start + timedelta(hours=1)  # 1 hour booking
    
    start_str = start.strftime("%Y-%m-%dT%H:%M")
    end_str = end.strftime("%Y-%m-%dT%H:%M")
    
    client.post(f"/bookings/new/{res.id}", data={
        "start": start_str, 
        "end": end_str,
        "csrf_token": ""
    }, follow_redirects=True)
    with app.app_context():
        b = Booking.query.first()
    client.get("/auth/logout", follow_redirects=True)
    client.post("/auth/login", data={"email": "owner@example.com", "password": "x", "csrf_token": ""}, follow_redirects=True)
    client.post(f"/bookings/{b.id}/approve", data={"csrf_token": ""}, follow_redirects=True)

    # student B tries overlapping and should be waitlisted
    client.get("/auth/logout", follow_redirects=True)
    client.post("/auth/register", data={"name": "B", "email": "b@example.com", "password": "b", "csrf_token": ""}, follow_redirects=True)
    client.post("/auth/login", data={"email": "b@example.com", "password": "b", "csrf_token": ""}, follow_redirects=True)
    r = client.post(f"/bookings/new/{res.id}", data={
        "start": start_str, 
        "end": end_str,
        "csrf_token": ""
    }, follow_redirects=True)
    assert b"waitlist" in r.data.lower() or b"Time slot not available" in r.data
    with app.app_context():
        assert Waitlist.query.count() == 1

    # Student A cancels their approved booking; waitlisted student B should get a pending booking
    client.get("/auth/logout", follow_redirects=True)
    client.post("/auth/login", data={"email": "a@example.com", "password": "a", "csrf_token": ""}, follow_redirects=True)
    with app.app_context():
        from src.models.models import User
        user_a = User.query.filter_by(email="a@example.com").first()
        user_b = User.query.filter_by(email="b@example.com").first()
        approved = Booking.query.filter_by(status="approved", user_id=user_a.id).first()
        assert approved is not None, "Student A should have an approved booking"
    client.post(f"/bookings/{approved.id}/cancel", data={"csrf_token": ""}, follow_redirects=True)

    with app.app_context():
        # Waitlist should be empty (student B was promoted)
        assert Waitlist.query.count() == 0, "Waitlist should be empty after promotion"
        # Student B should have a pending booking (since resource is restricted and requires approval)
        pending_for_b = Booking.query.filter_by(user_id=user_b.id, status="pending").first()
        assert pending_for_b is not None, f"Student B should have a pending booking. Found bookings: {[b.id for b in Booking.query.filter_by(user_id=user_b.id).all()]}"
        # Times should match the cancelled booking's time slot (within a minute tolerance for rounding)
        assert abs((pending_for_b.start_time - start).total_seconds()) < 60, f"Start time mismatch: expected {start}, got {pending_for_b.start_time}"
        assert abs((pending_for_b.end_time - end).total_seconds()) < 60, f"End time mismatch: expected {end}, got {pending_for_b.end_time}"


