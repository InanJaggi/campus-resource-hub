from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from datetime import datetime, timedelta, time
from ..extensions import db
from ..models.models import Booking, Resource, User, MessageThread, Message
from ..data_access.waitlist import join_waitlist, remove_waitlist_entry


bp = Blueprint("bookings", __name__, url_prefix="/bookings")


def _parse_dt(dt_str: str) -> datetime | None:
    """Parse datetime string from form input"""
    if not dt_str:
        return None
    try:
        return datetime.strptime(dt_str, "%Y-%m-%dT%H:%M")
    except ValueError:
        return None


def _get_or_create_system_user():
    """Get or create the Campus Booking Services system user"""
    system_user = User.query.filter_by(email="system@campus.edu").first()
    if not system_user:
        from ..extensions import bcrypt
        system_user = User(
            email="system@campus.edu",
            name="Campus Booking Services",
            password_hash=bcrypt.generate_password_hash("system").decode(),
            role="admin"
        )
        db.session.add(system_user)
        db.session.commit()
    return system_user


def _send_booking_message(user_id: int, booking: Booking, message_type: str):
    """Send a message to a user about their booking (approved/rejected)"""
    system_user = _get_or_create_system_user()
    
    # Find or create thread between system user and the booking user
    thread = MessageThread.query.filter(
        ((MessageThread.user_a_id == system_user.id) & (MessageThread.user_b_id == user_id)) |
        ((MessageThread.user_a_id == user_id) & (MessageThread.user_b_id == system_user.id))
    ).first()
    
    if not thread:
        thread = MessageThread(user_a_id=system_user.id, user_b_id=user_id)
        db.session.add(thread)
        db.session.flush()
    
    # Create message content based on type
    resource = booking.resource
    if message_type == "approved":
        body = f"Your booking request for {resource.title} has been approved.\n\n"
        body += f"Resource: {resource.title}\n"
        body += f"Location: {resource.location}\n"
        body += f"Start Time: {booking.start_time.strftime('%Y-%m-%d %I:%M %p')}\n"
        body += f"End Time: {booking.end_time.strftime('%Y-%m-%d %I:%M %p')}\n\n"
        body += "Your booking is confirmed. Please arrive on time."
    elif message_type == "rejected":
        body = f"Your booking request for {resource.title} has been rejected.\n\n"
        body += f"Resource: {resource.title}\n"
        body += f"Location: {resource.location}\n"
        body += f"Requested Time: {booking.start_time.strftime('%Y-%m-%d %I:%M %p')} to {booking.end_time.strftime('%Y-%m-%d %I:%M %p')}\n\n"
        body += "Unfortunately, this booking could not be approved. Please try selecting a different time slot or contact the resource owner for more information."
    else:
        return
    
    # Create and send message
    message = Message(
        thread_id=thread.id,
        sender_id=system_user.id,
        receiver_id=user_id,
        body=body,
        is_read=False
    )
    db.session.add(message)
    db.session.commit()


def _send_notification(email: str, notification_type: str, booking: Booking):
    """Simulate email notification (console print for now)"""
    resource = booking.resource
    if notification_type == "booking_requested":
        print(f"Email to: {email}")
        print(f"Subject: New Booking Request - {resource.title}")
        print(f"Body: {booking.user.name} has requested to book {resource.title} from {booking.start_time} to {booking.end_time}.")
    elif notification_type == "booking_approved":
        print(f"Email to: {email}")
        print(f"Subject: Booking Approved - {resource.title}")
        print(f"Body: Your booking for {resource.title} from {booking.start_time} to {booking.end_time} has been approved.")
    elif notification_type == "booking_cancelled":
        print(f"Email to: {email}")
        print(f"Subject: Booking Cancelled - {resource.title}")
        print(f"Body: Your booking for {resource.title} has been cancelled.")


