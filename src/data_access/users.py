# AI Contribution: Cursor AI suggested the initial user data access layer structure.
# The user management functions were reviewed and enhanced with proper error handling.

from typing import Optional
from ..extensions import db
from ..models.models import User


def create_user(email: str, name: str, password_hash: str, role: str = "student") -> User:
    user = User(email=email, name=name, password_hash=password_hash, role=role)
    db.session.add(user)
    db.session.commit()
    return user


def get_user_by_email(email: str) -> Optional[User]:
    return User.query.filter_by(email=email).first()


def promote_to_staff(user_id: int) -> Optional[User]:
    user = User.query.get(user_id)
    if not user:
        return None
    user.role = "staff"
    db.session.commit()
    return user


