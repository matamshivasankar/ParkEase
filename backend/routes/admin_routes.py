from flask import Blueprint, request, jsonify, send_file
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime, timedelta
from sqlalchemy import func, extract
import csv
import io
import json

from backend.models import db, User, Facility, Booking, Slot, Payment
from backend.middleware.auth_middleware import admin_required
from backend.utils.helpers import utcnow, parse_client_datetime, iso_utc
from backend.utils.lifecycle import complete_expired_bookings

admin_bp = Blueprint('admin', __name__, url_prefix='/api/admin')


def _payment_screenshot_file(payment):
    """Filename of a payment's screenshot, or None.

    Legacy rows stored an absolute filesystem path under 'screenshot_path';
    fall back to its basename so existing uploads keep rendering.
    """
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


@admin_bp.route('/dashboard', methods=['GET'])
@jwt_required()
@admin_required
def dashboard():
    complete_expired_bookings()

    total_users = User.query.filter_by(role='user').count()
    total_facilities = Facility.query.filter_by(is_active=True).count()
    total_bookings = Booking.query.count()
    active_bookings = Booking.query.filter_by(status='active').count()
    pending_verifications = Payment.query.filter_by(status='pending_screenshot').count()

    today = utcnow().date()
    today_revenue = db.session.query(func.sum(Booking.total_amount)).filter(
        func.date(Booking.paid_at) == today,
        Booking.payment_status == 'paid'
    ).scalar() or 0

    month_start = today.replace(day=1)
    monthly_revenue = db.session.query(func.sum(Booking.total_amount)).filter(
        Booking.paid_at >= month_start,
        Booking.payment_status == 'paid'
    ).scalar() or 0

    occupancy = {}
    for vtype in ['Car', 'Bike', 'Truck', 'EV']:
        total = db.session.query(func.sum(getattr(Facility, f'total_{vtype.lower()}'))).filter_by(is_active=True).scalar() or 0
        occupied = db.session.query(func.sum(getattr(Facility, f'total_{vtype.lower()}') - getattr(Facility, f'available_{vtype.lower()}'))).filter_by(is_active=True).scalar() or 0
        occupancy[vtype] = {
            'total': total,
            'occupied': occupied,
            'available': total - occupied,
            'percentage': round((occupied / total * 100) if total > 0 else 0, 1)
        }

    return jsonify({
        'stats': {
            'total_users': total_users,
            'total_facilities': total_facilities,
            'total_bookings': total_bookings,
            'active_bookings': active_bookings,
            'pending_verifications': pending_verifications,
            'today_revenue': round(today_revenue, 2),
            'monthly_revenue': round(monthly_revenue, 2)
        },
        'occupancy': occupancy
    }), 200


@admin_bp.route('/payments/pending', methods=['GET'])
@jwt_required()
@admin_required
def pending_verifications():
    """The payment verification queue: screenshots waiting for a decision."""
    payments = Payment.query.filter_by(status='pending_screenshot').order_by(
        Payment.created_at.desc()
    ).all()

    items = []
    for payment in payments:
        booking = Booking.query.get(payment.booking_id)
        if not booking:
            continue
        user = User.query.get(payment.user_id)
        try:
            gateway = json.loads(payment.gateway_response) if payment.gateway_response else {}
        except (TypeError, ValueError):
            gateway = {}

        items.append({
            'payment_id': payment.id,
            'payment_ref': payment.payment_id,
            'amount': payment.amount,
            'method': payment.method,
            'status': payment.status,
            'transaction_id': payment.transaction_id or gateway.get('transaction_id') or '',
            'screenshot_file': _payment_screenshot_file(payment),
            'screenshot_url': (
                '/screenshots/' + _payment_screenshot_file(payment)
                if _payment_screenshot_file(payment) else None
            ),
            'uploaded_at': iso_utc(payment.created_at),
            'booking': booking.to_dict(),
            'user': {
                'id': user.id,
                'user_id': user.user_id,
                'full_name': user.full_name,
                'email': user.email,
                'phone': user.phone
            } if user else None
        })

    return jsonify({
        'verifications': items,
        'pending_count': len(items)
    }), 200


