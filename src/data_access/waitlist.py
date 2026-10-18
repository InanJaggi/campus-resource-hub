# AI Contribution: Cursor AI suggested the waitlist system architecture and auto-promotion logic.
# The implementation was reviewed and enhanced with proper conflict detection and notification handling.

from datetime import datetime
from typing import Optional, List
from ..extensions import db
from ..models.models import Waitlist


def join_waitlist(resource_id: int, user_id: int, desired_start: Optional[datetime], desired_end: Optional[datetime]) -> Waitlist:
    entry = Waitlist(resource_id=resource_id, user_id=user_id, desired_start=desired_start, desired_end=desired_end)
    db.session.add(entry)
    db.session.commit()
    return entry


def next_waitlist_candidate(resource_id: int, start_time: Optional[datetime] = None, end_time: Optional[datetime] = None) -> Optional[Waitlist]:
    """Get next waitlist candidate for a resource, optionally matching time slot"""
    query = Waitlist.query.filter_by(resource_id=resource_id)
    
    # If time slot is provided, try to match it
    if start_time and end_time:
        # Normalize times to minutes (remove seconds and microseconds for comparison)
        start_time_normalized = start_time.replace(second=0, microsecond=0)
        end_time_normalized = end_time.replace(second=0, microsecond=0)
        
        # Get all waitlist entries for this resource
        all_entries = query.order_by(Waitlist.created_at.asc()).all()
        
        # First try to find exact match (within 1 minute tolerance)
        for entry in all_entries:
            if entry.desired_start and entry.desired_end:
                entry_start = entry.desired_start.replace(second=0, microsecond=0)
                entry_end = entry.desired_end.replace(second=0, microsecond=0)
                
                # Check if times match (within 1 minute)
                if (abs((entry_start - start_time_normalized).total_seconds()) < 60 and
                    abs((entry_end - end_time_normalized).total_seconds()) < 60):
                    return entry
        
        # If no exact match, try overlapping times
        for entry in all_entries:
            if entry.desired_start and entry.desired_end:
                # Check if times overlap
                if (entry.desired_start <= end_time and entry.desired_end >= start_time):
                    return entry
        
        # If no overlapping match but we have entries, return the first one (they'll get the slot)
        if all_entries:
            return all_entries[0]
    
    # Otherwise, just get the first (oldest) entry
    return query.order_by(Waitlist.created_at.asc()).first()


def remove_waitlist_entry(entry: Waitlist) -> None:
    db.session.delete(entry)
    db.session.commit()


def get_user_waitlist(user_id: int) -> List[Waitlist]:
    """Get all waitlist entries for a user"""
    return Waitlist.query.filter_by(user_id=user_id).order_by(Waitlist.created_at.desc()).all()


