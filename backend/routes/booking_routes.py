from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime, timedelta
import json

from backend.models import db, Booking, Slot, Facility, Vehicle, User
from backend.utils.helpers import (calculate_price, generate_booking_id, lock_slots,
                                release_slots, lock_slots_for_booking, parse_client_datetime, utcnow)
from backend.utils.qr_generator import generate_qr_code
from backend.middleware.auth_middleware import admin_required, get_current_user_id

booking_bp = Blueprint('bookings', __name__, url_prefix='/api/bookings')

MAX_SLOTS_PER_BOOKING = 4


def _resolve_vehicle_numbers(data, slot_codes):
    """Normalise the submitted vehicle numbers and check the 1:1 slot rule.

    Every booked slot needs its own vehicle number, so the count must match the
    slot count exactly and no number may be blank or repeated.
    """
    raw = data.get('vehicle_nos')

    if raw is None:
        # Single-slot bookings may still send the legacy scalar field.
        raw = [data.get('vehicle_no')]
    elif not isinstance(raw, list):
        return None, 'vehicle_nos must be a list of vehicle numbers'

    vehicles = []
    for item in raw:
        number = str(item or '').strip().upper()
        if not number:
            return None, 'Every selected slot needs a vehicle number'
        if len(number) > 15:
            return None, 'Vehicle number cannot exceed 15 characters'
        vehicles.append(number)

    if len(vehicles) != len(slot_codes):
        return None, f'You selected {len(slot_codes)} slot(s) but entered {len(vehicles)} vehicle number(s). One vehicle number is required per slot.'

    duplicates = {n for n in vehicles if vehicles.count(n) > 1}
    if duplicates:
        return None, 'Duplicate vehicle number(s): ' + ', '.join(sorted(duplicates))

    return vehicles, None


