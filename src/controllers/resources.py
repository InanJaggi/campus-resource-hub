from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from ..extensions import db
from ..models.models import Resource

bp = Blueprint("resources", __name__, url_prefix="/resources")


@bp.route("/")
def list_resources():
    try:
        from datetime import datetime
        from sqlalchemy import func, and_, or_
        from ..models.models import Booking
        
        # Get all filter parameters
        q = request.args.get("q", "").strip()
        category = request.args.get("category")
        location_filter = request.args.get("location", "").strip()
        min_capacity = request.args.get("min_capacity")
        min_rating = request.args.get("min_rating")
        available_date = request.args.get("available_date")
        available_time = request.args.get("available_time")
        sort_by = request.args.get("sort", "recent")  # recent, most_booked, top_rated
        
        query = Resource.query.filter_by(status="published")
        
        # Text search (title, description, location)
        if q:
            like = f"%{q}%"
            query = query.filter(
                (Resource.title.ilike(like)) | 
                (Resource.description.ilike(like)) | 
                (Resource.location.ilike(like))
            )
        
        # Category filter
        if category:
            query = query.filter_by(category=category)
        
        # Location filter
        if location_filter:
            query = query.filter(Resource.location.ilike(f"%{location_filter}%"))
        
        # Minimum capacity filter
        if min_capacity:
            try:
                min_cap = int(min_capacity)
                query = query.filter(Resource.capacity >= min_cap)
            except ValueError:
                pass
        
        # Minimum rating filter
        if min_rating:
            try:
                min_rat = float(min_rating)
                query = query.filter(Resource.avg_rating >= min_rat)
            except ValueError:
                pass
        
        # Time-based availability filter
        if available_date and available_time:
            try:
                # Parse date and time
                date_str = f"{available_date} {available_time}"
                target_datetime = datetime.strptime(date_str, "%Y-%m-%d %H:%M")
                
                # Find resources that are NOT booked at this time
                # Get all resource IDs that have conflicting bookings (pending or approved)
                conflicting_resource_ids = db.session.query(Booking.resource_id).filter(
                    Booking.status.in_(["pending", "approved"]),
                    Booking.start_time <= target_datetime,
                    Booking.end_time > target_datetime
                ).distinct().all()
                
                # Extract resource IDs from the result
                conflicting_ids = [row[0] for row in conflicting_resource_ids]
                
                # Filter out resources with conflicts (show only available ones)
                if conflicting_ids:
                    query = query.filter(~Resource.id.in_(conflicting_ids))
                # If no conflicts, all resources are available (no additional filter needed)
            except (ValueError, Exception) as e:
                # If date/time parsing fails, ignore the filter
                pass
        
        # Apply sorting (must be done after all filters)
        if sort_by == "most_booked":
            # For "most booked", we need to join with Booking and count
            # Use a subquery approach to avoid conflicts with time filtering
            booking_counts = db.session.query(
                Booking.resource_id,
                func.count(Booking.id).label('booking_count')
            ).filter(
                Booking.status.in_(["pending", "approved", "completed"])
            ).group_by(Booking.resource_id).subquery()
            
            # Left join with booking counts
            query = query.outerjoin(
                booking_counts, Resource.id == booking_counts.c.resource_id
            ).order_by(
                func.coalesce(booking_counts.c.booking_count, 0).desc(),
                Resource.created_at.desc()
            )
        elif sort_by == "top_rated":
            query = query.order_by(Resource.avg_rating.desc(), Resource.created_at.desc())
        else:  # recent (default)
            query = query.order_by(Resource.created_at.desc())
        
        resources = query.all()
        
        # Get unique categories for filter dropdown
        categories = db.session.query(Resource.category).filter_by(status="published").distinct().all()
        categories = [cat[0] for cat in categories]
        
        # Get unique locations for filter dropdown
        locations = db.session.query(Resource.location).filter(
            Resource.status == "published",
            Resource.location != "",
            Resource.location.isnot(None)
        ).distinct().all()
        locations = [loc[0] for loc in locations if loc[0]]
        
        return render_template("resources/list.html", 
            resources=resources, 
            q=q, 
            category=category,
            location_filter=location_filter,
            min_capacity=min_capacity,
            min_rating=min_rating,
            available_date=available_date,
            available_time=available_time,
            sort_by=sort_by,
            categories=categories,
            locations=locations
        )
    except Exception as e:
        flash(f"An error occurred while searching: {str(e)}", "danger")
        resources = Resource.query.filter_by(status="published").order_by(Resource.created_at.desc()).all()
        categories = []
        locations = []
        return render_template("resources/list.html", 
            resources=resources, 
            q="", 
            category="",
            location_filter="",
            min_capacity="",
            min_rating="",
            available_date="",
            available_time="",
            sort_by="recent",
            categories=categories,
            locations=locations
        )


