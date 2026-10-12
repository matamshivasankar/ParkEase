from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo
from backend.config import Config
import json


def utcnow():
    """Current time as a naive UTC datetime.

    Everything persisted in the database is naive UTC, so every comparison must
    use this instead of datetime.utcnow() (deprecated) or datetime.now()
    (naive local time, which silently breaks once the host is not on UTC).
    """
    return datetime.now(timezone.utc).replace(tzinfo=None)


def parse_client_datetime(value):
    """Parse an ISO-8601 string from the browser into a naive UTC datetime.

    The frontend sends `Date.prototype.toISOString()` output, which is UTC with
    a trailing 'Z'. Naive values are assumed to already be UTC. Aware values are
    converted to UTC and the tzinfo is dropped so results stay comparable with
    the naive values stored in the database.
    """
    if isinstance(value, datetime):
        parsed = value
    else:
        text = str(value).strip()
        if text.endswith(('Z', 'z')):
            text = text[:-1] + '+00:00'
        parsed = datetime.fromisoformat(text)

    if parsed.tzinfo is not None:
        parsed = parsed.astimezone(timezone.utc).replace(tzinfo=None)
    return parsed


def to_local(value):
    """Convert a naive UTC datetime to the configured local timezone."""
    local_tz = ZoneInfo(Config.LOCAL_TIMEZONE)
    return value.replace(tzinfo=timezone.utc).astimezone(local_tz)


def iso_utc(value):
    """Serialise a stored naive-UTC datetime for the browser.

    Values are persisted without a timezone, so they must be tagged as UTC on
    the way out. Without the 'Z' suffix `new Date(...)` in the browser treats
    them as local time and renders every timestamp shifted by the UTC offset.
    """
    if value is None:
        return None
    return value.replace(tzinfo=timezone.utc).isoformat().replace('+00:00', 'Z')


def calculate_price(facility, vehicle_type, duration_value, duration_unit, start_time, slot_count=1):
    """Price one booking.

    `slot_count` scales the base price because a booking covering N slots means
    N vehicles parked for the whole window, not one.
    """
    hourly_rate = facility.get_hourly_rate(vehicle_type)
    monthly_rate = facility.get_monthly_rate(vehicle_type)
    slot_count = max(1, int(slot_count or 1))

    if duration_unit == 'hours':
        base_price = hourly_rate * duration_value * slot_count
    elif duration_unit == 'days':
        base_price = hourly_rate * 24 * duration_value * slot_count
    elif duration_unit == 'monthly':
        base_price = monthly_rate * duration_value * slot_count
    else:
        base_price = hourly_rate * duration_value * slot_count

    discount = 0.0
    discount_reasons = []

    # Discount rules are business rules, so evaluate them in local park time
    # rather than UTC (a 09:00 IST start is 03:30 UTC and would be mispriced).
    local_start = to_local(start_time)

    if duration_unit == 'days' and duration_value >= 7:
        discount += base_price * Config.DISCOUNTS['weekly']
        discount_reasons.append('Weekly discount (10%)')

    if duration_unit == 'monthly':
        discount += base_price * Config.DISCOUNTS['monthly']
        discount_reasons.append('Monthly subscription (20%)')

    if local_start.weekday() >= 5:
        discount += base_price * Config.DISCOUNTS['weekend']
        discount_reasons.append('Weekend discount (15%)')

    if local_start.hour < 9:
        discount += base_price * Config.DISCOUNTS['early_bird']
        discount_reasons.append('Early bird discount (5%)')

    discount = round(min(discount, base_price * 0.5), 2)
    discounted_price = base_price - discount
    gst = round(discounted_price * Config.GST_RATE, 2)
    total_amount = round(discounted_price + gst, 2)

    return {
        'base_price': round(base_price, 2),
        'discount': discount,
        'discount_reason': '; '.join(discount_reasons) if discount_reasons else None,
        'gst': gst,
        'total_amount': total_amount,
        'hourly_rate': hourly_rate,
        'monthly_rate': monthly_rate,
        'slot_count': slot_count
    }


def generate_booking_id():
    from backend.models import Booking
    count = Booking.query.count() + 1
    return f"BKG-{datetime.now().year}-{count:05d}"


def lock_slots(slots, end_time):
    """Lock slots for booking using SELECT FOR UPDATE to prevent race conditions.

    This must be called within a database transaction. The slots are marked as
    occupied with the booking's end_time so they won't be available for other
    bookings overlapping this time range.
    """
    try:
        for slot in slots:
            slot.is_occupied = True
            slot.occupied_until = end_time
        return True
    except Exception:
        return False


def release_slots(slot_codes, facility_id=None):
    """Free held slots.

    `facility_id` must be supplied: slot codes like 'C1' repeat across
    facilities, so filtering on the code alone frees the same code everywhere.
    """
    from backend.models import Slot
    if not slot_codes:
        return True
    try:
        query = Slot.query.filter(Slot.slot_code.in_(slot_codes))
        if facility_id is not None:
            query = query.filter(Slot.facility_id == facility_id)
        for slot in query.all():
            slot.is_occupied = False
            slot.occupied_until = None
        return True
    except Exception:
        return False


def lock_slots_for_booking(slot_codes, facility_id, vehicle_type, start_time, end_time):
    """Atomically lock slots for a new booking using SELECT FOR UPDATE.

    Returns (success, slots_or_error_message).
    On success, returns (True, list_of_locked_slot_objects).
    On failure, returns (False, error_message).
    """
    from backend.models import Slot, db
    try:
        # Use SELECT FOR UPDATE to lock the rows and prevent concurrent modifications
        slots = Slot.query.filter(
            Slot.facility_id == facility_id,
            Slot.slot_code.in_(slot_codes),
            Slot.vehicle_type == vehicle_type
        ).with_for_update(nowait=True).all()

        if len(slots) != len(slot_codes):
            return False, f'One or more slots not found (found {len(slots)} of {len(slot_codes)})'

        for slot in slots:
            if not slot.is_available(start_time, end_time):
                return False, f'Slot {slot.slot_code} is not available for the selected time'

        # All slots available - lock them
        for slot in slots:
            slot.is_occupied = True
            slot.occupied_until = end_time

        db.session.flush()
        return True, slots

    except Exception as e:
        # Could be a lock timeout (nowait) or other DB error
        return False, 'Could not lock slots - they may be booked by another user. Please try again.'


def format_currency(amount):
    return f"₹{amount:,.2f}"


def get_vehicle_type_display(vtype):
    displays = {'Car': '🚗 Car', 'Bike': '🏍️ Bike', 'Truck': '🚛 Truck', 'EV': '🔋 EV'}
    return displays.get(vtype, vtype)


def get_status_badge_class(status):
    classes = {
        'reserved': 'badge-warning',
        'confirmed': 'badge-success',
        'active': 'badge-success',
        'completed': 'badge-info',
        'cancelled': 'badge-danger',
        'pending': 'badge-warning',
        'paid': 'badge-success',
        'refunded': 'badge-info',
        'failed': 'badge-danger'
    }
    return classes.get(status, 'badge-secondary')