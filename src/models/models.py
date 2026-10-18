from datetime import datetime
from typing import Optional
from ..extensions import db, login_manager
from flask_login import UserMixin


class BaseModel(db.Model):
    __abstract__ = True
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


class User(BaseModel, UserMixin):
    __tablename__ = "users"
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    name = db.Column(db.String(120), nullable=False)
    role = db.Column(db.String(20), default="student", nullable=False)  # student, staff, admin
    password_hash = db.Column(db.String(255), nullable=False)
    profile_image = db.Column(db.String(255), nullable=True)  # path to image file
    department = db.Column(db.String(100), nullable=True)

    resources = db.relationship("Resource", backref="owner", lazy=True)
    bookings = db.relationship("Booking", backref="user", lazy=True)


@login_manager.user_loader
def load_user(user_id: str) -> Optional[User]:
    try:
        return User.query.get(int(user_id))
    except Exception:
        return None


class Resource(BaseModel):
    __tablename__ = "resources"
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, default="")
    category = db.Column(db.String(100), default="general", index=True)
    location = db.Column(db.String(200), default="")
    capacity = db.Column(db.Integer, default=1)
    status = db.Column(db.String(20), default="published")  # draft, published, archived
    owner_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    avg_rating = db.Column(db.Float, default=0)
    images = db.Column(db.Text, nullable=True)  # comma-separated paths or JSON array
    availability_rules = db.Column(db.Text, nullable=True)  # JSON blob describing recurring availability
    opening_time = db.Column(db.Time, nullable=True)  # Hours of operation start (e.g., 07:00)
    closing_time = db.Column(db.Time, nullable=True)  # Hours of operation end (e.g., 23:59)
    booking_type = db.Column(db.String(20), default="restricted")  # open (no approval needed) or restricted (requires approval)
    
    # Category-specific fields (nullable, used based on category)
    model = db.Column(db.String(200), nullable=True)  # For lab/AV equipment
    equipment_included = db.Column(db.Text, nullable=True)  # What comes with it
    specifications = db.Column(db.Text, nullable=True)  # Technical specs
    connectivity = db.Column(db.String(200), nullable=True)  # For AV equipment (HDMI, USB, etc.)
    amenities = db.Column(db.Text, nullable=True)  # For study rooms/event spaces
    seating_type = db.Column(db.String(100), nullable=True)  # For study rooms
    has_whiteboard = db.Column(db.Boolean, default=False)  # For study rooms
    has_projector = db.Column(db.Boolean, default=False)  # For study rooms/event spaces
    setup_options = db.Column(db.Text, nullable=True)  # For event spaces
    catering_allowed = db.Column(db.Boolean, default=False)  # For event spaces
    subject = db.Column(db.String(100), nullable=True)  # For tutoring
    level = db.Column(db.String(50), nullable=True)  # For tutoring (beginner, intermediate, advanced)
    duration = db.Column(db.String(50), nullable=True)  # For tutoring (30min, 1hr, etc.)
    online_available = db.Column(db.Boolean, default=False)  # For tutoring

    bookings = db.relationship("Booking", backref="resource", lazy=True)
    reviews = db.relationship("Review", backref="resource", lazy=True)


class Booking(BaseModel):
    __tablename__ = "bookings"
    resource_id = db.Column(db.Integer, db.ForeignKey("resources.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False, index=True)
    end_time = db.Column(db.DateTime, nullable=False, index=True)
    status = db.Column(db.String(20), default="pending")  # pending, approved, rejected, cancelled, completed
    recurrence_pattern = db.Column(db.String(50), nullable=True)  # e.g., "daily", "weekly", "monthly"


class MessageThread(BaseModel):
    __tablename__ = "message_threads"
    user_a_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    user_b_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    messages = db.relationship("Message", backref="thread", lazy=True)


class Message(BaseModel):
    __tablename__ = "messages"
    thread_id = db.Column(db.Integer, db.ForeignKey("message_threads.id"), nullable=False, index=True)
    sender_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)  # for direct messages
    body = db.Column(db.Text, nullable=False)
    is_read = db.Column(db.Boolean, default=False, nullable=False)  # Track if message is read


class Review(BaseModel):
    __tablename__ = "reviews"
    resource_id = db.Column(db.Integer, db.ForeignKey("resources.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    rating = db.Column(db.Integer, nullable=False)  # 1-5
    comment = db.Column(db.Text, default="")
    
    user = db.relationship("User", backref="reviews", lazy=True)


class AdminLog(BaseModel):
    __tablename__ = "admin_logs"
    action = db.Column(db.String(255), nullable=False)
    actor_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    target_table = db.Column(db.String(50), nullable=True)  # e.g., "users", "resources", "bookings"
    details = db.Column(db.Text, nullable=True)  # JSON or text details
    
    actor = db.relationship("User", foreign_keys=[actor_id], backref="admin_actions")


class Waitlist(BaseModel):
    __tablename__ = "waitlist"
    resource_id = db.Column(db.Integer, db.ForeignKey("resources.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    desired_start = db.Column(db.DateTime, nullable=True)
    desired_end = db.Column(db.DateTime, nullable=True)
    
    resource = db.relationship("Resource", backref="waitlist_entries", lazy=True)
    user = db.relationship("User", backref="waitlist_entries", lazy=True)