@bp.route("/new", methods=["GET", "POST"])
@login_required
def new_resource():
    # Only staff and admin can create resources
    if current_user.role not in ["staff", "admin"]:
        flash("Only staff and administrators can create resources.", "warning")
        return redirect(url_for("resources.list_resources"))
    
    if request.method == "POST":
        title = request.form.get("title", "").strip()
        description = request.form.get("description", "").strip()
        category = request.form.get("category", "general").strip()
        location = request.form.get("location", "").strip()
        capacity = int(request.form.get("capacity", 1))
        status = request.form.get("status", "published")
        booking_type = request.form.get("booking_type", "restricted").strip()
        if not title:
            flash("Title required", "danger")
            return render_template("resources/form.html")
        
        # Get category-specific fields
        model = request.form.get("model", "").strip() or None
        equipment_included = request.form.get("equipment_included", "").strip() or None
        specifications = request.form.get("specifications", "").strip() or None
        connectivity = request.form.get("connectivity", "").strip() or None
        amenities = request.form.get("amenities", "").strip() or None
        seating_type = request.form.get("seating_type", "").strip() or None
        has_whiteboard = request.form.get("has_whiteboard") == "on"
        has_projector = request.form.get("has_projector") == "on"
        setup_options = request.form.get("setup_options", "").strip() or None
        catering_allowed = request.form.get("catering_allowed") == "on"
        subject = request.form.get("subject", "").strip() or None
        level = request.form.get("level", "").strip() or None
        duration = request.form.get("duration", "").strip() or None
        online_available = request.form.get("online_available") == "on"
        
        # Parse hours of operation
        opening_time_str = request.form.get("opening_time", "").strip() or None
        closing_time_str = request.form.get("closing_time", "").strip() or None
        opening_time = None
        closing_time = None
        if opening_time_str:
            try:
                from datetime import datetime
                opening_time = datetime.strptime(opening_time_str, "%H:%M").time()
            except ValueError:
                pass
        if closing_time_str:
            try:
                from datetime import datetime
                closing_time = datetime.strptime(closing_time_str, "%H:%M").time()
            except ValueError:
                pass
        
        # Create resource first to get ID for image naming
        res = Resource(
            title=title, description=description, category=category, location=location,
            capacity=capacity, owner_id=current_user.id, status=status, booking_type=booking_type,
            model=model, equipment_included=equipment_included, specifications=specifications,
            connectivity=connectivity, amenities=amenities, seating_type=seating_type,
            has_whiteboard=has_whiteboard, has_projector=has_projector,
            setup_options=setup_options, catering_allowed=catering_allowed,
            subject=subject, level=level, duration=duration, online_available=online_available,
            opening_time=opening_time, closing_time=closing_time
        )
        db.session.add(res)
        db.session.commit()  # Commit to get the resource ID
        
        # Handle image upload
        if 'image' in request.files:
            file = request.files['image']
            if file and file.filename:
                from ..utils.file_upload import save_resource_image
                image_path = save_resource_image(file, res.id)
                if image_path:
                    res.images = image_path
                    db.session.commit()
                else:
                    flash("Invalid image file. Allowed formats: PNG, JPG, JPEG, GIF, WEBP (max 10MB)", "warning")
        
        # Log admin action if admin created
        if current_user.role == "admin":
            from ..utils.admin_logging import log_admin_action
            log_admin_action(
                current_user.id,
                "create_resource",
                "resources",
                f"Created resource {res.id}: {title}"
            )
        
        flash("Resource created", "success")
        return redirect(url_for("resources.list_resources"))
    return render_template("resources/form.html")


@bp.route("/<int:resource_id>")
def detail(resource_id: int):
    resource = Resource.query.get_or_404(resource_id)
    return render_template("resources/detail.html", resource=resource)


