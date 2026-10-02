from flask import current_app

from backend.models import db, User, Notification


def _emit_to_user(user_id, payload):
    """Push a notification over SocketIO to every live tab of one user."""
    try:
        socketio = current_app.extensions.get('socketio')
        if socketio:
            socketio.emit('notification', payload, room=f'user_{user_id}')
    except Exception:
        pass  # SocketIO not initialised (tests, CLI, workers)


def create_notification(user_id, ntype, title, message=None, link=None):
    """Persist a notification for one user and push it live.

    Returns the Notification, or None if the row could not be stored.
    """
    notification = Notification(
        user_id=user_id,
        ntype=ntype,
        title=title,
        message=message,
        link=link
    )
    db.session.add(notification)
    try:
        db.session.flush()
    except Exception:
        db.session.rollback()
        return None
    _emit_to_user(user_id, notification.to_dict())
    return notification


def notify_admins(ntype, title, message=None, link=None):
    """Notify every admin account (used for the payment verification queue)."""
    admins = User.query.filter_by(role='admin', is_blocked=False).all()
    created = []
    for admin in admins:
        notification = create_notification(admin.id, ntype, title, message, link)
        if notification:
            created.append(notification)
    try:
        socketio = current_app.extensions.get('socketio')
        if socketio:
            socketio.emit('notification_admin', {
                'type': ntype,
                'title': title,
                'message': message,
                'link': link
            }, room='admins')
    except Exception:
        pass
    return created


def mark_all_read(user_id):
    """Clear the unread badge for a user. Returns the number updated."""
    updated = Notification.query.filter_by(user_id=user_id, is_read=False).update(
        {'is_read': True}, synchronize_session=False
    )
    db.session.commit()
    return updated


def prune(user_id, keep=50):
    """Drop a user's oldest read notifications so the table stays bounded."""
    read_ids = db.session.query(Notification.id).filter_by(
        user_id=user_id, is_read=True
    ).order_by(Notification.created_at.desc()).offset(keep).limit(100).all()
    if read_ids:
        Notification.query.filter(Notification.id.in_([i for (i,) in read_ids])).delete(
            synchronize_session=False
        )
        db.session.commit()