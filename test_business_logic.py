"""Tests for ParkEase core business logic."""

import pytest
from datetime import datetime, timedelta, timezone

from backend.app import create_app
from backend.models import db, User, Facility, Slot, Booking, Vehicle, Payment
from backend.utils.helpers import (calculate_price, lock_slots_for_booking,
                                   release_slots, utcnow, parse_client_datetime,
                                   iso_utc, generate_booking_id)
from backend.utils.validators import validate_registration, validate_login, validate_vehicle


@pytest.fixture
def app():
    app = create_app('testing')
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def db_session(app):
    with app.app_context():
        yield db.session


def create_sample_facility(db_session):
    """Create a facility with slots within an active session."""
    facility = Facility(
        facility_id='FAC-TEST-01',
        name='Test Facility',
        street='123 Test St',
        area='Test Area',
        city='Test City',
        pincode='123456',
        latitude=12.9716,
        longitude=77.5946,
        total_car=10,
        total_bike=20,
        available_car=10,
        available_bike=20,
        rate_car_hourly=40,
        rate_bike_hourly=30,
    )
    db_session.add(facility)
    db_session.flush()

    for i in range(1, 11):
        db_session.add(Slot(facility_id=facility.id, slot_code=f'C{i}', vehicle_type='Car'))
    for i in range(1, 21):
        db_session.add(Slot(facility_id=facility.id, slot_code=f'B{i}', vehicle_type='Bike'))

    db_session.commit()
    return facility


def create_sample_user(db_session):
    """Create a user within an active session."""
    user = User(
        user_id='PKR-2024-00001',
        full_name='Test User',
        email='test@example.com',
        phone='9876543210',
        role='user'
    )
    user.set_password('Test@123')
    db_session.add(user)
    db_session.commit()
    return user


class TestPriceCalculation:
    """Test price calculation with various scenarios."""

    def test_hourly_booking_car(self, db_session):
        facility = create_sample_facility(db_session)
        start = utcnow() + timedelta(hours=1)
        price = calculate_price(
            facility=facility,
            vehicle_type='Car',
            duration_value=2,
            duration_unit='hours',
            start_time=start,
            slot_count=1
        )
        assert price['base_price'] == 80
        assert price['total_amount'] > price['base_price']

    def test_multiple_slots(self, db_session):
        facility = create_sample_facility(db_session)
        start = utcnow() + timedelta(hours=1)
        price = calculate_price(
            facility=facility,
            vehicle_type='Car',
            duration_value=1,
            duration_unit='hours',
            start_time=start,
            slot_count=3
        )
        assert price['base_price'] == 120

    def test_weekly_discount(self, db_session):
        facility = create_sample_facility(db_session)
        start = utcnow() + timedelta(hours=1)
        while start.weekday() >= 5:
            start += timedelta(days=1)
        price = calculate_price(
            facility=facility,
            vehicle_type='Car',
            duration_value=7,
            duration_unit='days',
            start_time=start,
            slot_count=1
        )
        assert price['discount'] > 0
        assert 'Weekly discount' in (price['discount_reason'] or '')

    def test_weekend_discount(self, db_session):
        facility = create_sample_facility(db_session)
        start = utcnow() + timedelta(hours=1)
        while start.weekday() < 5:
            start += timedelta(days=1)
        price = calculate_price(
            facility=facility,
            vehicle_type='Car',
            duration_value=2,
            duration_unit='hours',
            start_time=start,
            slot_count=1
        )
        assert price['discount'] > 0
        assert 'Weekend discount' in (price['discount_reason'] or '')

    def test_early_bird_discount(self, db_session):
        facility = create_sample_facility(db_session)
        # Early bird is based on LOCAL time (Asia/Kolkata = UTC+5:30)
        # 8:00 IST = 02:30 UTC
        start = utcnow().replace(hour=2, minute=30, second=0, microsecond=0)
        if start <= utcnow():
            start += timedelta(days=1)
        price = calculate_price(
            facility=facility,
            vehicle_type='Car',
            duration_value=2,
            duration_unit='hours',
            start_time=start,
            slot_count=1
        )
        assert price['discount'] > 0
        assert 'Early bird discount' in (price['discount_reason'] or '')

    def test_monthly_booking(self, db_session):
        facility = create_sample_facility(db_session)
        start = utcnow() + timedelta(hours=1)
        price = calculate_price(
            facility=facility,
            vehicle_type='Car',
            duration_value=1,
            duration_unit='monthly',
            start_time=start,
            slot_count=1
        )
        assert price['base_price'] == facility.monthly_car


