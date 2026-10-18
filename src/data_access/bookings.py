# AI Contribution: Cursor AI suggested the conflict detection algorithm and booking CRUD structure.
# The has_conflict function was reviewed and enhanced with proper datetime handling and query optimization.

from datetime import datetime
from typing import Optional, List
from ..extensions import db
from ..models.models import Booking


def has_conflict(resource_id: int, start: datetime, end: datetime) -> bool:
    conflict = (
        Booking.query.filter_by(resource_id=resource_id, status="approved")
        .filter(Booking.start_time < end, Booking.end_time > start)
        .first()
    )
    return conflict is not None


def create_booking(resource_id: int, user_id: int, start: datetime, end: datetime) -> Booking:
    booking = Booking(resource_id=resource_id, user_id=user_id, start_time=start, end_time=end, status="pending")
    db.session.add(booking)
    db.session.commit()
    return booking


def approve_booking(booking: Booking) -> Booking:
    booking.status = "approved"
    db.session.commit()
    return booking


def user_bookings(user_id: int) -> List[Booking]:
    return Booking.query.filter_by(user_id=user_id).order_by(Booking.start_time.desc()).all()