@booking_bp.route('', methods=['POST'])
@jwt_required()
def create_booking():
    current_user_id = get_current_user_id()
    user = User.query.get(current_user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404

    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400

    required = ['facility_id', 'vehicle_type', 'start_time', 'end_time', 'duration_value', 'duration_unit', 'slot_codes']
    for field in required:
        if field not in data:
            return jsonify({'error': f'{field} is required'}), 400
    if 'vehicle_nos' not in data and 'vehicle_no' not in data:
        return jsonify({'error': 'A vehicle number is required for every slot'}), 400

    facility = Facility.query.get(data['facility_id'])
    if not facility:
        return jsonify({'error': 'Facility not found'}), 404

    try:
        start_time = parse_client_datetime(data['start_time'])
        end_time = parse_client_datetime(data['end_time'])
    except:
        return jsonify({'error': 'Invalid date format'}), 400

    if start_time >= end_time:
        return jsonify({'error': 'End time must be after start time'}), 400

    if start_time < utcnow():
        return jsonify({'error': 'Start time cannot be in the past'}), 400

    slot_codes = data['slot_codes']
    if not isinstance(slot_codes, list) or len(slot_codes) == 0:
        return jsonify({'error': 'At least one slot required'}), 400

    if len(set(slot_codes)) != len(slot_codes):
        return jsonify({'error': 'Duplicate slots selected'}), 400

    if len(slot_codes) > MAX_SLOTS_PER_BOOKING:
        return jsonify({'error': f'You can book at most {MAX_SLOTS_PER_BOOKING} slots at a time'}), 400

    vehicle_nos, vehicle_error = _resolve_vehicle_numbers(data, slot_codes)
    if vehicle_error:
        return jsonify({'error': vehicle_error}), 400

    # Atomically lock slots using SELECT FOR UPDATE to prevent race conditions
    locked, result = lock_slots_for_booking(
        slot_codes=slot_codes,
        facility_id=facility.id,
        vehicle_type=data['vehicle_type'],
        start_time=start_time,
        end_time=end_time
    )
    if not locked:
        return jsonify({'error': result}), 409

    slots = result

    try:
        price_data = calculate_price(
            facility=facility,
            vehicle_type=data['vehicle_type'],
            duration_value=data['duration_value'],
            duration_unit=data['duration_unit'],
            start_time=start_time,
            slot_count=len(slot_codes)
        )

        booking = Booking(
            booking_id=generate_booking_id(),
            user_id=current_user_id,
            facility_id=facility.id,
            vehicle_no=vehicle_nos[0],
            vehicle_type=data['vehicle_type'],
            start_time=start_time,
            end_time=end_time,
            duration_value=data['duration_value'],
            duration_unit=data['duration_unit'],
            base_price=price_data['base_price'],
            discount=price_data['discount'],
            discount_reason=price_data['discount_reason'],
            gst=price_data['gst'],
            total_amount=price_data['total_amount'],
            status='reserved'
        )
        booking.set_slot_codes(slot_codes)
        booking.set_vehicles(slot_codes, vehicle_nos)

        db.session.add(booking)
        db.session.flush()

        qr_data = {
            'booking_id': booking.booking_id,
            'facility': facility.name,
            'slots': slot_codes,
            'vehicles': vehicle_nos,
            'start': start_time.isoformat(),
            'end': end_time.isoformat()
        }
        booking.qr_code = generate_qr_code(qr_data)

        db.session.commit()

        # Sync availability counts
        facility.sync_availability()
        db.session.commit()

        return jsonify({
            'message': 'Booking created successfully',
            'booking': booking.to_dict(),
            'price_breakdown': price_data
        }), 201

    except Exception as e:
        release_slots(slot_codes, facility_id=facility.id)
        db.session.rollback()
        return jsonify({'error': 'Failed to create booking'}), 500


@booking_bp.route('/<int:booking_id>', methods=['GET'])
@jwt_required()
def get_booking(booking_id):
    current_user_id = get_current_user_id()
    booking = Booking.query.get(booking_id)
    if not booking:
        return jsonify({'error': 'Booking not found'}), 404

    if booking.user_id != current_user_id:
        user = User.query.get(current_user_id)
        if not user or user.role != 'admin':
            return jsonify({'error': 'Unauthorized'}), 403

    return jsonify({'booking': booking.to_dict()}), 200


@booking_bp.route('/<int:booking_id>', methods=['PUT'])
@jwt_required()
def modify_booking(booking_id):
    current_user_id = get_current_user_id()
    booking = Booking.query.get(booking_id)
    if not booking:
        return jsonify({'error': 'Booking not found'}), 404

    if booking.user_id != current_user_id:
        return jsonify({'error': 'Unauthorized'}), 403

    if booking.status not in ['reserved', 'active']:
        return jsonify({'error': 'Cannot modify this booking'}), 400

    if booking.start_time <= utcnow():
        return jsonify({'error': 'Cannot modify booking that has started'}), 400

    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400

    release_slots(booking.get_slot_codes(), facility_id=booking.facility_id)

    if 'start_time' in data and 'end_time' in data:
        try:
            new_start = parse_client_datetime(data['start_time'])
            new_end = parse_client_datetime(data['end_time'])
        except:
            return jsonify({'error': 'Invalid date format'}), 400

        if new_start >= new_end or new_start < utcnow():
            return jsonify({'error': 'Invalid time range'}), 400

        booking.start_time = new_start
        booking.end_time = new_end

    if 'duration_value' in data:
        booking.duration_value = data['duration_value']
    if 'duration_unit' in data:
        booking.duration_unit = data['duration_unit']

    if 'slot_codes' in data:
        slot_codes = data['slot_codes']
        if not isinstance(slot_codes, list) or not slot_codes:
            return jsonify({'error': 'At least one slot required'}), 400
        if len(set(slot_codes)) != len(slot_codes):
            return jsonify({'error': 'Duplicate slots selected'}), 400
        if len(slot_codes) > MAX_SLOTS_PER_BOOKING:
            return jsonify({'error': f'You can book at most {MAX_SLOTS_PER_BOOKING} slots at a time'}), 400
        slots = Slot.query.filter(
            Slot.facility_id == booking.facility_id,
            Slot.slot_code.in_(slot_codes),
            Slot.vehicle_type == booking.vehicle_type
        ).all()
        if len(slots) != len(slot_codes):
            return jsonify({'error': 'Invalid slots'}), 400
        for slot in slots:
            if not slot.is_available(booking.start_time, booking.end_time):
                return jsonify({'error': f'Slot {slot.slot_code} not available'}), 409
        lock_slots(slots, booking.end_time)
        booking.set_slot_codes(slot_codes)

    # Vehicle numbers stay 1:1 with slots, so changing the slot count or the
    # vehicle list is validated together.
    wants_vehicles = 'vehicle_nos' in data or 'vehicle_no' in data
    slot_codes = booking.get_slot_codes()
    if wants_vehicles:
        vehicle_nos, vehicle_error = _resolve_vehicle_numbers(data, slot_codes)
        if vehicle_error:
            return jsonify({'error': vehicle_error}), 400
        booking.set_vehicles(slot_codes, vehicle_nos)
    elif len(booking.get_vehicles()) != len(slot_codes):
        return jsonify({
            'error': f'This booking has {len(slot_codes)} slot(s), so {len(slot_codes)} vehicle number(s) are required. Send vehicle_nos.'
        }), 400

    facility = Facility.query.get(booking.facility_id)
    price_data = calculate_price(
        facility=facility,
        vehicle_type=booking.vehicle_type,
        duration_value=booking.duration_value,
        duration_unit=booking.duration_unit,
        start_time=booking.start_time,
        slot_count=len(slot_codes)
    )
    booking.base_price = price_data['base_price']
    booking.discount = price_data['discount']
    booking.discount_reason = price_data['discount_reason']
    booking.gst = price_data['gst']
    booking.total_amount = price_data['total_amount']

    db.session.commit()

    # Sync availability counts
    facility.sync_availability()
    db.session.commit()

    return jsonify({'message': 'Booking modified', 'booking': booking.to_dict()}), 200


@booking_bp.route('/<int:booking_id>', methods=['DELETE'])
@jwt_required()
def cancel_booking(booking_id):
    current_user_id = get_current_user_id()
    booking = Booking.query.get(booking_id)
    if not booking:
        return jsonify({'error': 'Booking not found'}), 404

    if booking.user_id != current_user_id:
        user = User.query.get(current_user_id)
        if not user or user.role != 'admin':
            return jsonify({'error': 'Unauthorized'}), 403

    if booking.status == 'completed':
        return jsonify({'error': 'Cannot cancel completed booking'}), 400

    if booking.status == 'cancelled':
        return jsonify({'error': 'Booking already cancelled'}), 400

    hours_until_start = (booking.start_time - utcnow()).total_seconds() / 3600

    if booking.payment_status == 'paid':
        if hours_until_start >= 24:
            refund_percent = 1.0
        elif hours_until_start >= 2:
            refund_percent = 0.5
        else:
            refund_percent = 0.0

        if refund_percent > 0:
            refund_amount = booking.total_amount * refund_percent
            user = User.query.get(booking.user_id)
            user.wallet_balance += refund_amount
            booking.payment_status = 'refunded'

    release_slots(booking.get_slot_codes(), facility_id=booking.facility_id)
    booking.status = 'cancelled'
    db.session.commit()

    # Sync availability counts
    facility = Facility.query.get(booking.facility_id)
    if facility:
        facility.sync_availability()
        db.session.commit()

    return jsonify({'message': 'Booking cancelled', 'booking': booking.to_dict()}), 200


@booking_bp.route('/<int:booking_id>/checkin', methods=['POST'])
@jwt_required()
def checkin(booking_id):
    current_user_id = get_current_user_id()
    booking = Booking.query.get(booking_id)
    if not booking:
        return jsonify({'error': 'Booking not found'}), 404

    if booking.user_id != current_user_id:
        return jsonify({'error': 'Unauthorized'}), 403

    if booking.status not in ['reserved', 'confirmed', 'active']:
        return jsonify({'error': 'Booking not in valid state for check-in'}), 400

    if booking.payment_status != 'paid':
        return jsonify({'error': 'Payment required before check-in'}), 400

    now = utcnow()
    if now < booking.start_time - timedelta(minutes=30):
        return jsonify({'error': 'Too early for check-in'}), 400

    booking.check_in_time = now
    booking.status = 'active'

    for slot_code in booking.get_slot_codes():
        slot = Slot.query.filter_by(facility_id=booking.facility_id, slot_code=slot_code).first()
        if slot:
            slot.is_occupied = True
            slot.occupied_until = booking.end_time

    db.session.commit()

    # Sync availability counts
    facility = Facility.query.get(booking.facility_id)
    if facility:
        facility.sync_availability()
        db.session.commit()

    return jsonify({'message': 'Check-in successful', 'booking': booking.to_dict()}), 200


@booking_bp.route('/<int:booking_id>/checkout', methods=['POST'])
@jwt_required()
def checkout(booking_id):
    current_user_id = get_current_user_id()
    booking = Booking.query.get(booking_id)
    if not booking:
        return jsonify({'error': 'Booking not found'}), 404

    if booking.user_id != current_user_id:
        return jsonify({'error': 'Unauthorized'}), 403

    if booking.status != 'active':
        return jsonify({'error': 'Booking not active'}), 400

    now = utcnow()
    booking.check_out_time = now
    booking.status = 'completed'

    for slot_code in booking.get_slot_codes():
        slot = Slot.query.filter_by(facility_id=booking.facility_id, slot_code=slot_code).first()
        if slot:
            slot.is_occupied = False
            slot.occupied_until = None

    db.session.commit()

    # Sync availability counts
    facility = Facility.query.get(booking.facility_id)
    if facility:
        facility.sync_availability()
        db.session.commit()

    return jsonify({'message': 'Check-out successful', 'booking': booking.to_dict()}), 200


@booking_bp.route('/<int:booking_id>/receipt', methods=['GET'])
@jwt_required()
def download_receipt(booking_id):
    current_user_id = get_current_user_id()
    booking = Booking.query.get(booking_id)
    if not booking:
        return jsonify({'error': 'Booking not found'}), 404

    if booking.user_id != current_user_id:
        user = User.query.get(current_user_id)
        if not user or user.role != 'admin':
            return jsonify({'error': 'Unauthorized'}), 403

    from backend.utils.receipt_generator import generate_receipt_pdf
    pdf_path = generate_receipt_pdf(booking)

    from flask import send_file
    return send_file(pdf_path, as_attachment=True, download_name=f"receipt_{booking.booking_id}.pdf")


@booking_bp.route('/price-estimate', methods=['POST'])
def price_estimate():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400

    required = ['facility_id', 'vehicle_type', 'duration_value', 'duration_unit', 'start_time']
    for field in required:
        if field not in data:
            return jsonify({'error': f'{field} is required'}), 400

    facility = Facility.query.get(data['facility_id'])
    if not facility:
        return jsonify({'error': 'Facility not found'}), 404

    try:
        start_time = parse_client_datetime(data['start_time'])
    except:
        return jsonify({'error': 'Invalid date format'}), 400

    price_data = calculate_price(
        facility=facility,
        vehicle_type=data['vehicle_type'],
        duration_value=data['duration_value'],
        duration_unit=data['duration_unit'],
        start_time=start_time,
        slot_count=data.get('slot_count', 1)
    )

    return jsonify({'price_breakdown': price_data}), 200