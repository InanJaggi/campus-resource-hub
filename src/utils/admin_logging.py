"""Utility for logging admin actions"""
from ..extensions import db
from ..models.models import AdminLog


def log_admin_action(actor_id: int, action: str, target_table: str = None, details: str = None):
    """Helper to log admin actions"""
    log = AdminLog(
        action=action,
        actor_id=actor_id,
        target_table=target_table,
        details=details
    )
    db.session.add(log)
    db.session.commit()