def _render_calendar_view(resource: Resource):
    """Render the calendar booking view"""
    from calendar import day_name, month_name
    
    # Get week start date (Monday)
    week_str = request.args.get("week")
    if week_str:
        try:
            week_start = datetime.strptime(week_str, "%Y-%m-%d").date()
            # Ensure it's a Monday
            days_since_monday = week_start.weekday()
            if days_since_monday != 0:
                week_start = week_start - timedelta(days=days_since_monday)
        except ValueError:
            week_start = datetime.now().date()
            # Get Monday of current week
            days_since_monday = week_start.weekday()
            if days_since_monday != 0:
                week_start = week_start - timedelta(days=days_since_monday)
    else:
        week_start = datetime.now().date()
        # Get Monday of current week
        days_since_monday = week_start.weekday()
        if days_since_monday != 0:
            week_start = week_start - timedelta(days=days_since_monday)
    
    # Calculate week end (Sunday)
    week_end = week_start + timedelta(days=6)
    
    # Get days of week
    days_of_week = []
    for i in range(7):
        day_date = week_start + timedelta(days=i)
        days_of_week.append({
            'name': day_name[day_date.weekday()],
            'date': day_date.strftime('%b %d'),
            'iso': day_date.isoformat()
        })
    
    # Get hours for calendar display (always show 7am-11pm for full day view)
    # Operating hours will be enforced via JavaScript and validation
    hours = list(range(7, 24))  # 7am to 11pm (displayed as 7-23)
    
    # Get all bookings for this resource in this week (approved and pending)
    week_start_dt = datetime.combine(week_start, time.min)
    week_end_dt = datetime.combine(week_end, time.max)
    
    bookings = Booking.query.filter(
        Booking.resource_id == resource.id,
        Booking.status.in_(["approved", "pending"]),
        Booking.start_time <= week_end_dt,
        Booking.end_time >= week_start_dt
    ).all()
    
    # Format booked slots for JavaScript
    booked_slots = []
    for booking in bookings:
        user = User.query.get(booking.user_id)
        booked_slots.append({
            'start': booking.start_time.isoformat(),
            'end': booking.end_time.isoformat(),
            'user_name': user.name if user else 'Unknown'
        })
    
    return render_template(
        "bookings/calendar.html",
        resource=resource,
        days_of_week=days_of_week,
        hours=hours,
        booked_slots=booked_slots,
        current_week_start=week_start
    )


