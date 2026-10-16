from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
import uuid
import json
import base64
import os
import re

from backend.models import db, Booking, User, Payment, Facility, WalletRecharge, WalletTransaction
from backend.middleware.auth_middleware import admin_required, get_current_user_id
from backend.utils.helpers import utcnow, iso_utc, release_slots
from backend.utils.notifier import create_notification, notify_admins
from backend.utils.qr_generator import generate_qr_code_base64

payment_bp = Blueprint('payments', __name__, url_prefix='/api/payments')

MAX_SCREENSHOT_BYTES = 5 * 1024 * 1024
SCREENSHOT_MAGIC = (b'\x89PNG\r\n\x1a\n', b'\xff\xd8\xff', b'GIF87a', b'GIF89a', b'RIFF')


@payment_bp.route('/initiate', methods=['POST'])
@jwt_required()
def initiate_payment():
    current_user_id = get_current_user_id()
    user = User.query.get(current_user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404

    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400

    booking_id = data.get('booking_id')
    payment_method = data.get('payment_method')

    if not booking_id or not payment_method:
        return jsonify({'error': 'booking_id and payment_method required'}), 400

    if payment_method not in ['upi', 'wallet']:
        return jsonify({'error': 'Invalid payment method. Only UPI and Wallet are supported.'}), 400

    booking = Booking.query.get(booking_id)
    if not booking:
        return jsonify({'error': 'Booking not found'}), 404

    if booking.user_id != current_user_id:
        return jsonify({'error': 'Unauthorized'}), 403

    if booking.payment_status == 'paid':
        return jsonify({'error': 'Booking already paid'}), 400

    if booking.status == 'cancelled':
        return jsonify({'error': 'Cannot pay for cancelled booking'}), 400

    # Create payment record
    payment = Payment(
        payment_id=f"PAY-{datetime.now().year}-{Payment.query.count() + 1:05d}",
        booking_id=booking.id,
        user_id=current_user_id,
        amount=booking.total_amount,
        method=payment_method,
        status='pending'
    )
    db.session.add(payment)
    db.session.flush()

    if payment_method == 'wallet':
        if user.wallet_balance < booking.total_amount:
            return jsonify({'error': 'Insufficient wallet balance'}), 400
        user.wallet_balance -= booking.total_amount
        booking.payment_status = 'paid'
        booking.payment_method = 'wallet'
        booking.transaction_id = f"TXN-{uuid.uuid4().hex[:12].upper()}"
        booking.paid_at = utcnow()
        
        payment.status = 'paid'
        payment.transaction_id = booking.transaction_id
        payment.paid_at = utcnow()
        db.session.commit()

        # Emit real-time update
        emit_payment_update(booking.id, 'paid', payment.to_dict())

        return jsonify({
            'message': 'Payment successful',
            'payment': payment.to_dict()
        }), 200

    db.session.commit()

    # Emit real-time update
    emit_payment_update(booking.id, 'initiated', payment.to_dict())

    return jsonify({
        'message': 'Payment initiated',
        'payment': payment.to_dict(),
        'payment_gateway_url': f'/payment/gateway/{booking.booking_id}?method={payment_method}'
    }), 200


def emit_payment_update(booking_id, event, data):
    """Emit real-time payment update via SocketIO if available"""
    try:
        from flask_socketio import emit
        socketio = current_app.extensions.get('socketio')
        if socketio:
            socketio.emit(f'payment_{event}', data, room=f'booking_{booking_id}')
    except:
        pass  # SocketIO not available


@payment_bp.route('/upi/qr', methods=['POST'])
@jwt_required()
def generate_upi_qr():
    """Generate UPI QR code for payment"""
    current_user_id = get_current_user_id()
    user = User.query.get(current_user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404

    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400

    booking_id = data.get('booking_id')
    if not booking_id:
        return jsonify({'error': 'booking_id required'}), 400

    booking = Booking.query.get(booking_id)
    if not booking:
        return jsonify({'error': 'Booking not found'}), 404

    if booking.user_id != current_user_id:
        return jsonify({'error': 'Unauthorized'}), 403

    if booking.payment_status == 'paid':
        return jsonify({'error': 'Booking already paid'}), 400

    # UPI details for merchant
    merchant_upi = os.environ.get('MERCHANT_UPI', '6305898891@upi')
    merchant_name = os.environ.get('MERCHANT_NAME', 'ParkEase')

    # Create UPI payment URL
    upi_url = f"upi://pay?pa={merchant_upi}&pn={merchant_name}&am={booking.total_amount:.2f}&cu=INR&tn=Booking%20{booking.booking_id}&tr={booking.booking_id}"

    # Generate QR code as base64
    qr_base64 = generate_qr_code_base64(upi_url)

    # The amount is already fixed on the booking, but the client shows how it was
    # derived, so send the slot-type rate and the booked duration that produced it.
    facility = Facility.query.get(booking.facility_id)
    slot_count = max(1, len(booking.get_slot_codes()))
    monthly = booking.duration_unit == 'monthly'
    rate = facility.get_monthly_rate(booking.vehicle_type) if monthly and facility \
        else facility.get_hourly_rate(booking.vehicle_type)

    return jsonify({
        'upi_url': upi_url,
        'qr_code': qr_base64,
        'amount': booking.total_amount,
        'booking_id': booking.booking_id,
        'merchant_upi': merchant_upi,
        'merchant_name': merchant_name,
        'pricing': {
            'vehicle_type': booking.vehicle_type,
            'slot_count': slot_count,
            'duration_value': booking.duration_value,
            'duration_unit': booking.duration_unit,
            'rate_basis': 'monthly' if monthly else 'hourly',
            'rate': rate,
            'base_price': booking.base_price,
            'discount': booking.discount,
            'discount_reason': booking.discount_reason,
            'gst': booking.gst,
            'total': booking.total_amount
        }
    }), 200


@payment_bp.route('/upi/upload-screenshot', methods=['POST'])
@jwt_required()
def upload_payment_screenshot():
    """Upload UPI payment screenshot and queue it for admin verification."""
    current_user_id = get_current_user_id()
    user = User.query.get(current_user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404

    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400

    booking_id = data.get('booking_id')
    screenshot_base64 = data.get('screenshot_base64')
    transaction_id = str(data.get('transaction_id') or '').strip()

    if not booking_id or not screenshot_base64:
        return jsonify({'error': 'booking_id and screenshot_base64 required'}), 400

    if not transaction_id:
        return jsonify({'error': 'Transaction ID is required'}), 400

    if not re.match(r'^[0-9]{12}$', transaction_id):
        return jsonify({'error': 'Transaction ID must contain exactly 12 digits.'}), 400

    booking = Booking.query.get(booking_id)
    if not booking:
        return jsonify({'error': 'Booking not found'}), 404

    if booking.user_id != current_user_id:
        return jsonify({'error': 'Unauthorized'}), 403

    if booking.payment_status == 'paid':
        return jsonify({'error': 'Booking already paid'}), 400

    if booking.status == 'cancelled':
        return jsonify({'error': 'Cannot submit payment for a cancelled booking'}), 400

    # Decode and sanity-check the payload. The client already validates the
    # mime type, but the server must not trust that.
    try:
        encoded = screenshot_base64.split(',', 1)[1] if ',' in screenshot_base64 else screenshot_base64
        screenshot_data = base64.b64decode(encoded, validate=True)
    except Exception:
        return jsonify({'error': 'Screenshot is not valid base64'}), 400

    if not screenshot_data:
        return jsonify({'error': 'Screenshot is empty'}), 400
    if len(screenshot_data) > MAX_SCREENSHOT_BYTES:
        return jsonify({'error': 'Screenshot exceeds 5MB limit'}), 400
    if not screenshot_data.startswith(SCREENSHOT_MAGIC):
        return jsonify({'error': 'Screenshot must be a PNG, JPEG or GIF image'}), 400

    # Get or create the pending payment record
    payment = Payment.query.filter_by(booking_id=booking.id, status='pending').order_by(Payment.created_at.desc()).first()
    if not payment:
        payment = Payment(
            payment_id=f"PAY-{datetime.now().year}-{Payment.query.count() + 1:05d}",
            booking_id=booking.id,
            user_id=current_user_id,
            amount=booking.total_amount,
            method='upi',
            status='pending_screenshot'
        )
        db.session.add(payment)
    else:
        payment.status = 'pending_screenshot'

    payment.transaction_id = transaction_id or None
    # The booking-level flag is what the admin queue and the user dashboard read,
    # so it must move in lockstep with the payment status.
    booking.payment_status = 'pending_verification'

    # Read the folder from the active app config rather than the Config class:
    # the testing config points it at a scratch directory, and writing to the
    # class attribute there would litter backend/screenshots instead.
    folder = current_app.config['SCREENSHOT_FOLDER']
    try:
        os.makedirs(folder, exist_ok=True)
        extension = 'jpg' if screenshot_data.startswith(b'\xff\xd8\xff') else (
            'gif' if screenshot_data.startswith((b'GIF87a', b'GIF89a')) else (
                'webp' if screenshot_data.startswith(b'RIFF') else 'png'))
        screenshot_filename = f"screenshot_{booking.booking_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{extension}"
        screenshot_path = os.path.join(folder, screenshot_filename)
        with open(screenshot_path, 'wb') as f:
            f.write(screenshot_data)
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to save screenshot: {str(e)}'}), 500

    payment.gateway_response = json.dumps({
        # Store the filename, not the absolute path: the DB should not depend on
        # where the server happens to keep its files.
        'screenshot_file': screenshot_filename,
        'transaction_id': transaction_id,
        'uploaded_at': utcnow().isoformat()
    })

    # Tell the admins there is something to check.
    notify_admins(
        ntype='payment_verification',
        title='Payment screenshot awaiting review',
        message=f"{user.full_name} submitted a UPI screenshot for booking {booking.booking_id} of Rs.{booking.total_amount:.2f}.",
        link='admin'
    )

    db.session.commit()

    # Emit real-time update
    emit_payment_update(booking.id, 'screenshot_uploaded', payment.to_dict())

    return jsonify({
        'message': 'Screenshot uploaded successfully. An admin will review it shortly.',
        'payment': payment.to_dict(),
        'booking': booking.to_dict()
    }), 200


@payment_bp.route('/admin/verify-screenshot/<int:payment_id>', methods=['POST'])
@jwt_required()
@admin_required
def admin_verify_screenshot(payment_id):
    """Admin approves or rejects a submitted UPI payment screenshot."""
    data = request.get_json() or {}
    action = data.get('action')  # 'approve' or 'reject'
    notes = str(data.get('notes') or '').strip()

    admin = User.query.get(get_current_user_id())

    payment = Payment.query.get(payment_id)
    if not payment:
        return jsonify({'error': 'Payment not found'}), 404

    booking = Booking.query.get(payment.booking_id)
    if not booking:
        return jsonify({'error': 'Booking not found'}), 404

    if action not in ('approve', 'reject'):
        return jsonify({'error': 'Invalid action. Use approve or reject'}), 400

    # Only a screenshot that is actually queued may be decided, so a double click
    # or a stale admin tab cannot flip an already-settled payment.
    if payment.status != 'pending_screenshot':
        return jsonify({
            'error': f'Payment is not awaiting verification (current status: {payment.status})'
        }), 409

    if booking.payment_status == 'paid':
        return jsonify({'error': 'Booking is already paid'}), 409

    existing_data = json.loads(payment.gateway_response) if payment.gateway_response else {}

    if action == 'approve':
        booking.payment_status = 'paid'
        booking.payment_method = 'upi'
        booking.transaction_id = (
            existing_data.get('transaction_id')
            or payment.transaction_id
            or f"TXN-{uuid.uuid4().hex[:12].upper()}"
        )
        booking.paid_at = utcnow()
        booking.status = 'confirmed'  # Confirm the booking - slot is now allocated

        payment.status = 'paid'
        payment.transaction_id = booking.transaction_id
        payment.paid_at = utcnow()
        existing_data.update({
            'verified': True,
            'verified_by': admin.user_id if admin else 'admin',
            'verified_by_name': admin.full_name if admin else 'Admin',
            'verified_at': utcnow().isoformat(),
            'notes': notes
        })
        payment.gateway_response = json.dumps(existing_data)

        create_notification(
            booking.user_id,
            ntype='payment_approved',
            title='Payment approved',
            message=f"Your payment of Rs.{booking.total_amount:.2f} for booking {booking.booking_id} was verified and your slot is confirmed.",
            link='dashboard'
        )
        message = 'Payment approved and booking confirmed'
    else:
        booking.payment_status = 'failed'
        booking.status = 'cancelled'  # Cancel booking on payment rejection

        # The slots were held for this booking, so hand them back to the pool.
        release_slots(booking.get_slot_codes(), facility_id=booking.facility_id)

        payment.status = 'failed'
        existing_data.update({
            'verified': False,
            'verified_by': admin.user_id if admin else 'admin',
            'verified_by_name': admin.full_name if admin else 'Admin',
            'verified_at': utcnow().isoformat(),
            'notes': notes,
            'error': 'Screenshot verification failed'
        })
        payment.gateway_response = json.dumps(existing_data)

        create_notification(
            booking.user_id,
            ntype='payment_rejected',
            title='Payment rejected',
            message=(notes and
                     f"Your payment for booking {booking.booking_id} was rejected: {notes}"
                     ) or
                    f"Your payment for booking {booking.booking_id} was rejected and the booking was cancelled.",
            link='dashboard'
        )
        message = 'Payment rejected and booking cancelled'

    db.session.commit()

    # Sync availability counts
    facility = Facility.query.get(booking.facility_id)
    if facility:
        facility.sync_availability()
        db.session.commit()

    # Emit real-time updates
    emit_payment_update(booking.id, payment.status, payment.to_dict())
    # Emit booking status update for real-time UI update
    try:
        socketio = current_app.extensions.get('socketio')
        if socketio:
            socketio.emit('booking_updated', booking.to_dict(), room=f'booking_{booking.id}')
            socketio.emit('booking_updated', booking.to_dict(), room=f'user_{booking.user_id}')
    except:
        pass

    return jsonify({
        'message': message,
        'payment': payment.to_dict(),
        'booking': booking.to_dict()
    }), 200


@payment_bp.route('/verify', methods=['POST'])
@jwt_required()
def verify_payment():
    current_user_id = get_current_user_id()
    user = User.query.get(current_user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404

    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400

    booking_id = data.get('booking_id')
    transaction_id = data.get('transaction_id')
    payment_method = data.get('payment_method')

    if not all([booking_id, transaction_id, payment_method]):
        return jsonify({'error': 'booking_id, transaction_id, and payment_method required'}), 400

    booking = Booking.query.get(booking_id)
    if not booking:
        return jsonify({'error': 'Booking not found'}), 404

    if booking.user_id != current_user_id:
        return jsonify({'error': 'Unauthorized'}), 403

    if booking.payment_status == 'paid':
        return jsonify({'error': 'Already paid'}), 400

    # Get the pending payment record
    payment = Payment.query.filter_by(booking_id=booking.id, status='pending').order_by(Payment.created_at.desc()).first()
    if not payment:
        return jsonify({'error': 'No pending payment found'}), 404

    import random
    success = random.random() > 0.1

    if success:
        booking.payment_status = 'paid'
        booking.payment_method = payment_method
        booking.transaction_id = transaction_id
        booking.paid_at = utcnow()
        
        payment.status = 'paid'
        payment.transaction_id = transaction_id
        payment.paid_at = utcnow()
        payment.gateway_response = json.dumps({'verified': True, 'method': payment_method})
        db.session.commit()

        # Emit real-time update
        emit_payment_update(booking.id, 'paid', payment.to_dict())

        return jsonify({
            'message': 'Payment verified successfully',
            'payment': payment.to_dict()
        }), 200
    else:
        booking.payment_status = 'failed'
        payment.status = 'failed'
        payment.gateway_response = json.dumps({'verified': False, 'method': payment_method, 'error': 'Payment declined'})
        db.session.commit()

        # Emit real-time update
        emit_payment_update(booking.id, 'failed', payment.to_dict())

        return jsonify({'error': 'Payment failed. Please try again.', 'payment': payment.to_dict()}), 400


@payment_bp.route('/refund', methods=['POST'])
@jwt_required()
@admin_required
def process_refund():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400

    booking_id = data.get('booking_id')
    amount = data.get('amount')
    reason = data.get('reason', 'Admin refund')

    if not booking_id or not amount:
        return jsonify({'error': 'booking_id and amount required'}), 400

    booking = Booking.query.get(booking_id)
    if not booking:
        return jsonify({'error': 'Booking not found'}), 404

    if booking.payment_status != 'paid':
        return jsonify({'error': 'Booking not paid'}), 400

    if amount > booking.total_amount:
        return jsonify({'error': 'Refund amount exceeds payment'}), 400

    user = User.query.get(booking.user_id)
    user.wallet_balance += amount
    booking.payment_status = 'refunded'
    db.session.commit()

    return jsonify({
        'message': 'Refund processed',
        'refund': {
            'booking_id': booking.booking_id,
            'amount': amount,
            'reason': reason,
            'new_wallet_balance': user.wallet_balance
        }
    }), 200


@payment_bp.route('/history', methods=['GET'])
@jwt_required()
def payment_history():
    current_user_id = get_current_user_id()
    user = User.query.get(current_user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404

    bookings = Booking.query.filter(
        Booking.user_id == current_user_id,
        Booking.payment_status.in_(['paid', 'refunded', 'failed'])
    ).order_by(Booking.paid_at.desc()).all()

    return jsonify({
        'payments': [{
            'booking_id': b.booking_id,
            'transaction_id': b.transaction_id,
            'amount': b.total_amount,
            'method': b.payment_method,
            'status': b.payment_status,
            'paid_at': iso_utc(b.paid_at)
        } for b in bookings]
    }), 200


@payment_bp.route('/wallet', methods=['GET'])
@jwt_required()
def get_wallet():
    current_user_id = get_current_user_id()
    user = User.query.get(current_user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404

    return jsonify({'wallet_balance': user.wallet_balance}), 200


@payment_bp.route('/wallet/add', methods=['POST'])
@jwt_required()
def add_to_wallet():
    current_user_id = get_current_user_id()
    user = User.query.get(current_user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404

    data = request.get_json()
    if not data or 'amount' not in data:
        return jsonify({'error': 'Amount required'}), 400

    amount = float(data['amount'])
    if amount <= 0 or amount > 50000:
        return jsonify({'error': 'Invalid amount (1-50000)'}), 400

    user.wallet_balance += amount
    db.session.commit()

    return jsonify({
        'message': 'Amount added to wallet',
        'wallet_balance': user.wallet_balance
    }), 200


@payment_bp.route('/status/<int:booking_id>', methods=['GET'])
@jwt_required()
def payment_status(booking_id):
    """Real-time payment status check"""
    current_user_id = get_current_user_id()
    booking = Booking.query.get(booking_id)
    if not booking:
        return jsonify({'error': 'Booking not found'}), 404

    if booking.user_id != current_user_id:
        user = User.query.get(current_user_id)
        if not user or user.role != 'admin':
            return jsonify({'error': 'Unauthorized'}), 403

    payment = Payment.query.filter_by(booking_id=booking.id).order_by(Payment.created_at.desc()).first()
    
    return jsonify({
        'booking_id': booking.booking_id,
        'payment_status': booking.payment_status,
        'payment': payment.to_dict() if payment else None
    }), 200


@payment_bp.route('/webhook', methods=['POST'])
def payment_webhook():
    """Payment gateway webhook endpoint for real-time updates"""
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400

    booking_id = data.get('booking_id')
    transaction_id = data.get('transaction_id')
    status = data.get('status')  # 'paid', 'failed', 'refunded'
    gateway_response = data

    if not all([booking_id, transaction_id, status]):
        return jsonify({'error': 'Missing required fields'}), 400

    booking = Booking.query.filter_by(booking_id=booking_id).first()
    if not booking:
        return jsonify({'error': 'Booking not found'}), 404

    payment = Payment.query.filter_by(booking_id=booking.id, transaction_id=transaction_id).first()
    if not payment:
        # Create payment record if doesn't exist
        payment = Payment(
            payment_id=f"PAY-{datetime.now().year}-{Payment.query.count() + 1:05d}",
            booking_id=booking.id,
            user_id=booking.user_id,
            amount=booking.total_amount,
            method=data.get('method', 'gateway'),
            status=status,
            transaction_id=transaction_id,
            gateway_response=json.dumps(gateway_response),
            paid_at=utcnow() if status == 'paid' else None
        )
        db.session.add(payment)
    else:
        payment.status = status
        payment.gateway_response = json.dumps(gateway_response)
        if status == 'paid':
            payment.paid_at = utcnow()

    # Update booking
    booking.payment_status = status
    booking.transaction_id = transaction_id
    booking.payment_method = data.get('method', 'gateway')
    if status == 'paid':
        booking.paid_at = utcnow()
        booking.status = 'reserved'

    db.session.commit()

    # Emit real-time update
    emit_payment_update(booking.id, status, payment.to_dict())

    return jsonify({'message': 'Webhook processed', 'payment': payment.to_dict()}), 200


# ============================================================
# WALLET RECHARGE ROUTES
# ============================================================

@payment_bp.route('/wallet/recharge', methods=['POST'])
@jwt_required()
def create_wallet_recharge():
    """User submits a wallet recharge request with screenshot and transaction ID."""
    current_user_id = get_current_user_id()
    user = User.query.get(current_user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404

    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400

    amount = data.get('amount')
    transaction_id = str(data.get('transaction_id') or '').strip()
    screenshot_base64 = data.get('screenshot_base64')

    if not amount or not transaction_id or not screenshot_base64:
        return jsonify({'error': 'Amount, transaction ID, and screenshot are required'}), 400

    try:
        amount = float(amount)
    except (TypeError, ValueError):
        return jsonify({'error': 'Invalid amount'}), 400

    if amount <= 0 or amount > 50000:
        return jsonify({'error': 'Invalid amount (1-50000)'}), 400

    # Validate transaction ID: exactly 12 digits
    if not re.match(r'^[0-9]{12}$', transaction_id):
        return jsonify({'error': 'Transaction ID must contain exactly 12 digits.'}), 400

    # Check for duplicate transaction ID
    existing = WalletRecharge.query.filter_by(transaction_id=transaction_id).first()
    if existing:
        return jsonify({'error': 'This transaction ID has already been used'}), 409

    # Decode and validate screenshot
    try:
        encoded = screenshot_base64.split(',', 1)[1] if ',' in screenshot_base64 else screenshot_base64
        screenshot_data = base64.b64decode(encoded, validate=True)
    except Exception:
        return jsonify({'error': 'Screenshot is not valid base64'}), 400

    if not screenshot_data:
        return jsonify({'error': 'Screenshot is empty'}), 400
    if len(screenshot_data) > MAX_SCREENSHOT_BYTES:
        return jsonify({'error': 'Screenshot exceeds 5MB limit'}), 400
    if not screenshot_data.startswith(SCREENSHOT_MAGIC):
        return jsonify({'error': 'Screenshot must be a PNG, JPEG or GIF image'}), 400

    # Save screenshot
    folder = current_app.config['SCREENSHOT_FOLDER']
    try:
        os.makedirs(folder, exist_ok=True)
        extension = 'jpg' if screenshot_data.startswith(b'\xff\xd8\xff') else (
            'gif' if screenshot_data.startswith((b'GIF87a', b'GIF89a')) else (
                'webp' if screenshot_data.startswith(b'RIFF') else 'png'))
        screenshot_filename = f"recharge_{user.user_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{extension}"
        screenshot_path = os.path.join(folder, screenshot_filename)
        with open(screenshot_path, 'wb') as f:
            f.write(screenshot_data)
    except Exception as e:
        return jsonify({'error': f'Failed to save screenshot: {str(e)}'}), 500

    # Create recharge request
    recharge = WalletRecharge(
        recharge_id=f"RCH-{datetime.now().year}-{WalletRecharge.query.count() + 1:05d}",
        user_id=current_user_id,
        amount=amount,
        transaction_id=transaction_id,
        screenshot_file=screenshot_filename,
        status='pending_verification'
    )
    db.session.add(recharge)
    db.session.commit()

    # Notify admins
    notify_admins(
        ntype='wallet_recharge_verification',
        title='Wallet recharge awaiting verification',
        message=f"{user.full_name} submitted a wallet recharge of Rs.{amount:.2f} (TXN: {transaction_id}).",
        link='admin'
    )

    return jsonify({
        'message': 'Payment submitted successfully. Your wallet will be credited after admin verification.',
        'recharge': recharge.to_dict()
    }), 200


@payment_bp.route('/wallet/recharge/history', methods=['GET'])
@jwt_required()
def get_wallet_recharge_history():
    """Get user's wallet recharge request history."""
    current_user_id = get_current_user_id()
    user = User.query.get(current_user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404

    recharges = WalletRecharge.query.filter_by(user_id=current_user_id).order_by(WalletRecharge.created_at.desc()).all()

    return jsonify({
        'recharges': [r.to_dict() for r in recharges]
    }), 200


@payment_bp.route('/wallet/transactions', methods=['GET'])
@jwt_required()
def get_wallet_transactions():
    """Get user's wallet transaction history."""
    current_user_id = get_current_user_id()
    user = User.query.get(current_user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404

    transactions = WalletTransaction.query.filter_by(user_id=current_user_id).order_by(WalletTransaction.created_at.desc()).all()

    return jsonify({
        'transactions': [t.to_dict() for t in transactions]
    }), 200


# ============================================================
# ADMIN WALLET RECHARGE VERIFICATION ROUTES
# ============================================================

@payment_bp.route('/admin/wallet/recharges', methods=['GET'])
@jwt_required()
@admin_required
def admin_get_wallet_recharges():
    """Admin: Get all wallet recharge requests with filtering."""
    status = request.args.get('status')
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 20))

    query = WalletRecharge.query.order_by(WalletRecharge.created_at.desc())

    if status:
        query = query.filter_by(status=status)

    pagination = query.paginate(page=page, per_page=per_page, error_out=False)

    return jsonify({
        'recharges': [r.to_dict() for r in pagination.items],
        'pagination': {
            'page': page,
            'per_page': per_page,
            'total': pagination.total,
            'pages': pagination.pages
        }
    }), 200


@payment_bp.route('/admin/wallet/recharge/<int:recharge_id>', methods=['POST'])
@jwt_required()
@admin_required
def admin_verify_wallet_recharge(recharge_id):
    """Admin approves or rejects a wallet recharge request."""
    data = request.get_json() or {}
    action = data.get('action')  # 'approve' or 'reject'
    notes = str(data.get('notes') or '').strip()

    admin_user = User.query.get(get_current_user_id())

    recharge = WalletRecharge.query.get(recharge_id)
    if not recharge:
        return jsonify({'error': 'Recharge request not found'}), 404

    if recharge.status != 'pending_verification':
        return jsonify({
            'error': f'Recharge is not awaiting verification (current status: {recharge.status})'
        }), 409

    if action not in ('approve', 'reject'):
        return jsonify({'error': 'Invalid action. Use approve or reject'}), 400

    # Prevent admin from approving their own recharge request
    if admin_user and admin_user.id == recharge.user_id:
        return jsonify({'error': 'You cannot approve/reject your own recharge request'}), 403

    user = User.query.get(recharge.user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404

    if action == 'approve':
        # Check if already processed (idempotency)
        if recharge.status == 'approved':
            return jsonify({'error': 'This recharge has already been approved'}), 409

        # Use database transaction for atomic wallet credit
        try:
            balance_before = user.wallet_balance
            user.wallet_balance += recharge.amount
            balance_after = user.wallet_balance

            # Update recharge record
            recharge.status = 'approved'
            recharge.admin_id = admin_user.id if admin_user else None
            recharge.admin_notes = notes
            recharge.verified_at = utcnow()
            recharge.updated_at = utcnow()

            # Create wallet transaction record
            wallet_txn = WalletTransaction(
                transaction_id=f"WLT-{datetime.now().year}-{WalletTransaction.query.count() + 1:05d}",
                user_id=user.id,
                type='credit',
                amount=recharge.amount,
                balance_before=balance_before,
                balance_after=balance_after,
                description=f'Wallet recharge approved (TXN: {recharge.transaction_id})',
                reference_type='recharge',
                reference_id=recharge.id
            )
            db.session.add(wallet_txn)

            db.session.commit()

            # Notify user
            create_notification(
                user.id,
                ntype='wallet_recharge_approved',
                title='Wallet recharge approved',
                message=f"Your wallet recharge of Rs.{recharge.amount:.2f} has been approved. New balance: Rs.{balance_after:.2f}",
                link='dashboard'
            )

            message = 'Wallet recharge approved and amount credited'
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': f'Failed to process approval: {str(e)}'}), 500

    else:  # reject
        if not notes:
            return jsonify({'error': 'Rejection reason is required'}), 400

        recharge.status = 'rejected'
        recharge.admin_id = admin_user.id if admin_user else None
        recharge.rejected_reason = notes
        recharge.updated_at = utcnow()
        db.session.commit()

        create_notification(
            user.id,
            ntype='wallet_recharge_rejected',
            title='Wallet recharge rejected',
            message=f"Your wallet recharge of Rs.{recharge.amount:.2f} was rejected: {notes}",
            link='dashboard'
        )

        message = 'Wallet recharge rejected'

    return jsonify({
        'message': message,
        'recharge': recharge.to_dict()
    }), 200


@payment_bp.route('/admin/wallet/stats', methods=['GET'])
@jwt_required()
@admin_required
def admin_wallet_recharge_stats():
    """Admin: Get wallet recharge statistics."""
    from sqlalchemy import func

    total_pending = WalletRecharge.query.filter_by(status='pending_verification').count()
    total_approved = WalletRecharge.query.filter_by(status='approved').count()
    total_rejected = WalletRecharge.query.filter_by(status='rejected').count()
    total_amount_pending = db.session.query(func.sum(WalletRecharge.amount)).filter_by(status='pending_verification').scalar() or 0
    total_amount_approved = db.session.query(func.sum(WalletRecharge.amount)).filter_by(status='approved').scalar() or 0

    return jsonify({
        'pending_count': total_pending,
        'approved_count': total_approved,
        'rejected_count': total_rejected,
        'pending_amount': float(total_amount_pending),
        'approved_amount': float(total_amount_approved)
    }), 200