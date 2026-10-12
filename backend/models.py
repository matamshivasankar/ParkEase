from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta

from backend.utils.helpers import iso_utc
import uuid
import json

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.String(20), unique=True, nullable=False, index=True)
    full_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    phone = db.Column(db.String(10), nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), default='user', nullable=False)
    wallet_balance = db.Column(db.Float, default=0.0)
    is_verified = db.Column(db.Boolean, default=False)
    is_blocked = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)

    vehicles = db.relationship('Vehicle', backref='user', lazy=True, cascade='all, delete-orphan')
    bookings = db.relationship('Booking', backref='user', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def generate_user_id(self):
        count = User.query.count() + 1
        return f"PKR-{datetime.now().year}-{count:05d}"

    def to_dict(self, include_sensitive=False):
        data = {
            'id': self.id,
            'user_id': self.user_id,
            'full_name': self.full_name,
            'email': self.email,
            'phone': self.phone,
            'role': self.role,
            'wallet_balance': self.wallet_balance,
            'is_verified': self.is_verified,
            'is_blocked': self.is_blocked,
            'created_at': iso_utc(self.created_at),
            'last_login': iso_utc(self.last_login),
        }
        if include_sensitive:
            data['password_hash'] = self.password_hash
        return data


class Vehicle(db.Model):
    __tablename__ = 'vehicles'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    vehicle_no = db.Column(db.String(15), nullable=False)
    vehicle_type = db.Column(db.String(10), nullable=False)
    is_default = db.Column(db.Boolean, default=False)

    __table_args__ = (db.UniqueConstraint('user_id', 'vehicle_no', name='unique_user_vehicle'),)

    def to_dict(self):
        return {
            'id': self.id,
            'vehicle_no': self.vehicle_no,
            'vehicle_type': self.vehicle_type,
            'is_default': self.is_default
        }


class Facility(db.Model):
    __tablename__ = 'facilities'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    facility_id = db.Column(db.String(20), unique=True, nullable=False, index=True)
    name = db.Column(db.String(100), nullable=False)
    street = db.Column(db.String(200), nullable=False)
    area = db.Column(db.String(100), nullable=False)
    city = db.Column(db.String(50), nullable=False, index=True)
    pincode = db.Column(db.String(10), nullable=False)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    total_car = db.Column(db.Integer, default=0)
    total_bike = db.Column(db.Integer, default=0)
    total_truck = db.Column(db.Integer, default=0)
    total_ev = db.Column(db.Integer, default=0)
    available_car = db.Column(db.Integer, default=0)
    available_bike = db.Column(db.Integer, default=0)
    available_truck = db.Column(db.Integer, default=0)
    available_ev = db.Column(db.Integer, default=0)
    rate_car_hourly = db.Column(db.Float, default=40)
    rate_bike_hourly = db.Column(db.Float, default=30)
    rate_truck_hourly = db.Column(db.Float, default=60)
    rate_ev_hourly = db.Column(db.Float, default=35)
    monthly_car = db.Column(db.Float, default=8000)
    monthly_bike = db.Column(db.Float, default=5000)
    monthly_truck = db.Column(db.Float, default=12000)
    monthly_ev = db.Column(db.Float, default=6500)
    amenities = db.Column(db.Text)
    open_time = db.Column(db.String(10), default='06:00')
    close_time = db.Column(db.String(10), default='23:00')
    rating = db.Column(db.Float, default=0.0)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    slots = db.relationship('Slot', backref='facility', lazy=True, cascade='all, delete-orphan')
    bookings = db.relationship('Booking', backref='facility', lazy=True)

    def get_available_count(self, vehicle_type):
        field = f'available_{vehicle_type.lower()}'
        return getattr(self, field, 0)

    def get_total_count(self, vehicle_type):
        field = f'total_{vehicle_type.lower()}'
        return getattr(self, field, 0)

    def get_hourly_rate(self, vehicle_type):
        field = f'rate_{vehicle_type.lower()}_hourly'
        return getattr(self, field, 0)

    def get_monthly_rate(self, vehicle_type):
        field = f'monthly_{vehicle_type.lower()}'
        return getattr(self, field, 0)

    def get_amenities_list(self):
        if self.amenities:
            try:
                return json.loads(self.amenities)
            except:
                return []
        return []

    def sync_availability(self):
        """Recalculate available slot counts from the Slot table.

        This ensures the denormalized available_xxx fields stay in sync with
        the actual Slot.is_occupied state. Call after booking changes.
        """
        from backend.models import Slot
        counts = {v: 0 for v in ['car', 'bike', 'truck', 'ev']}
        for slot in self.slots:
            if not slot.is_occupied:
                key = slot.vehicle_type.lower()
                if key in counts:
                    counts[key] += 1

        self.available_car = counts['car']
        self.available_bike = counts['bike']
        self.available_truck = counts['truck']
        self.available_ev = counts['ev']

    def to_dict(self, include_slots=False):
        data = {
            'id': self.id,
            'facility_id': self.facility_id,
            'name': self.name,
            'street': self.street,
            'area': self.area,
            'city': self.city,
            'pincode': self.pincode,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'total_slots': {
                'Car': self.total_car,
                'Bike': self.total_bike,
                'Truck': self.total_truck,
                'EV': self.total_ev
            },
            'available_slots': {
                'Car': self.available_car,
                'Bike': self.available_bike,
                'Truck': self.available_truck,
                'EV': self.available_ev
            },
            'rates': {
                'hourly': {
                    'Car': self.rate_car_hourly,
                    'Bike': self.rate_bike_hourly,
                    'Truck': self.rate_truck_hourly,
                    'EV': self.rate_ev_hourly
                },
                'monthly': {
                    'Car': self.monthly_car,
                    'Bike': self.monthly_bike,
                    'Truck': self.monthly_truck,
                    'EV': self.monthly_ev
                }
            },
            'amenities': self.get_amenities_list(),
            'open_time': self.open_time,
            'close_time': self.close_time,
            'rating': self.rating,
            'is_active': self.is_active
        }
        if include_slots:
            data['slots'] = [slot.to_dict() for slot in self.slots if slot.vehicle_type in ['Car', 'Bike', 'Truck', 'EV']]
        return data


class Slot(db.Model):
    __tablename__ = 'slots'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    facility_id = db.Column(db.Integer, db.ForeignKey('facilities.id'), nullable=False)
    slot_code = db.Column(db.String(10), nullable=False)
    vehicle_type = db.Column(db.String(10), nullable=False)
    is_occupied = db.Column(db.Boolean, default=False)
    occupied_until = db.Column(db.DateTime)

    __table_args__ = (db.UniqueConstraint('facility_id', 'slot_code', name='unique_facility_slot'),)

    def to_dict(self):
        return {
            'id': self.id,
            'slot_code': self.slot_code,
            'vehicle_type': self.vehicle_type,
            'is_occupied': self.is_occupied,
            'occupied_until': iso_utc(self.occupied_until)
        }

    def is_available(self, start_time=None, end_time=None):
        if not self.is_occupied:
            return True
        if self.occupied_until and start_time:
            return self.occupied_until <= start_time
        return False


class BookingVehicle(db.Model):
    """One vehicle number per booked slot.

    `Booking.vehicle_no` holds the primary (first) vehicle for backwards
    compatibility, but a booking can cover several slots, so the full set is
    stored here as one row per slot.
    """
    __tablename__ = 'booking_vehicles'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    booking_id = db.Column(db.Integer, db.ForeignKey('bookings.id'), nullable=False, index=True)
    slot_code = db.Column(db.String(10), nullable=False)
    vehicle_no = db.Column(db.String(15), nullable=False)
    vehicle_type = db.Column(db.String(10), nullable=False)

    def to_dict(self):
        return {
            'slot_code': self.slot_code,
            'vehicle_no': self.vehicle_no,
            'vehicle_type': self.vehicle_type
        }


class Booking(db.Model):
    __tablename__ = 'bookings'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    booking_id = db.Column(db.String(20), unique=True, nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    facility_id = db.Column(db.Integer, db.ForeignKey('facilities.id'), nullable=False)
    slot_ids = db.Column(db.Text, nullable=False)
    vehicle_no = db.Column(db.String(15), nullable=False)
    vehicle_type = db.Column(db.String(10), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)
    duration_value = db.Column(db.Integer, nullable=False)
    duration_unit = db.Column(db.String(10), nullable=False)
    base_price = db.Column(db.Float, nullable=False)
    discount = db.Column(db.Float, default=0.0)
    discount_reason = db.Column(db.String(100))
    gst = db.Column(db.Float, default=0.0)
    total_amount = db.Column(db.Float, nullable=False)
    payment_status = db.Column(db.String(20), default='pending')
    payment_method = db.Column(db.String(20))
    transaction_id = db.Column(db.String(50))
    paid_at = db.Column(db.DateTime)
    status = db.Column(db.String(20), default='reserved')
    qr_code = db.Column(db.Text)
    check_in_time = db.Column(db.DateTime)
    check_out_time = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    booking_vehicles = db.relationship(
        'BookingVehicle', backref='booking', lazy=True, cascade='all, delete-orphan'
    )

    def generate_booking_id(self):
        count = Booking.query.count() + 1
        return f"BKG-{datetime.now().year}-{count:05d}"

    def get_slot_codes(self):
        try:
            return json.loads(self.slot_ids)
        except:
            return []

    def set_slot_codes(self, codes):
        self.slot_ids = json.dumps(codes)

    def set_vehicles(self, slot_codes, vehicles):
        """Replace the vehicle-per-slot rows for this booking.

        `vehicles` is a list of vehicle numbers positionally matched to
        `slot_codes`, so slot i is driven by vehicle i.
        """
        self.booking_vehicles.clear()
        for slot_code, vehicle_no in zip(slot_codes, vehicles):
            self.booking_vehicles.append(BookingVehicle(
                slot_code=slot_code,
                vehicle_no=vehicle_no,
                vehicle_type=self.vehicle_type
            ))
        self.vehicle_no = vehicles[0]

    def get_vehicles(self):
        """Vehicle-per-slot rows ordered the same way as get_slot_codes()."""
        by_slot = {v.slot_code: v.vehicle_no for v in self.booking_vehicles}
        return [by_slot.get(code, self.vehicle_no) for code in self.get_slot_codes()]

    def calculate_duration_hours(self):
        if self.duration_unit == 'hours':
            return self.duration_value
        elif self.duration_unit == 'days':
            return self.duration_value * 24
        elif self.duration_unit == 'monthly':
            return self.duration_value * 24 * 30
        return self.duration_value

    def to_dict(self, include_slots=True):
        data = {
            'id': self.id,
            'booking_id': self.booking_id,
            'user_id': self.user_id,
            'facility_id': self.facility_id,
            'vehicle_no': self.vehicle_no,
            'vehicle_type': self.vehicle_type,
            'start_time': iso_utc(self.start_time),
            'end_time': iso_utc(self.end_time),
            'duration_value': self.duration_value,
            'duration_unit': self.duration_unit,
            'base_price': self.base_price,
            'discount': self.discount,
            'discount_reason': self.discount_reason,
            'gst': self.gst,
            'total_amount': self.total_amount,
            'payment_status': self.payment_status,
            'payment_method': self.payment_method,
            'transaction_id': self.transaction_id,
            'paid_at': iso_utc(self.paid_at),
            'status': self.status,
            'qr_code': self.qr_code,
            'check_in_time': iso_utc(self.check_in_time),
            'check_out_time': iso_utc(self.check_out_time),
            'created_at': iso_utc(self.created_at),
        }
        if include_slots:
            data['slot_codes'] = self.get_slot_codes()
            data['vehicles'] = self.get_vehicles()
        return data


class Notification(db.Model):
    """In-app notification delivered to a single user.

    `ntype` drives the icon/colour in the UI and the link is a view name the
    frontend can navigate to (e.g. 'admin', 'dashboard').
    """
    __tablename__ = 'notifications'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    ntype = db.Column(db.String(30), nullable=False, default='info')
    title = db.Column(db.String(120), nullable=False)
    message = db.Column(db.Text)
    link = db.Column(db.String(60))
    is_read = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'type': self.ntype,
            'title': self.title,
            'message': self.message,
            'link': self.link,
            'is_read': self.is_read,
            'created_at': iso_utc(self.created_at)
        }


class Payment(db.Model):
    __tablename__ = 'payments'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    payment_id = db.Column(db.String(20), unique=True, nullable=False, index=True)
    booking_id = db.Column(db.Integer, db.ForeignKey('bookings.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    method = db.Column(db.String(20), nullable=False)
    status = db.Column(db.String(20), default='pending')
    transaction_id = db.Column(db.String(50))
    gateway_response = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    paid_at = db.Column(db.DateTime)

    booking = db.relationship('Booking', backref='payments')
    user = db.relationship('User', backref='payments')

    def generate_payment_id(self):
        count = Payment.query.count() + 1
        return f"PAY-{datetime.now().year}-{count:05d}"

    def to_dict(self):
        return {
            'id': self.id,
            'payment_id': self.payment_id,
            'booking_id': self.booking_id,
            'user_id': self.user_id,
            'amount': self.amount,
            'method': self.method,
            'status': self.status,
            'transaction_id': self.transaction_id,
            'gateway_response': self.gateway_response,
            'created_at': iso_utc(self.created_at),
            'paid_at': iso_utc(self.paid_at)
        }


def init_db(app):
    db.init_app(app)
    with app.app_context():
        db.create_all()