class TestSlotLocking:
    """Test slot locking mechanism."""

    def test_lock_slots_success(self, db_session):
        facility = create_sample_facility(db_session)
        slots = Slot.query.filter_by(facility_id=facility.id, vehicle_type='Car').limit(2).all()
        end_time = utcnow() + timedelta(hours=2)

        success, result = lock_slots_for_booking(
            slot_codes=[s.slot_code for s in slots],
            facility_id=facility.id,
            vehicle_type='Car',
            start_time=utcnow() + timedelta(hours=1),
            end_time=end_time
        )
        assert success is True
        assert len(result) == 2

    def test_lock_slots_conflict(self, db_session):
        facility = create_sample_facility(db_session)
        slot = Slot.query.filter_by(facility_id=facility.id, vehicle_type='Car').first()
        end_time = utcnow() + timedelta(hours=2)

        lock_slots_for_booking(
            slot_codes=[slot.slot_code],
            facility_id=facility.id,
            vehicle_type='Car',
            start_time=utcnow() + timedelta(hours=1),
            end_time=end_time
        )

        success, msg = lock_slots_for_booking(
            slot_codes=[slot.slot_code],
            facility_id=facility.id,
            vehicle_type='Car',
            start_time=utcnow() + timedelta(minutes=30),
            end_time=end_time
        )
        assert success is False
        assert 'not available' in msg.lower()

    def test_release_slots(self, db_session):
        facility = create_sample_facility(db_session)
        slots = Slot.query.filter_by(facility_id=facility.id, vehicle_type='Car').limit(2).all()
        slot_codes = [s.slot_code for s in slots]

        lock_slots_for_booking(
            slot_codes=slot_codes,
            facility_id=facility.id,
            vehicle_type='Car',
            start_time=utcnow() + timedelta(hours=1),
            end_time=utcnow() + timedelta(hours=3)
        )
        release_slots(slot_codes, facility_id=facility.id)

        for slot in Slot.query.filter(Slot.slot_code.in_(slot_codes)).all():
            assert slot.is_occupied is False
            assert slot.occupied_until is None


class TestBookingValidation:
    """Test booking validation logic."""

    def test_vehicle_number_per_slot(self):
        from backend.routes.booking_routes import _resolve_vehicle_numbers

        vehicles, err = _resolve_vehicle_numbers({'vehicle_nos': ['MH12AB1234', 'MH12CD5678']}, ['C1', 'C2'])
        assert err is None
        assert len(vehicles) == 2

        vehicles, err = _resolve_vehicle_numbers({'vehicle_nos': ['MH12AB1234']}, ['C1', 'C2'])
        assert err is not None
        assert 'vehicle number' in err.lower()

        vehicles, err = _resolve_vehicle_numbers({'vehicle_nos': ['MH12AB1234', 'MH12AB1234']}, ['C1', 'C2'])
        assert err is not None
        assert 'duplicate' in err.lower()

        vehicles, err = _resolve_vehicle_numbers({'vehicle_nos': ['MH12AB1234', '']}, ['C1', 'C2'])
        assert err is not None
        assert 'vehicle number' in err.lower()


class TestValidators:
    """Test input validators."""

    def test_validate_registration_valid(self):
        data = {
            'full_name': 'Test User',
            'email': 'test@example.com',
            'phone': '9876543210',
            'password': 'Test@123'
        }
        assert validate_registration(data) is None

    def test_validate_registration_invalid_email(self):
        data = {
            'full_name': 'Test User',
            'email': 'invalid-email',
            'phone': '9876543210',
            'password': 'Test@123'
        }
        assert validate_registration(data) is not None

    def test_validate_registration_weak_password(self):
        data = {
            'full_name': 'Test User',
            'email': 'test@example.com',
            'phone': '9876543210',
            'password': 'weak'
        }
        assert validate_registration(data) is not None

    def test_validate_login_valid(self):
        data = {'email': 'test@example.com', 'password': 'Test@123'}
        assert validate_login(data) is None

    def test_validate_login_missing_fields(self):
        assert validate_login({'email': 'test@example.com'}) is not None
        assert validate_login({'password': 'Test@123'}) is not None
        assert validate_login({}) is not None

    def test_validate_vehicle_valid(self):
        assert validate_vehicle({'vehicle_no': 'MH12AB1234', 'vehicle_type': 'Car'}) is None
        assert validate_vehicle({'vehicle_no': 'MH12AB1234', 'vehicle_type': 'Bike'}) is None

    def test_validate_vehicle_invalid_type(self):
        assert validate_vehicle({'vehicle_no': 'MH12AB1234', 'vehicle_type': 'Invalid'}) is not None

    def test_validate_vehicle_missing_number(self):
        assert validate_vehicle({'vehicle_type': 'Car'}) is not None


