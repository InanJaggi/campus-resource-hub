from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from ..extensions import db
from ..models.models import MessageThread, Message, User

bp = Blueprint("messages", __name__, url_prefix="/messages")


def get_unread_count(user_id: int) -> int:
    """Get count of unread messages for a user"""
    return Message.query.join(MessageThread).filter(
        ((MessageThread.user_a_id == user_id) | (MessageThread.user_b_id == user_id)),
        Message.receiver_id == user_id,
        Message.is_read == False
    ).count()


@bp.route("/")
@login_required
def list_threads():
    threads = MessageThread.query.filter(
        (MessageThread.user_a_id == current_user.id) | (MessageThread.user_b_id == current_user.id)
    ).order_by(MessageThread.updated_at.desc()).all()
    
    # Get unread counts and other user info for each thread
    thread_data = []
    for thread in threads:
        other_user = User.query.get(thread.user_b_id if thread.user_a_id == current_user.id else thread.user_a_id)
        unread_count = Message.query.filter_by(
            thread_id=thread.id,
            receiver_id=current_user.id,
            is_read=False
        ).count()
        
        # Get last message
        last_message = Message.query.filter_by(thread_id=thread.id).order_by(Message.created_at.desc()).first()
        
        thread_data.append({
            'thread': thread,
            'other_user': other_user,
            'unread_count': unread_count,
            'last_message': last_message
        })
    
    return render_template("messages/threads.html", thread_data=thread_data)


@bp.route("/thread/<int:thread_id>", methods=["GET", "POST"])
@login_required
def thread(thread_id: int):
    thr = MessageThread.query.get_or_404(thread_id)
    if current_user.id not in {thr.user_a_id, thr.user_b_id}:
        flash("Not authorized", "danger")
        return redirect(url_for("messages.list_threads"))
    
    # Get the other user in the conversation
    other_user_id = thr.user_b_id if thr.user_a_id == current_user.id else thr.user_a_id
    other_user = User.query.get(other_user_id)
    
    if request.method == "POST":
        body = request.form.get("body", "").strip()
        if body:
            msg = Message(thread_id=thr.id, sender_id=current_user.id, receiver_id=other_user_id, body=body)
            db.session.add(msg)
            db.session.commit()
            return redirect(url_for("messages.thread", thread_id=thread_id))
    
    # Mark all messages in this thread as read (for current user as receiver)
    Message.query.filter_by(
        thread_id=thr.id,
        receiver_id=current_user.id,
        is_read=False
    ).update({"is_read": True})
    db.session.commit()
    
    messages = Message.query.filter_by(thread_id=thr.id).order_by(Message.created_at.asc()).all()
    return render_template("messages/thread.html", thread=thr, messages=messages, other_user=other_user)


@bp.route("", methods=["POST"])
@login_required
def send_message():
    """POST /messages - send message (API endpoint)"""
    data = request.get_json() or {}
    thread_id = data.get("thread_id")
    receiver_id = data.get("receiver_id")
    body = data.get("body", "").strip()
    
    if not body:
        return jsonify({"error": "Message body required"}), 400
    
    if thread_id:
        thread = MessageThread.query.get(thread_id)
        if not thread or current_user.id not in {thread.user_a_id, thread.user_b_id}:
            return jsonify({"error": "Not authorized"}), 403
        other_user_id = thread.user_b_id if thread.user_a_id == current_user.id else thread.user_a_id
        msg = Message(thread_id=thread_id, sender_id=current_user.id, receiver_id=other_user_id, body=body)
    elif receiver_id:
        # Create or find thread
        thread = MessageThread.query.filter(
            ((MessageThread.user_a_id == current_user.id) & (MessageThread.user_b_id == receiver_id)) |
            ((MessageThread.user_a_id == receiver_id) & (MessageThread.user_b_id == current_user.id))
        ).first()
        if not thread:
            thread = MessageThread(user_a_id=current_user.id, user_b_id=receiver_id)
            db.session.add(thread)
            db.session.flush()
        msg = Message(thread_id=thread.id, sender_id=current_user.id, receiver_id=receiver_id, body=body)
    else:
        return jsonify({"error": "thread_id or receiver_id required"}), 400
    
    db.session.add(msg)
    db.session.commit()
    return jsonify({"message": "Message sent", "id": msg.id}), 201


@bp.route("/new/<int:receiver_id>", methods=["GET", "POST"])
@login_required
def new_message(receiver_id: int):
    """Start a new conversation with a user"""
    receiver = User.query.get_or_404(receiver_id)
    
    # Find or create thread
    thread = MessageThread.query.filter(
        ((MessageThread.user_a_id == current_user.id) & (MessageThread.user_b_id == receiver_id)) |
        ((MessageThread.user_a_id == receiver_id) & (MessageThread.user_b_id == current_user.id))
    ).first()
    
    if not thread:
        thread = MessageThread(user_a_id=current_user.id, user_b_id=receiver_id)
        db.session.add(thread)
        db.session.commit()
    
    return redirect(url_for("messages.thread", thread_id=thread.id))


