from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime

from backend.models import db, User, Vehicle, Booking, Payment
from backend.middleware.auth_middleware import get_current_user_id
from backend.utils.lifecycle import complete_expired_bookings
from backend.utils.validators import validate_vehicle

user_bp = Blueprint('users', __name__, url_prefix='/api/users')


@user_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    current_user_id = get_current_user_id()
    user = User.query.get(current_user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404

    return jsonify({'user': user.to_dict()}), 200


@user_bp.route('/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    current_user_id = get_current_user_id()
    user = User.query.get(current_user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404

    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400

    if 'full_name' in data and data['full_name'].strip():
        user.full_name = data['full_name'].strip()

    if 'phone' in data and data['phone'].strip():
        if User.query.filter(User.phone == data['phone'].strip(), User.id != user.id).first():
            return jsonify({'error': 'Phone number already in use'}), 409
        user.phone = data['phone'].strip()

    db.session.commit()
    return jsonify({'message': 'Profile updated', 'user': user.to_dict()}), 200


@user_bp.route('/vehicles', methods=['GET'])
@jwt_required()
def get_vehicles():
    current_user_id = get_current_user_id()
    vehicles = Vehicle.query.filter_by(user_id=current_user_id).all()
    return jsonify({'vehicles': [v.to_dict() for v in vehicles]}), 200


@user_bp.route('/vehicles', methods=['POST'])
@jwt_required()
def add_vehicle():
    current_user_id = get_current_user_id()
    user = User.query.get(current_user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404

    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400

    validation_error = validate_vehicle(data)
    if validation_error:
        return jsonify({'error': validation_error}), 400

    vehicle_no = data['vehicle_no'].strip().upper()
    vehicle_type = data['vehicle_type']

    if Vehicle.query.filter_by(user_id=current_user_id, vehicle_no=vehicle_no).first():
        return jsonify({'error': 'Vehicle already registered'}), 409

    is_default = data.get('is_default', False)
    if is_default:
        Vehicle.query.filter_by(user_id=current_user_id, is_default=True).update({'is_default': False})

    vehicle = Vehicle(
        user_id=current_user_id,
        vehicle_no=vehicle_no,
        vehicle_type=vehicle_type,
        is_default=is_default
    )

    db.session.add(vehicle)
    db.session.commit()

    return jsonify({'message': 'Vehicle added', 'vehicle': vehicle.to_dict()}), 201


@user_bp.route('/vehicles/<int:vehicle_id>', methods=['DELETE'])
@jwt_required()
def remove_vehicle(vehicle_id):
    current_user_id = get_current_user_id()
    vehicle = Vehicle.query.filter_by(id=vehicle_id, user_id=current_user_id).first()
    if not vehicle:
        return jsonify({'error': 'Vehicle not found'}), 404

    was_default = vehicle.is_default
    db.session.delete(vehicle)

    if was_default:
        remaining = Vehicle.query.filter_by(user_id=current_user_id).first()
        if remaining:
            remaining.is_default = True

    db.session.commit()
    return jsonify({'message': 'Vehicle removed'}), 200


@user_bp.route('/vehicles/<int:vehicle_id>/default', methods=['PUT'])
@jwt_required()
def set_default_vehicle(vehicle_id):
    current_user_id = get_current_user_id()
    vehicle = Vehicle.query.filter_by(id=vehicle_id, user_id=current_user_id).first()
    if not vehicle:
        return jsonify({'error': 'Vehicle not found'}), 404

    Vehicle.query.filter_by(user_id=current_user_id, is_default=True).update({'is_default': False})
    vehicle.is_default = True
    db.session.commit()

    return jsonify({'message': 'Default vehicle updated', 'vehicle': vehicle.to_dict()}), 200


@user_bp.route('/bookings', methods=['GET'])
@jwt_required()
def get_user_bookings():
    current_user_id = get_current_user_id()
    user = User.query.get(current_user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404

    # An elapsed booking must read back as completed, not sit on `active`.
    complete_expired_bookings(current_user_id)

    status = request.args.get('status')
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 10))

    query = Booking.query.filter_by(user_id=current_user_id).order_by(Booking.created_at.desc())

    if status:
        query = query.filter_by(status=status)

    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    bookings = pagination.items

    def _payment_screenshot_file(payment):
        """Filename of a payment's screenshot, or None."""
        import json
        if not payment.gateway_response:
            return None
        try:
            gw = json.loads(payment.gateway_response)
        except (TypeError, ValueError):
            return None
        name = gw.get('screenshot_file')
        if not name:
            legacy = gw.get('screenshot_path')
            if legacy:
                name = str(legacy).replace('\\', '/').split('/')[-1]
        return name or None

    def _booking_payment_info(booking):
        """Get the latest payment info for a booking, including screenshot."""
        payment = Payment.query.filter_by(booking_id=booking.id).order_by(Payment.created_at.desc()).first()
        if not payment:
            return {}
        screenshot_file = _payment_screenshot_file(payment)
        return {
            'payment_id': payment.payment_id,
            'payment_status': payment.status,
            'transaction_id': payment.transaction_id,
            'payment_method': payment.method,
            'screenshot_file': screenshot_file,
            'screenshot_url': f'/screenshots/{screenshot_file}' if screenshot_file else None,
            'paid_at': payment.paid_at.isoformat() if payment.paid_at else None
        }

    return jsonify({
        'bookings': [b.to_dict() | _booking_payment_info(b) for b in bookings],
        'pagination': {
            'page': page,
            'per_page': per_page,
            'total': pagination.total,
            'pages': pagination.pages
        }
    }), 200