class TestDateTimeHelpers:
    """Test datetime parsing and formatting."""

    def test_parse_client_datetime_iso_with_z(self):
        dt = parse_client_datetime('2024-01-15T10:30:00.000Z')
        assert dt.tzinfo is None
        assert dt.hour == 10
        assert dt.minute == 30

    def test_parse_client_datetime_iso_with_offset(self):
        dt = parse_client_datetime('2024-01-15T10:30:00+05:30')
        assert dt.tzinfo is None
        assert dt.hour == 5

    def test_iso_utc_formatting(self):
        dt = datetime(2024, 1, 15, 10, 30, 0)
        result = iso_utc(dt)
        assert result.endswith('Z')
        assert '2024-01-15T10:30:00' in result

    def test_utcnow_returns_naive_utc(self):
        now = utcnow()
        assert now.tzinfo is None
        assert abs((now - datetime.now(timezone.utc).replace(tzinfo=None)).total_seconds()) < 5


class TestFacilityAvailabilitySync:
    """Test that facility availability stays in sync with slots."""

    def test_sync_availability(self, db_session):
        facility = create_sample_facility(db_session)
        facility.sync_availability()
        assert facility.available_car == 10
        assert facility.available_bike == 20

        car_slots = Slot.query.filter_by(facility_id=facility.id, vehicle_type='Car').limit(3).all()
        for slot in car_slots:
            slot.is_occupied = True
            slot.occupied_until = utcnow() + timedelta(hours=2)
        db_session.commit()

        facility.sync_availability()
        db_session.commit()
        assert facility.available_car == 7
        assert facility.available_bike == 20


class TestAuthFlow:
    """Test authentication flow."""

    def test_register_login_logout(self, client, db_session):
        # Register
        resp = client.post('/api/auth/register', json={
            'full_name': 'New User',
            'email': 'newuser@example.com',
            'phone': '9123456789',
            'password': 'Test@123'
        })
        assert resp.status_code == 201
        data = resp.get_json()
        assert 'access_token' in data
        assert data['user']['email'] == 'newuser@example.com'

        # Login
        resp = client.post('/api/auth/login', json={
            'email': 'newuser@example.com',
            'password': 'Test@123'
        })
        assert resp.status_code == 200
        login_data = resp.get_json()
        assert 'access_token' in login_data

        # Verify token
        resp = client.get('/api/auth/verify', headers={
            'Authorization': f"Bearer {login_data['access_token']}"
        })
        assert resp.status_code == 200

        # Logout
        resp = client.post('/api/auth/logout', headers={
            'Authorization': f"Bearer {login_data['access_token']}"
        })
        assert resp.status_code == 200


class TestBookingFlow:
    """Test complete booking flow."""

    def test_create_booking(self, client, db_session):
        # Create user and facility in session
        user = create_sample_user(db_session)
        facility = create_sample_facility(db_session)

        # Login
        login_resp = client.post('/api/auth/login', json={
            'email': 'test@example.com',
            'password': 'Test@123'
        })
        assert login_resp.status_code == 200
        token = login_resp.get_json()['access_token']

        # Create booking
        start = utcnow() + timedelta(hours=1)
        end = start + timedelta(hours=2)
        resp = client.post('/api/bookings', json={
            'facility_id': facility.id,
            'vehicle_type': 'Car',
            'start_time': start.isoformat() + 'Z',
            'end_time': end.isoformat() + 'Z',
            'duration_value': 2,
            'duration_unit': 'hours',
            'slot_codes': ['C1'],
            'vehicle_nos': ['MH12AB1234']
        }, headers={'Authorization': f'Bearer {token}'})

        assert resp.status_code == 201
        data = resp.get_json()
        assert 'booking' in data
        assert data['booking']['status'] == 'reserved'

    def test_price_estimate(self, client, db_session):
        facility = create_sample_facility(db_session)
        start = utcnow() + timedelta(hours=1)
        resp = client.post('/api/bookings/price-estimate', json={
            'facility_id': facility.id,
            'vehicle_type': 'Car',
            'duration_value': 2,
            'duration_unit': 'hours',
            'start_time': start.isoformat() + 'Z',
            'slot_count': 1
        })
        assert resp.status_code == 200
        data = resp.get_json()
        assert 'price_breakdown' in data
        assert data['price_breakdown']['total_amount'] > 0


if __name__ == '__main__':
    pytest.main([__file__, '-v'])