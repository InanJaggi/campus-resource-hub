from flask import Blueprint, render_template, redirect, url_for, request, flash, jsonify
from flask_login import login_required, current_user
from datetime import datetime, timedelta
from sqlalchemy import func, extract
from ..extensions import db
from ..models.models import User, Booking, Review, AdminLog, Resource

bp = Blueprint("admin", __name__, url_prefix="/admin")


def _require_admin():
    if not current_user.is_authenticated or current_user.role != "admin":
        return False
    return True


def _log_admin_action(action: str, target_table: str = None, details: str = None):
    """Helper to log admin actions"""
    from ..utils.admin_logging import log_admin_action
    log_admin_action(current_user.id, action, target_table, details)


@bp.route("/")
@login_required
def dashboard():
    if not _require_admin():
        flash("Admin only", "danger")
        return redirect(url_for("index"))
    
    # Comprehensive statistics
    from datetime import datetime
    now = datetime.utcnow()
    
    # Basic counts
    total_users = User.query.count()
    total_resources = Resource.query.count()
    total_bookings = Booking.query.count()
    total_reviews = Review.query.count()
    
    # Active bookings (approved and upcoming)
    active_bookings = Booking.query.filter(
        Booking.status == "approved",
        Booking.end_time >= now
    ).count()
    
    # Average rating across all resources
    avg_rating = db.session.query(func.avg(Resource.avg_rating)).filter(
        Resource.avg_rating > 0
    ).scalar() or 0
    
    # Most popular booking time (hour of day)
    popular_hour = db.session.query(
        extract('hour', Booking.start_time).label('hour'),
        func.count(Booking.id).label('count')
    ).filter(
        Booking.status.in_(['approved', 'completed'])
    ).group_by('hour').order_by(func.count(Booking.id).desc()).first()
    
    popular_booking_hour = popular_hour[0] if popular_hour else None
    popular_booking_count = popular_hour[1] if popular_hour else 0
    
    # Booking status breakdown
    pending_bookings = Booking.query.filter_by(status="pending").count()
    approved_bookings = Booking.query.filter_by(status="approved").count()
    completed_bookings = Booking.query.filter_by(status="completed").count()
    cancelled_bookings = Booking.query.filter_by(status="cancelled").count()
    
    # Recent activity
    recent_users = User.query.order_by(User.created_at.desc()).limit(5).all()
    recent_bookings = Booking.query.order_by(Booking.created_at.desc()).limit(5).all()
    recent_reviews = Review.query.order_by(Review.created_at.desc()).limit(5).all()
    
    # Resources with most bookings
    popular_resources = db.session.query(
        Resource, func.count(Booking.id).label('booking_count')
    ).join(Booking).group_by(Resource.id).order_by(
        func.count(Booking.id).desc()
    ).limit(5).all()
    
    return render_template("admin/dashboard.html",
        total_users=total_users,
        total_resources=total_resources,
        total_bookings=total_bookings,
        total_reviews=total_reviews,
        active_bookings=active_bookings,
        avg_rating=round(avg_rating, 2),
        popular_booking_hour=popular_booking_hour,
        popular_booking_count=popular_booking_count,
        pending_bookings=pending_bookings,
        approved_bookings=approved_bookings,
        completed_bookings=completed_bookings,
        cancelled_bookings=cancelled_bookings,
        recent_users=recent_users,
        recent_bookings=recent_bookings,
        recent_reviews=recent_reviews,
        popular_resources=popular_resources
    )


@bp.route("/stats", methods=["GET"])
@login_required
def stats():
    """GET /admin/stats - usage metrics (API endpoint)"""
    if not _require_admin():
        from flask import jsonify
        return jsonify({"error": "Admin only"}), 403
    
    from sqlalchemy import func
    from ..models.models import User, Resource, Booking, Review
    
    stats_data = {
        "total_users": User.query.count(),
        "total_resources": Resource.query.count(),
        "total_bookings": Booking.query.count(),
        "total_reviews": Review.query.count(),
        "pending_bookings": Booking.query.filter_by(status="pending").count(),
        "approved_bookings": Booking.query.filter_by(status="approved").count(),
        "completed_bookings": Booking.query.filter_by(status="completed").count(),
    }
    
    from flask import jsonify
    return jsonify(stats_data), 200


@bp.route("/logs")
@login_required
def logs():
    """View admin action logs"""
    if not _require_admin():
        flash("Admin only", "danger")
        return redirect(url_for("index"))
    
    logs = AdminLog.query.order_by(AdminLog.created_at.desc()).all()
    return render_template("admin/logs.html", logs=logs)


@bp.route("/booking-logs")
@login_required
def booking_logs():
    """View all booking logs"""
    if not _require_admin():
        flash("Admin only", "danger")
        return redirect(url_for("index"))
    
    bookings = Booking.query.order_by(Booking.created_at.desc()).all()
    return render_template("admin/booking_logs.html", bookings=bookings)


@bp.route("/users")
@login_required
def users():
    """User management page"""
    if not _require_admin():
        flash("Admin only", "danger")
        return redirect(url_for("index"))
    
    users_list = User.query.order_by(User.created_at.desc()).all()
    return render_template("admin/users.html", users=users_list)


@bp.route("/users/<int:user_id>", methods=["GET", "POST"])
@login_required
def edit_user(user_id: int):
    """View and edit user details"""
    if not _require_admin():
        flash("Admin only", "danger")
        return redirect(url_for("index"))
    
    user = User.query.get_or_404(user_id)
    
    if request.method == "POST":
        old_data = {
            "name": user.name,
            "email": user.email,
            "role": user.role,
            "department": user.department
        }
        
        user.name = request.form.get("name", user.name).strip()
        user.email = request.form.get("email", user.email).strip().lower()
        user.role = request.form.get("role", user.role)
        user.department = request.form.get("department", user.department).strip() if request.form.get("department") else None
        
        changes = []
        for key, old_value in old_data.items():
            new_value = getattr(user, key)
            if old_value != new_value:
                changes.append(f"{key}: {old_value} → {new_value}")
        
        if changes:
            from ..utils.admin_logging import log_admin_action
            log_admin_action(
                current_user.id,
                "edit_user",
                "users",
                f"User {user_id}: {', '.join(changes)}"
            )
            flash("User updated successfully", "success")
        else:
            flash("No changes made", "info")
        
        return redirect(url_for("admin.edit_user", user_id=user_id))
    
    # Get user's bookings and resources
    user_bookings = Booking.query.filter_by(user_id=user_id).order_by(Booking.created_at.desc()).all()
    user_resources = Resource.query.filter_by(owner_id=user_id).all()
    user_reviews = Review.query.filter_by(user_id=user_id).all()
    
    return render_template("admin/edit_user.html",
        user=user,
        bookings=user_bookings,
        resources=user_resources,
        reviews=user_reviews
    )


@bp.route("/promote/<int:user_id>", methods=["POST"])
@login_required
def promote(user_id: int):
    if not _require_admin():
        flash("Admin only", "danger")
        return redirect(url_for("admin.dashboard"))
    user = User.query.get_or_404(user_id)
    old_role = user.role
    user.role = "staff"
    from ..utils.admin_logging import log_admin_action
    log_admin_action(
        current_user.id,
        "promote_user",
        "users",
        f"Promoted user {user_id} from {old_role} to staff"
    )
    flash("User promoted to staff", "success")
    return redirect(url_for("admin.users"))