@bp.route("/new/<int:resource_id>", methods=["GET", "POST"])
@login_required
def new_booking(resource_id: int):
    resource = Resource.query.get_or_404(resource_id)
    
    # Handle calendar view
    view = request.args.get("view", "form")
    if view == "calendar" and request.method == "GET":
        return _render_calendar_view(resource)
    
    if request.method == "POST":
        start = _parse_dt(request.form.get("start"))
        end = _parse_dt(request.form.get("end"))
        # Get view parameter from request (check both args and form data)
        view = request.args.get("view") or request.form.get("view") or "form"
        
        if not start or not end or start >= end:
            flash("Invalid time range", "danger")
            # Return to appropriate view
            if view == "calendar":
                return _render_calendar_view(resource)
            return render_template("bookings/form.html", resource=resource)
        
        # Check minimum booking duration (30 minutes)
        duration = end - start
        if duration < timedelta(minutes=29):  # Less than 29 minutes = invalid (must be 30+)
            flash("Minimum booking duration is 30 minutes", "danger")
            if view == "calendar":
                return _render_calendar_view(resource)
            return render_template("bookings/form.html", resource=resource)
        
        # Check hours of operation
        if resource.opening_time and resource.closing_time:
            start_time_only = start.time()
            end_time_only = end.time()
            
            # Check if booking starts and ends within operating hours
            if start_time_only < resource.opening_time or end_time_only > resource.closing_time:
                flash(f"This resource is only available from {resource.opening_time.strftime('%I:%M %p')} to {resource.closing_time.strftime('%I:%M %p')}. Your booking is outside these hours.", "danger")
                if view == "calendar":
                    return _render_calendar_view(resource)
                return render_template("bookings/form.html", resource=resource)
        
        # Round times to 15-minute intervals (validate)
        start_minute = start.minute
        end_minute = end.minute
        if start_minute % 15 != 0 or end_minute % 15 != 0:
            flash("Booking times must be in 15-minute intervals (e.g., :00, :15, :30, :45)", "danger")
            if view == "calendar":
                return _render_calendar_view(resource)
            return render_template("bookings/form.html", resource=resource)
        
        # Check for recurrence
        recurrence = request.form.get("recurrence", "").strip() or None
        
        # conflict detection - check for approved or pending bookings that conflict
        conflict = (
            Booking.query.filter_by(resource_id=resource.id)
            .filter(Booking.status.in_(["approved", "pending"]))
            .filter(Booking.start_time < end, Booking.end_time > start)
            .first()
        )
        
        if conflict:
            # Check if user is already on waitlist for this exact time slot
            from ..models.models import Waitlist
            existing_waitlist = Waitlist.query.filter_by(
                resource_id=resource.id,
                user_id=current_user.id
            ).filter(
                Waitlist.desired_start == start,
                Waitlist.desired_end == end
            ).first()
            
            if existing_waitlist:
                flash("You are already on the waitlist for this time slot.", "info")
            else:
                # Auto-enroll to waitlist
                join_waitlist(resource.id, current_user.id, start, end)
                flash("Time slot not available. You have been added to the waitlist. You will be automatically notified if this time slot becomes available.", "warning")
            
            # Redirect back to calendar or resource detail based on view
            if view == "calendar":
                return redirect(url_for("bookings.new_booking", resource_id=resource.id, view="calendar"))
            return redirect(url_for("resources.detail", resource_id=resource.id))
        
        # No conflict - proceed with booking
        # Determine booking status based on resource booking type
        if resource.booking_type == "open":
            # Open resources: automatically approve (no conflict, so safe to approve)
            booking_status = "approved"
            flash_message = "Booking confirmed! Your booking has been automatically approved."
        else:
            # Restricted resources: require approval
            booking_status = "pending"
            flash_message = "Booking requested. Awaiting approval from resource owner."
        
        booking = Booking(resource_id=resource.id, user_id=current_user.id,
                          start_time=start, end_time=end, status=booking_status, recurrence_pattern=recurrence)
        db.session.add(booking)
        db.session.commit()
        
        # Send notification based on booking type
        owner = resource.owner
        if resource.booking_type == "open":
            # For open resources, notify user of approval
            _send_notification(current_user.email, "booking_approved", booking)
        else:
            # For restricted resources, notify owner of booking request
            _send_notification(owner.email, "booking_requested", booking)
        
        flash(flash_message, "success")
        
        # Redirect back to calendar or resource detail based on view
        if view == "calendar":
            return redirect(url_for("bookings.new_booking", resource_id=resource.id, view="calendar"))
        return redirect(url_for("resources.detail", resource_id=resource.id))
    
    # Check if calendar view is requested
    view = request.args.get("view", "calendar")  # Default to calendar view
    if view == "calendar":
        return _render_calendar_view(resource)
    
    return render_template("bookings/form.html", resource=resource)


@bp.route("")
@login_required
def my_bookings():
    """List user's bookings"""
    all_bookings = Booking.query.filter_by(user_id=current_user.id).order_by(Booking.start_time.desc()).all()
    now = datetime.utcnow()
    
    # Auto-mark past approved bookings as completed
    for booking in all_bookings:
        if booking.status == "approved" and booking.end_time < now:
            booking.status = "completed"
    db.session.commit()
    
    # Re-fetch to get updated statuses
    all_bookings = Booking.query.filter_by(user_id=current_user.id).order_by(Booking.start_time.desc()).all()
    past_bookings = [b for b in all_bookings if b.end_time < now or b.status in ['completed', 'cancelled']]
    current_bookings = [b for b in all_bookings if b.status == "approved" and b.start_time <= now <= b.end_time]
    upcoming_bookings = [b for b in all_bookings if b.status in ['pending', 'approved'] and b.start_time > now]
    
    # Get user's waitlist entries with position information
    from ..data_access.waitlist import get_user_waitlist
    from ..models.models import Waitlist
    from sqlalchemy.orm import joinedload
    
    # Eagerly load resource relationship to avoid N+1 queries
    waitlist_entries = (
        Waitlist.query
        .options(joinedload(Waitlist.resource))
        .filter_by(user_id=current_user.id)
        .order_by(Waitlist.created_at.desc())
        .all()
    )
    
    # Calculate position for each waitlist entry
    waitlist_with_positions = []
    for entry in waitlist_entries:
        # Get all waitlist entries for this resource, ordered by creation time
        all_entries = Waitlist.query.filter_by(resource_id=entry.resource_id).order_by(Waitlist.created_at.asc()).all()
        position = next((i + 1 for i, e in enumerate(all_entries) if e.id == entry.id), len(all_entries))
        waitlist_with_positions.append((entry, position))
    
    return render_template("bookings/my_bookings.html",
        past_bookings=past_bookings,
        current_bookings=current_bookings,
        upcoming_bookings=upcoming_bookings,
        waitlist_with_positions=waitlist_with_positions,
        now=now
    )