@admin_bp.route('/revenue', methods=['GET'])
@jwt_required()
@admin_required
def revenue_analytics():
    days = int(request.args.get('days', 30))
    end_date = utcnow()
    start_date = end_date - timedelta(days=days)

    daily_revenue = db.session.query(
        func.date(Booking.paid_at).label('date'),
        func.sum(Booking.total_amount).label('revenue'),
        func.count(Booking.id).label('bookings')
    ).filter(
        Booking.paid_at >= start_date,
        Booking.paid_at <= end_date,
        Booking.payment_status == 'paid'
    ).group_by(func.date(Booking.paid_at)).all()

    vehicle_revenue = db.session.query(
        Booking.vehicle_type,
        func.sum(Booking.total_amount).label('revenue'),
        func.count(Booking.id).label('bookings')
    ).filter(
        Booking.paid_at >= start_date,
        Booking.payment_status == 'paid'
    ).group_by(Booking.vehicle_type).all()

    facility_revenue = db.session.query(
        Facility.name,
        func.sum(Booking.total_amount).label('revenue'),
        func.count(Booking.id).label('bookings')
    ).join(Booking).filter(
        Booking.paid_at >= start_date,
        Booking.payment_status == 'paid'
    ).group_by(Facility.id).order_by(func.sum(Booking.total_amount).desc()).limit(10).all()

    return jsonify({
        'daily': [{'date': str(d.date), 'revenue': round(float(d.revenue), 2), 'bookings': d.bookings} for d in daily_revenue],
        'by_vehicle': [{'vehicle_type': v.vehicle_type, 'revenue': round(float(v.revenue), 2), 'bookings': v.bookings} for v in vehicle_revenue],
        'top_facilities': [{'name': f.name, 'revenue': round(float(f.revenue), 2), 'bookings': f.bookings} for f in facility_revenue]
    }), 200


@admin_bp.route('/bookings', methods=['GET'])
@jwt_required()
@admin_required
def get_all_bookings():
    complete_expired_bookings()

    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 20))
    status = request.args.get('status')
    facility_id = request.args.get('facility_id', type=int)
    user_id = request.args.get('user_id', type=int)

    query = Booking.query.order_by(Booking.created_at.desc())

    if status:
        query = query.filter_by(status=status)
    if facility_id:
        query = query.filter_by(facility_id=facility_id)
    if user_id:
        query = query.filter_by(user_id=user_id)

    pagination = query.paginate(page=page, per_page=per_page, error_out=False)

    return jsonify({
        'bookings': [b.to_dict() for b in pagination.items],
        'pagination': {
            'page': page,
            'per_page': per_page,
            'total': pagination.total,
            'pages': pagination.pages
        }
    }), 200


@admin_bp.route('/users', methods=['GET'])
@jwt_required()
@admin_required
def get_all_users():
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 20))
    search = request.args.get('search')
    role = request.args.get('role')
    is_blocked = request.args.get('is_blocked', type=bool)

    query = User.query.order_by(User.created_at.desc())

    if search:
        query = query.filter(
            (User.full_name.ilike(f'%{search}%')) |
            (User.email.ilike(f'%{search}%')) |
            (User.phone.ilike(f'%{search}%'))
        )
    if role:
        query = query.filter_by(role=role)
    if is_blocked is not None:
        query = query.filter_by(is_blocked=is_blocked)

    pagination = query.paginate(page=page, per_page=per_page, error_out=False)

    return jsonify({
        'users': [u.to_dict() for u in pagination.items],
        'pagination': {
            'page': page,
            'per_page': per_page,
            'total': pagination.total,
            'pages': pagination.pages
        }
    }), 200


