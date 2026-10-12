"""Booking state transitions that have to happen on their own.

A booking that was checked in and whose end time has now passed must become
`completed` and hand its slots back to the pool, but no request is guaranteed
to arrive at that exact moment. Instead of running a background scheduler, the
sweep is triggered lazily by the reads whose results depend on it, so the state
is correct by the time anyone looks at it.
"""
from flask import current_app

from backend.models import db, Booking, Slot
from backend.utils.helpers import utcnow
from backend.utils.notifier import create_notification


def _emit(event, data, room):
    """Push a SocketIO event, ignoring the case where SocketIO is not running."""
    try:
        socketio = current_app.extensions.get('socketio')
        if socketio:
            socketio.emit(event, data, room=room)
    except Exception:
        pass


def complete_expired_bookings(user_ids=None):
    """Complete every checked-in booking whose end time has passed.

    Pass user_ids to sweep only those owners' bookings, which is what the
    per-user booking list wants. Returns the bookings that were transitioned.
    """
    now = utcnow()

    query = Booking.query.filter(
        Booking.status == 'active',
        Booking.check_in_time.isnot(None),
        Booking.end_time <= now,
    )
    if user_ids is not None:
        if isinstance(user_ids, int):
            user_ids = [user_ids]
        if not user_ids:
            return []
        query = query.filter(Booking.user_id.in_(user_ids))

    expired = query.all()
    if not expired:
        return []

    for booking in expired:
        # Record when the slot was actually released, not the end time we would
        # have preferred, so an overstay stays visible in the receipt.
        booking.check_out_time = now
        booking.status = 'completed'

        for slot_code in booking.get_slot_codes():
            slot = Slot.query.filter_by(
                facility_id=booking.facility_id, slot_code=slot_code
            ).first()
            if slot:
                slot.is_occupied = False
                slot.occupied_until = None

        create_notification(
            booking.user_id,
            'booking_completed',
            'Parking completed',
            f'Your parking for booking {booking.booking_id} has ended and the slot is free again.',
            'dashboard',
        )

    db.session.commit()

    for booking in expired:
        _emit('booking_updated', booking.to_dict(), room=f'booking_{booking.id}')

    return expired