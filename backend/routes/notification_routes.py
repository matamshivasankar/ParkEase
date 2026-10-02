from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required

from backend.models import db, Notification, User
from backend.middleware.auth_middleware import admin_required, get_current_user_id
from backend.utils.notifier import mark_all_read, prune

notification_bp = Blueprint('notifications', __name__, url_prefix='/api/notifications')


def _scoped_query(user_id):
    return Notification.query.filter_by(user_id=user_id)


@notification_bp.route('', methods=['GET'])
@jwt_required()
def list_notifications():
    """Notifications for the signed-in user, newest first."""
    current_user_id = get_current_user_id()
    if not User.query.get(current_user_id):
        return jsonify({'error': 'User not found'}), 404

    try:
        limit = min(max(int(request.args.get('limit', 30)), 1), 100)
    except (TypeError, ValueError):
        limit = 30
    unread_only = request.args.get('unread_only') == 'true'

    query = _scoped_query(current_user_id)
    if unread_only:
        query = query.filter_by(is_read=False)
    query = query.order_by(Notification.created_at.desc())

    total = query.count()
    items = query.limit(limit).all()
    unread = _scoped_query(current_user_id).filter_by(is_read=False).count()

    return jsonify({
        'notifications': [n.to_dict() for n in items],
        'unread_count': unread,
        'total': total
    }), 200


@notification_bp.route('/unread-count', methods=['GET'])
@jwt_required()
def unread_count():
    """Lightweight poll for the navbar badge."""
    current_user_id = get_current_user_id()
    unread = _scoped_query(current_user_id).filter_by(is_read=False).count()
    return jsonify({'unread_count': unread}), 200


@notification_bp.route('/<int:notification_id>/read', methods=['PUT'])
@jwt_required()
def mark_read(notification_id):
    current_user_id = get_current_user_id()
    notification = Notification.query.get(notification_id)
    if not notification:
        return jsonify({'error': 'Notification not found'}), 404
    if notification.user_id != current_user_id:
        return jsonify({'error': 'Unauthorized'}), 403

    notification.is_read = True
    db.session.commit()

    return jsonify({
        'message': 'Marked as read',
        'notification': notification.to_dict(),
        'unread_count': _scoped_query(current_user_id).filter_by(is_read=False).count()
    }), 200


@notification_bp.route('/read-all', methods=['PUT'])
@jwt_required()
def read_all():
    current_user_id = get_current_user_id()
    updated = mark_all_read(current_user_id)
    prune(current_user_id)
    return jsonify({
        'message': 'All notifications marked as read',
        'updated': updated,
        'unread_count': 0
    }), 200


@notification_bp.route('/<int:notification_id>', methods=['DELETE'])
@jwt_required()
def delete_notification(notification_id):
    current_user_id = get_current_user_id()
    notification = Notification.query.get(notification_id)
    if not notification:
        return jsonify({'error': 'Notification not found'}), 404
    if notification.user_id != current_user_id:
        return jsonify({'error': 'Unauthorized'}), 403

    db.session.delete(notification)
    db.session.commit()
    return jsonify({'message': 'Notification deleted'}), 200


@notification_bp.route('/read-all', methods=['DELETE'])
@jwt_required()
def delete_all_read():
    """Clear the signed-in user's notification history."""
    current_user_id = get_current_user_id()
    deleted = _scoped_query(current_user_id).delete(synchronize_session=False)
    db.session.commit()
    return jsonify({'message': 'All notifications cleared', 'deleted': deleted}), 200