@bp.route("/resource-owner")
@login_required
def resource_owner_bookings():
    """List bookings for resources owned by the current user"""
    # Get all resources owned by current user
    owned_resources = Resource.query.filter_by(owner_id=current_user.id).all()
    if not owned_resources:
        flash("You don't own any resources yet.", "info")
        return redirect(url_for("resources.list_resources"))
    
    resource_ids = [r.id for r in owned_resources]
    
    # Get all bookings for owned resources, ordered by start time (most recent first)
    all_bookings = Booking.query.filter(
        Booking.resource_id.in_(resource_ids)
    ).order_by(Booking.start_time.desc()).all()
    
    # Separate by status
    pending_bookings = [b for b in all_bookings if b.status == "pending"]
    approved_bookings = [b for b in all_bookings if b.status == "approved"]
    completed_bookings = [b for b in all_bookings if b.status == "completed"]
    cancelled_bookings = [b for b in all_bookings if b.status in ["cancelled", "rejected"]]
    
    return render_template("bookings/resource_owner_bookings.html",
        pending_bookings=pending_bookings,
        approved_bookings=approved_bookings,
        completed_bookings=completed_bookings,
        cancelled_bookings=cancelled_bookings,
        owned_resources=owned_resources
    )


@bp.route("/<int:booking_id>", methods=["GET"])
@login_required
def booking_detail(booking_id: int):
    """View booking details"""
    booking = Booking.query.get_or_404(booking_id)
    if booking.user_id != current_user.id and current_user.role != "admin" and booking.resource.owner_id != current_user.id:
        flash("Not authorized", "danger")
        return redirect(url_for("bookings.my_bookings"))
    
    # Determine if booking can be edited (upcoming and approved/pending)
    now = datetime.utcnow()
    can_edit = (
        booking.start_time > now and
        booking.status in ['pending', 'approved'] and
        booking.user_id == current_user.id
    )
    
    return render_template("bookings/detail.html", booking=booking, can_edit=can_edit)


@bp.route("/<int:booking_id>/edit", methods=["GET", "POST"])
@login_required
def edit_booking(booking_id: int):
    """Edit upcoming booking"""
    booking = Booking.query.get_or_404(booking_id)
    
    # Only user who made booking can edit, and only if upcoming
    if booking.user_id != current_user.id:
        flash("Not authorized", "danger")
        return redirect(url_for("bookings.my_bookings"))
    
    now = datetime.utcnow()
    if booking.start_time <= now or booking.status not in ['pending', 'approved']:
        flash("Only upcoming bookings can be edited", "warning")
        return redirect(url_for("bookings.booking_detail", booking_id=booking_id))
    
    if request.method == "POST":
        start = _parse_dt(request.form.get("start"))
        end = _parse_dt(request.form.get("end"))
        recurrence = request.form.get("recurrence", "").strip() or None
        
        if not start or not end or start >= end:
            flash("Invalid time range", "danger")
            return render_template("bookings/edit.html", booking=booking)
        
        # Check minimum booking duration (30 minutes)
        duration = end - start
        if duration < timedelta(minutes=29):  # Less than 29 minutes = invalid (must be 30+)
            flash("Minimum booking duration is 30 minutes", "danger")
            return render_template("bookings/edit.html", booking=booking)
        
        # Check hours of operation
        resource = booking.resource
        if resource.opening_time and resource.closing_time:
            start_time_only = start.time()
            end_time_only = end.time()
            
            # Check if booking starts and ends within operating hours
            if start_time_only < resource.opening_time or end_time_only > resource.closing_time:
                flash(f"This resource is only available from {resource.opening_time.strftime('%I:%M %p')} to {resource.closing_time.strftime('%I:%M %p')}. Your booking is outside these hours.", "danger")
                return render_template("bookings/edit.html", booking=booking)
        
        # Round times to 15-minute intervals (validate)
        start_minute = start.minute
        end_minute = end.minute
        if start_minute % 15 != 0 or end_minute % 15 != 0:
            flash("Booking times must be in 15-minute intervals (e.g., :00, :15, :30, :45)", "danger")
            return render_template("bookings/edit.html", booking=booking)
        
        # Check for conflicts (excluding current booking)
        conflict = (
            Booking.query.filter_by(resource_id=booking.resource_id, status="approved")
            .filter(Booking.id != booking.id)
            .filter(Booking.start_time < end, Booking.end_time > start)
            .first()
        )
        if conflict:
            flash("Time slot conflicts with existing booking", "danger")
            return render_template("bookings/edit.html", booking=booking)
        
        booking.start_time = start
        booking.end_time = end
        booking.recurrence_pattern = recurrence
        # Only set to pending if resource requires approval and booking was approved
        if booking.status == "approved" and booking.resource.booking_type == "restricted":
            # If editing an approved booking for a restricted resource, might need re-approval
            booking.status = "pending"
            flash("Booking updated and set to pending for re-approval", "info")
        # For open resources, keep status as approved (or if it was already pending, leave it pending)
        
        db.session.commit()
        flash("Booking updated", "success")
        return redirect(url_for("bookings.booking_detail", booking_id=booking_id))
    
    return render_template("bookings/edit.html", booking=booking)


