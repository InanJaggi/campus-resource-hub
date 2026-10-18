from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required
import re
from ..extensions import db, bcrypt
from ..models.models import User

bp = Blueprint("auth", __name__, url_prefix="/auth")


def validate_password(password: str):
    """
    Validate password strength.
    Requirements:
    - At least 8 characters
    - At least one uppercase letter
    - At least one lowercase letter
    - At least one number
    - Special characters are highly recommended (but not required)
    
    Returns: (is_valid, error_message)
    """
    if len(password) < 8:
        return False, "Password must be at least 8 characters long."
    
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter."
    
    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter."
    
    if not re.search(r'\d', password):
        return False, "Password must contain at least one number."
    
    # Special characters are recommended but not required
    has_special = bool(re.search(r'[!@#$%^&*(),.?":{}|<>]', password))
    
    return True, "" if has_special else "Consider adding a special character for stronger security."


@bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        user = User.query.filter_by(email=email).first()
        if user and bcrypt.check_password_hash(user.password_hash, password):
            login_user(user)
            flash("Logged in.", "success")
            return redirect(url_for("index"))
        flash("Invalid credentials", "danger")
    return render_template("auth/login.html")


@bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        name = request.form.get("name", "").strip()
        role = request.form.get("role", "student")
        password = request.form.get("password", "")
        
        if not email or not password or not name:
            flash("All fields required", "danger")
            return render_template("auth/register.html")
        
        # Validate password strength
        is_valid, error_msg = validate_password(password)
        if not is_valid:
            flash(error_msg, "danger")
            return render_template("auth/register.html")
        elif error_msg:  # Warning message (e.g., missing special character)
            flash(error_msg, "warning")
        
        if User.query.filter_by(email=email).first():
            flash("Email already registered", "warning")
            return render_template("auth/register.html")
        
        hashed = bcrypt.generate_password_hash(password).decode()
        user = User(email=email, name=name, role=role, password_hash=hashed)
        db.session.add(user)
        db.session.commit()
        flash("Registration successful. Please log in.", "success")
        return redirect(url_for("auth.login"))
    return render_template("auth/register.html")


@bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Logged out.", "info")
    return redirect(url_for("index"))


