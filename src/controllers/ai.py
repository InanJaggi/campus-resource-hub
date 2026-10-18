# AI Contribution: Cursor AI suggested the MCP (Model Context Protocol) endpoint structure
# for safe, read-only database queries. The implementation was reviewed and enhanced with
# proper error handling and query limits.

from flask import Blueprint, jsonify, request
from flask_login import login_required
from ..models.models import Resource, Booking, Review

# MCP-like read-only endpoints for AI agents: strictly GET and JSON.
bp = Blueprint("ai", __name__)


@bp.get("/resources")
def ai_resources():
    q = request.args.get("q", "").strip()
    query = Resource.query
    if q:
        like = f"%{q}%"
        query = query.filter((Resource.title.ilike(like)) | (Resource.description.ilike(like)))
    records = query.limit(100).all()
    return jsonify([
        {
            "id": r.id,
            "title": r.title,
            "category": r.category,
            "location": r.location,
            "capacity": r.capacity,
            "rating": r.avg_rating,
            "status": r.status,
        }
        for r in records
    ])


@bp.get("/resource/<int:resource_id>/schedule")
def ai_resource_schedule(resource_id: int):
    bookings = (
        Booking.query.filter_by(resource_id=resource_id, status="approved")
        .order_by(Booking.start_time.asc())
        .limit(200)
        .all()
    )
    return jsonify([
        {
            "start": b.start_time.isoformat(),
            "end": b.end_time.isoformat(),
            "user_id": b.user_id,
        }
        for b in bookings
    ])


@bp.get("/resource/<int:resource_id>/reviews")
def ai_resource_reviews(resource_id: int):
    reviews = Review.query.filter_by(resource_id=resource_id).order_by(Review.created_at.desc()).limit(100).all()
    return jsonify([
        {
            "rating": rv.rating,
            "comment": rv.comment,
            "user_id": rv.user_id,
            "created_at": rv.created_at.isoformat(),
        }
        for rv in reviews
    ])