@bp.route("/<int:booking_id>/approve", methods=["POST", "PUT"])
@login_required
def approve(booking_id: int):
    """Approve a booking (admin or resource owner only)"""
    booking = Booking.query.get_or_404(booking_id)
    resource = booking.resource
    
    # Only resource owner or admin can approve
    if booking.resource.owner_id != current_user.id and current_user.role != "admin":
        flash("Not authorized", "danger")
        return redirect(url_for("bookings.my_bookings"))
    
    # Only pending bookings can be approved
    if booking.status != "pending":
        flash("Only pending bookings can be approved", "warning")
        return redirect(request.referrer or url_for("bookings.my_bookings"))
    
    # Check for conflicts with approved bookings
    conflict = (
        Booking.query.filter_by(resource_id=resource.id, status="approved")
        .filter(Booking.id != booking.id)
        .filter(Booking.start_time < booking.end_time, Booking.end_time > booking.start_time)
        .first()
    )
    if conflict:
        flash("Cannot approve due to conflict with existing booking", "warning")
        return redirect(request.referrer or url_for("bookings.my_bookings"))
    
    booking.status = "approved"
    db.session.commit()
    
    # Log admin action if admin approved
    if current_user.role == "admin":
        from ..utils.admin_logging import log_admin_action
        log_admin_action(
            current_user.id,
            "approve_booking",
            "bookings",
            f"Approved booking {booking.id} for resource {resource.id}"
        )
    
    _send_notification(booking.user.email, "booking_approved", booking)
    _send_booking_message(booking.user_id, booking, "approved")
    
    flash("Booking approved", "success")
    return redirect(request.referrer or url_for("bookings.my_bookings"))


@bp.route("/<int:booking_id>/reject", methods=["POST"])
@login_required
def reject(booking_id: int):
    """Reject a pending booking (admin or resource owner only)"""
    booking = Booking.query.get_or_404(booking_id)
    resource = booking.resource
    
    # Only resource owner or admin can reject
    if booking.resource.owner_id != current_user.id and current_user.role != "admin":
        flash("Not authorized", "danger")
        return redirect(url_for("bookings.my_bookings"))
    
    # Only pending bookings can be rejected
    if booking.status != "pending":
        flash("Only pending bookings can be rejected", "warning")
        return redirect(request.referrer or url_for("bookings.my_bookings"))
    
    booking.status = "rejected"
    db.session.commit()
    
    # Log admin action if admin rejected
    if current_user.role == "admin":
        from ..utils.admin_logging import log_admin_action
        log_admin_action(
            current_user.id,
            "reject_booking",
            "bookings",
            f"Rejected booking {booking.id} for resource {resource.id}"
        )
    
    _send_notification(booking.user.email, "booking_cancelled", booking)
    _send_booking_message(booking.user_id, booking, "rejected")
    
    flash("Booking rejected", "info")
    return redirect(request.referrer or url_for("bookings.my_bookings"))


