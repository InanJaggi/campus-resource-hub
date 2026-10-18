from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from ..extensions import db
from ..models.models import Review, Booking, Resource
from ..data_access.reviews import add_review

bp = Blueprint("reviews", __name__, url_prefix="/reviews")


@bp.route("")
@login_required
def list_reviews():
    """List all resources the user can review"""
    # Get all resources where user has completed bookings but hasn't reviewed yet
    completed_bookings = Booking.query.filter_by(
        user_id=current_user.id,
        status="completed"
    ).all()
    
    # Get resource IDs from completed bookings
    resource_ids = [b.resource_id for b in completed_bookings]
    
    # Get resources user can review (has completed booking but no review)
    reviewable_resources = []
    for resource_id in set(resource_ids):
        resource = Resource.query.get(resource_id)
        if resource:
            # Check if user already reviewed
            existing_review = Review.query.filter_by(
                resource_id=resource_id,
                user_id=current_user.id
            ).first()
            if not existing_review:
                reviewable_resources.append(resource)
    
    # Get resources user has already reviewed
    user_reviews = Review.query.filter_by(user_id=current_user.id).order_by(Review.created_at.desc()).all()
    
    return render_template("reviews/list.html",
        reviewable_resources=reviewable_resources,
        user_reviews=user_reviews
    )


@bp.route("/new/<int:resource_id>", methods=["GET", "POST"])
@login_required
def new_review(resource_id: int):
    resource = Resource.query.get_or_404(resource_id)
    
    # Check if user has a completed booking for this resource
    completed_booking = (
        Booking.query.filter_by(resource_id=resource_id, user_id=current_user.id, status="completed")
        .first()
    )
    
    if not completed_booking:
        flash("You can only review resources you have completed bookings for.", "warning")
        return redirect(url_for("resources.detail", resource_id=resource_id))
    
    # Check if user already reviewed this resource
    existing_review = Review.query.filter_by(resource_id=resource_id, user_id=current_user.id).first()
    if existing_review:
        flash("You have already reviewed this resource.", "info")
        return redirect(url_for("resources.detail", resource_id=resource_id))
    
    if request.method == "POST":
        rating = int(request.form.get("rating", 0))
        comment = request.form.get("comment", "").strip()
        
        if not rating or rating < 1 or rating > 5:
            flash("Please provide a valid rating (1-5)", "danger")
            return render_template("reviews/form.html", resource=resource)
        
        add_review(resource_id, current_user.id, rating, comment)
        flash("Review submitted successfully!", "success")
        return redirect(url_for("reviews.list_reviews"))
    
    return render_template("reviews/form.html", resource=resource)


@bp.route("", methods=["POST"])
@login_required
def submit_review():
    """POST /reviews - submit review (API endpoint)"""
    from flask import jsonify, request as req
    data = req.get_json() or {}
    resource_id = data.get("resource_id")
    rating = data.get("rating")
    comment = data.get("comment", "").strip()
    
    if not resource_id or not rating:
        return jsonify({"error": "resource_id and rating required"}), 400
    
    if rating < 1 or rating > 5:
        return jsonify({"error": "Rating must be between 1 and 5"}), 400
    
    # Check if user has completed booking
    completed_booking = (
        Booking.query.filter_by(resource_id=resource_id, user_id=current_user.id, status="completed")
        .first()
    )
    if not completed_booking:
        return jsonify({"error": "You can only review resources you have completed bookings for"}), 403
    
    # Check if already reviewed
    existing = Review.query.filter_by(resource_id=resource_id, user_id=current_user.id).first()
    if existing:
        return jsonify({"error": "You have already reviewed this resource"}), 400
    
    review = add_review(resource_id, current_user.id, rating, comment)
    return jsonify({"message": "Review submitted", "id": review.id}), 201