@bp.route("/<int:resource_id>/edit", methods=["GET", "POST"])
@login_required
def edit(resource_id: int):
    resource = Resource.query.get_or_404(resource_id)
    if resource.owner_id != current_user.id and current_user.role != "admin":
        flash("Not authorized", "danger")
        return redirect(url_for("resources.detail", resource_id=resource.id))
    if request.method == "POST":
        for field in ["title", "description", "category", "location", "status", "booking_type"]:
            setattr(resource, field, request.form.get(field, getattr(resource, field)))
        resource.capacity = int(request.form.get("capacity", resource.capacity))
        
        # Update category-specific fields
        resource.model = request.form.get("model", "").strip() or None
        resource.equipment_included = request.form.get("equipment_included", "").strip() or None
        resource.specifications = request.form.get("specifications", "").strip() or None
        resource.connectivity = request.form.get("connectivity", "").strip() or None
        resource.amenities = request.form.get("amenities", "").strip() or None
        resource.seating_type = request.form.get("seating_type", "").strip() or None
        resource.has_whiteboard = request.form.get("has_whiteboard") == "on"
        resource.has_projector = request.form.get("has_projector") == "on"
        resource.setup_options = request.form.get("setup_options", "").strip() or None
        resource.catering_allowed = request.form.get("catering_allowed") == "on"
        resource.subject = request.form.get("subject", "").strip() or None
        resource.level = request.form.get("level", "").strip() or None
        resource.duration = request.form.get("duration", "").strip() or None
        resource.online_available = request.form.get("online_available") == "on"
        
        # Parse hours of operation
        opening_time_str = request.form.get("opening_time", "").strip() or None
        closing_time_str = request.form.get("closing_time", "").strip() or None
        if opening_time_str:
            try:
                from datetime import datetime
                resource.opening_time = datetime.strptime(opening_time_str, "%H:%M").time()
            except ValueError:
                resource.opening_time = None
        else:
            resource.opening_time = None
        if closing_time_str:
            try:
                from datetime import datetime
                resource.closing_time = datetime.strptime(closing_time_str, "%H:%M").time()
            except ValueError:
                resource.closing_time = None
        else:
            resource.closing_time = None
        
        # Handle image upload (replace existing if new image uploaded)
        if 'image' in request.files:
            file = request.files['image']
            if file and file.filename:
                from ..utils.file_upload import save_resource_image, delete_resource_image
                # Delete old image if exists
                if resource.images:
                    delete_resource_image(resource.images)
                # Save new image
                image_path = save_resource_image(file, resource.id)
                if image_path:
                    resource.images = image_path
                else:
                    flash("Invalid image file. Allowed formats: PNG, JPG, JPEG, GIF, WEBP (max 10MB)", "warning")
        
        db.session.commit()
        
        # Log admin action if admin edited
        if current_user.role == "admin":
            from ..utils.admin_logging import log_admin_action
            log_admin_action(
                current_user.id,
                "edit_resource",
                "resources",
                f"Edited resource {resource.id}: {resource.title}"
            )
        
        flash("Resource updated", "success")
        return redirect(url_for("resources.detail", resource_id=resource.id))
    return render_template("resources/form.html", resource=resource)


@bp.route("/<int:resource_id>", methods=["DELETE"])
@login_required
def delete(resource_id: int):
    """DELETE /resources/<id> - delete resource (API endpoint)"""
    resource = Resource.query.get_or_404(resource_id)
    if resource.owner_id != current_user.id and current_user.role != "admin":
        from flask import jsonify
        return jsonify({"error": "Not authorized"}), 403
    
    resource_title = resource.title
    db.session.delete(resource)
    db.session.commit()
    
    # Log admin action if admin deleted
    if current_user.role == "admin":
        from ..utils.admin_logging import log_admin_action
        log_admin_action(
            current_user.id,
            "delete_resource",
            "resources",
            f"Deleted resource {resource_id}: {resource_title}"
        )
    
    from flask import jsonify
    return jsonify({"message": "Resource deleted"}), 200


@bp.route("/<int:resource_id>/activate", methods=["POST"])
@login_required
def activate(resource_id: int):
    """Activate a draft or archived resource (make it published)"""
    resource = Resource.query.get_or_404(resource_id)
    if resource.owner_id != current_user.id and current_user.role != "admin":
        flash("Not authorized", "danger")
        return redirect(request.referrer or url_for("resources.list_resources"))
    
    if resource.status not in ["draft", "archived"]:
        flash("Resource is already published", "info")
        return redirect(request.referrer or url_for("resources.list_resources"))
    
    resource.status = "published"
    db.session.commit()
    
    # Log admin action if admin activated
    if current_user.role == "admin":
        from ..utils.admin_logging import log_admin_action
        log_admin_action(
            current_user.id,
            "activate_resource",
            "resources",
            f"Activated resource {resource_id}: {resource.title}"
        )
    
    flash("Resource activated and now visible to all users", "success")
    return redirect(request.referrer or url_for("resources.detail", resource_id=resource_id))


@bp.route("/my-resources")
@login_required
def my_resources():
    """List resources owned by the current user"""
    # Only staff and admin can own resources
    if current_user.role not in ["staff", "admin"]:
        flash("Only staff and administrators can own resources.", "warning")
        return redirect(url_for("resources.list_resources"))
    
    # Get all resources owned by current user
    owned_resources = Resource.query.filter_by(owner_id=current_user.id).order_by(Resource.created_at.desc()).all()
    
    return render_template("resources/my_resources.html", resources=owned_resources)