@bp.route("/<int:booking_id>/cancel", methods=["POST"])
@login_required
def cancel(booking_id: int):
    """Cancel a booking"""
    booking = Booking.query.get_or_404(booking_id)
    resource = booking.resource
    now = datetime.utcnow()
    
    # Only owner, admin, or booking user can cancel
    if booking.user_id != current_user.id and booking.resource.owner_id != current_user.id and current_user.role != "admin":
        flash("Not authorized", "danger")
        return redirect(url_for("bookings.my_bookings"))
    
    # If user is cancelling their own booking, only allow if booking hasn't started yet
    if booking.user_id == current_user.id and booking.start_time <= now:
        flash("You can only cancel bookings that haven't started yet.", "warning")
        return redirect(url_for("bookings.my_bookings"))
    
    # Preserve booking times and original status before cancelling (for waitlist promotion)
    cancelled_start_time = booking.start_time
    cancelled_end_time = booking.end_time
    original_status = booking.status  # Save original status before cancelling
    
    booking.status = "cancelled"
    db.session.commit()
    
    # Log admin action if admin cancelled
    if current_user.role == "admin":
        from ..utils.admin_logging import log_admin_action
        log_admin_action(
            current_user.id,
            "cancel_booking",
            "bookings",
            f"Cancelled booking {booking.id} for resource {resource.id}"
        )
    
    _send_notification(booking.user.email, "booking_cancelled", booking)
    
    # Check waitlist and promote next user if applicable
    # Only promote if the cancelled booking was approved or pending (slot was actually reserved)
    from ..data_access.waitlist import next_waitlist_candidate, remove_waitlist_entry
    from ..models.models import User as UserModel
    
    if original_status in ["approved", "pending"]:
        waitlist_entry = next_waitlist_candidate(resource.id, cancelled_start_time, cancelled_end_time)
        if waitlist_entry:
            # Determine booking status based on resource booking type
            if resource.booking_type == "open":
                booking_status = "approved"
                notification_type = "booking_approved"
            else:
                booking_status = "pending"
                notification_type = "booking_requested"
            
            # Create booking for waitlisted user using the cancelled booking's time slot
            new_booking = Booking(
                resource_id=resource.id,
                user_id=waitlist_entry.user_id,
                start_time=cancelled_start_time,
                end_time=cancelled_end_time,
                status=booking_status
            )
            db.session.add(new_booking)
            db.session.flush()  # Flush to get the booking ID
            
            # Remove waitlist entry
            remove_waitlist_entry(waitlist_entry)
            db.session.commit()
            
            # Get the user for notification
            waitlisted_user = UserModel.query.get(waitlist_entry.user_id)
            if waitlisted_user:
                _send_notification(
                    waitlisted_user.email,
                    notification_type,
                    new_booking
                )
            
            flash(f"Booking cancelled. First person on waitlist has been {'approved' if booking_status == 'approved' else 'notified'} for this time slot.", "info")
        else:
            flash("Booking cancelled", "info")
    else:
        flash("Booking cancelled", "info")
    
    return redirect(request.referrer or url_for("bookings.my_bookings"))


@bp.route("/waitlist/<int:waitlist_id>/cancel", methods=["POST"])
@login_required
def cancel_waitlist(waitlist_id: int):
    """Cancel/remove a waitlist entry"""
    from ..models.models import Waitlist
    
    waitlist_entry = Waitlist.query.get_or_404(waitlist_id)
    
    # Only the user who created the waitlist entry can cancel it
    if waitlist_entry.user_id != current_user.id:
        flash("Not authorized to cancel this waitlist entry", "danger")
        return redirect(url_for("bookings.my_bookings"))
    
    # Get resource info for flash message
    resource = waitlist_entry.resource
    
    # Remove the waitlist entry
    remove_waitlist_entry(waitlist_entry)
    
    flash(f"You have been removed from the waitlist for {resource.title}.", "info")
    return redirect(url_for("bookings.my_bookings"))