@admin_bp.route('/users/<int:user_id>/block', methods=['PUT'])
@jwt_required()
@admin_required
def toggle_block_user(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404

    if user.role == 'admin':
        return jsonify({'error': 'Cannot block admin'}), 400

    user.is_blocked = not user.is_blocked
    db.session.commit()

    return jsonify({
        'message': f"User {'blocked' if user.is_blocked else 'unblocked'}",
        'user': user.to_dict()
    }), 200


@admin_bp.route('/pricing', methods=['PUT'])
@jwt_required()
@admin_required
def update_pricing():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400

    facility_id = data.get('facility_id')
    if not facility_id:
        return jsonify({'error': 'facility_id required'}), 400

    facility = Facility.query.get(facility_id)
    if not facility:
        return jsonify({'error': 'Facility not found'}), 404

    pricing_fields = [
        'rate_car_hourly', 'rate_bike_hourly', 'rate_truck_hourly', 'rate_ev_hourly',
        'monthly_car', 'monthly_bike', 'monthly_truck', 'monthly_ev'
    ]

    for field in pricing_fields:
        if field in data:
            setattr(facility, field, float(data[field]))

    db.session.commit()
    return jsonify({'message': 'Pricing updated', 'facility': facility.to_dict()}), 200


@admin_bp.route('/reports/bookings', methods=['GET'])
@jwt_required()
@admin_required
def export_bookings():
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    query = Booking.query

    if start_date:
        query = query.filter(Booking.created_at >= parse_client_datetime(start_date))
    if end_date:
        query = query.filter(Booking.created_at <= parse_client_datetime(end_date))

    bookings = query.order_by(Booking.created_at.desc()).all()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['Booking ID', 'User', 'Email', 'Facility', 'Vehicle', 'Vehicle Type',
                     'Start Time', 'End Time', 'Duration', 'Base Price', 'Discount',
                     'GST', 'Total Amount', 'Payment Status', 'Status', 'Created At'])

    for b in bookings:
        user = User.query.get(b.user_id)
        facility = Facility.query.get(b.facility_id)
        writer.writerow([
            b.booking_id,
            user.full_name if user else '',
            user.email if user else '',
            facility.name if facility else '',
            b.vehicle_no,
            b.vehicle_type,
            b.start_time.isoformat() if b.start_time else '',
            b.end_time.isoformat() if b.end_time else '',
            f"{b.duration_value} {b.duration_unit}",
            b.base_price,
            b.discount,
            b.gst,
            b.total_amount,
            b.payment_status,
            b.status,
            b.created_at.isoformat() if b.created_at else ''
        ])

    output.seek(0)
    return send_file(
        io.BytesIO(output.getvalue().encode()),
        mimetype='text/csv',
        as_attachment=True,
        download_name=f'bookings_report_{datetime.now().strftime("%Y%m%d")}.csv'
    )


@admin_bp.route('/reports/revenue', methods=['GET'])
@jwt_required()
@admin_required
def export_revenue():
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    query = Booking.query.filter(Booking.payment_status == 'paid')

    if start_date:
        query = query.filter(Booking.paid_at >= parse_client_datetime(start_date))
    if end_date:
        query = query.filter(Booking.paid_at <= parse_client_datetime(end_date))

    bookings = query.order_by(Booking.paid_at.desc()).all()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['Date', 'Booking ID', 'Facility', 'Vehicle', 'Amount', 'Payment Method'])

    for b in bookings:
        facility = Facility.query.get(b.facility_id)
        writer.writerow([
            b.paid_at.date().isoformat() if b.paid_at else '',
            b.booking_id,
            facility.name if facility else '',
            b.vehicle_no,
            b.total_amount,
            b.payment_method
        ])

    output.seek(0)
    return send_file(
        io.BytesIO(output.getvalue().encode()),
        mimetype='text/csv',
        as_attachment=True,
        download_name=f'revenue_report_{datetime.now().strftime("%Y%m%d")}.csv'
    )


@admin_bp.route('/facilities', methods=['GET'])
@jwt_required()
@admin_required
def admin_facilities():
    facilities = Facility.query.order_by(Facility.created_at.desc()).all()
    return jsonify({'facilities': [f.to_dict() for f in facilities]}), 200