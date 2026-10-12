from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from backend.utils.helpers import parse_client_datetime
from sqlalchemy import or_, and_, func
from math import radians, cos, sin, sqrt, atan2

from backend.models import db, Facility, Slot
from backend.middleware.auth_middleware import admin_required

facility_bp = Blueprint('facilities', __name__, url_prefix='/api/facilities')


def haversine(lat1, lon1, lat2, lon2):
    R = 6371
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    return R * c


@facility_bp.route('', methods=['GET'])
def get_facilities():
    city = request.args.get('city')
    vehicle_type = request.args.get('vehicle_type')
    q = request.args.get('q', '').strip()
    min_price = request.args.get('min_price', type=float)
    max_price = request.args.get('max_price', type=float)
    latitude = request.args.get('latitude', type=float)
    longitude = request.args.get('longitude', type=float)
    radius = request.args.get('radius', type=float, default=10)
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 20))

    query = Facility.query.filter_by(is_active=True)

    if q:
        query = query.filter(
            or_(
                Facility.name.ilike(f'%{q}%'),
                Facility.area.ilike(f'%{q}%'),
                Facility.city.ilike(f'%{q}%'),
                Facility.street.ilike(f'%{q}%')
            )
        )

    if city:
        query = query.filter(Facility.city.ilike(f'%{city}%'))

    if vehicle_type:
        available_field = f'available_{vehicle_type.lower()}'
        if hasattr(Facility, available_field):
            query = query.filter(getattr(Facility, available_field) > 0)

    if min_price is not None or max_price is not None:
        pass

    if latitude and longitude:
        all_facilities = query.all()
        filtered = []
        for f in all_facilities:
            dist = haversine(latitude, longitude, f.latitude, f.longitude)
            if dist <= radius:
                f.distance = round(dist, 2)
                filtered.append(f)
        filtered.sort(key=lambda x: x.distance)
        total = len(filtered)
        start = (page - 1) * per_page
        end = start + per_page
        facilities = filtered[start:end]
        return jsonify({
            'facilities': [f.to_dict() for f in facilities],
            'pagination': {'page': page, 'per_page': per_page, 'total': total, 'pages': (total + per_page - 1) // per_page}
        }), 200

    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    return jsonify({
        'facilities': [f.to_dict() for f in pagination.items],
        'pagination': {
            'page': page,
            'per_page': per_page,
            'total': pagination.total,
            'pages': pagination.pages
        }
    }), 200


@facility_bp.route('/<int:facility_id>', methods=['GET'])
def get_facility(facility_id):
    facility = Facility.query.get(facility_id)
    if not facility:
        return jsonify({'error': 'Facility not found'}), 404

    return jsonify({'facility': facility.to_dict(include_slots=True)}), 200


@facility_bp.route('/search', methods=['GET'])
def search_facilities():
    q = request.args.get('q', '').strip()
    if not q:
        return jsonify({'error': 'Search query required'}), 400

    query = Facility.query.filter_by(is_active=True).filter(
        or_(
            Facility.name.ilike(f'%{q}%'),
            Facility.area.ilike(f'%{q}%'),
            Facility.city.ilike(f'%{q}%'),
            Facility.street.ilike(f'%{q}%')
        )
    )

    facilities = query.limit(20).all()
    return jsonify({'facilities': [f.to_dict() for f in facilities]}), 200


@facility_bp.route('/<int:facility_id>/slots', methods=['GET'])
def get_available_slots(facility_id):
    facility = Facility.query.get(facility_id)
    if not facility:
        return jsonify({'error': 'Facility not found'}), 404

    vehicle_type = request.args.get('vehicle_type')
    start_time = request.args.get('start_time')
    end_time = request.args.get('end_time')

    query = Slot.query.filter_by(facility_id=facility_id)

    if vehicle_type:
        query = query.filter_by(vehicle_type=vehicle_type)

    slots = query.all()

    if start_time and end_time:
        try:
            start_dt = parse_client_datetime(start_time)
            end_dt = parse_client_datetime(end_time)
            available_slots = [s for s in slots if s.is_available(start_dt, end_dt)]
        except Exception:
            available_slots = [s for s in slots if not s.is_occupied]
    else:
        available_slots = [s for s in slots if not s.is_occupied]

    return jsonify({
        'slots': [s.to_dict() for s in available_slots],
        'counts': {
            'Car': len([s for s in available_slots if s.vehicle_type == 'Car']),
            'Bike': len([s for s in available_slots if s.vehicle_type == 'Bike']),
            'Truck': len([s for s in available_slots if s.vehicle_type == 'Truck']),
            'EV': len([s for s in available_slots if s.vehicle_type == 'EV'])
        }
    }), 200


@facility_bp.route('', methods=['POST'])
@jwt_required()
@admin_required
def create_facility():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400

    required = ['name', 'street', 'area', 'city', 'pincode', 'latitude', 'longitude']
    for field in required:
        if not data.get(field):
            return jsonify({'error': f'{field} is required'}), 400

    count = Facility.query.count() + 1
    facility_id = f"FAC-{data['city'][:3].upper()}-{count:03d}"

    facility = Facility(
        facility_id=facility_id,
        name=data['name'],
        street=data['street'],
        area=data['area'],
        city=data['city'],
        pincode=data['pincode'],
        latitude=float(data['latitude']),
        longitude=float(data['longitude']),
        total_car=data.get('total_car', 20),
        total_bike=data.get('total_bike', 30),
        total_truck=data.get('total_truck', 5),
        total_ev=data.get('total_ev', 5),
        available_car=data.get('total_car', 20),
        available_bike=data.get('total_bike', 30),
        available_truck=data.get('total_truck', 5),
        available_ev=data.get('total_ev', 5),
        rate_car_hourly=data.get('rate_car_hourly', 40),
        rate_bike_hourly=data.get('rate_bike_hourly', 30),
        rate_truck_hourly=data.get('rate_truck_hourly', 60),
        rate_ev_hourly=data.get('rate_ev_hourly', 35),
        monthly_car=data.get('monthly_car', 8000),
        monthly_bike=data.get('monthly_bike', 5000),
        monthly_truck=data.get('monthly_truck', 12000),
        monthly_ev=data.get('monthly_ev', 6500),
        amenities=data.get('amenities'),
        open_time=data.get('open_time', '06:00'),
        close_time=data.get('close_time', '23:00'),
        is_active=data.get('is_active', True)
    )

    db.session.add(facility)
    db.session.flush()

    slot_configs = [
        ('Car', facility.total_car, 'C'),
        ('Bike', facility.total_bike, 'B'),
        ('Truck', facility.total_truck, 'T'),
        ('EV', facility.total_ev, 'E')
    ]

    for vtype, count, prefix in slot_configs:
        for i in range(1, count + 1):
            slot = Slot(
                facility_id=facility.id,
                slot_code=f"{prefix}{i}",
                vehicle_type=vtype
            )
            db.session.add(slot)

    db.session.commit()
    return jsonify({'message': 'Facility created', 'facility': facility.to_dict()}), 201


@facility_bp.route('/<int:facility_id>', methods=['PUT'])
@jwt_required()
@admin_required
def update_facility(facility_id):
    facility = Facility.query.get(facility_id)
    if not facility:
        return jsonify({'error': 'Facility not found'}), 404

    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400

    updatable = ['name', 'street', 'area', 'city', 'pincode', 'latitude', 'longitude',
                 'rate_car_hourly', 'rate_bike_hourly', 'rate_truck_hourly', 'rate_ev_hourly',
                 'monthly_car', 'monthly_bike', 'monthly_truck', 'monthly_ev',
                 'amenities', 'open_time', 'close_time', 'is_active']

    for field in updatable:
        if field in data:
            setattr(facility, field, data[field])

    db.session.commit()
    return jsonify({'message': 'Facility updated', 'facility': facility.to_dict()}), 200


@facility_bp.route('/<int:facility_id>', methods=['DELETE'])
@jwt_required()
@admin_required
def delete_facility(facility_id):
    facility = Facility.query.get(facility_id)
    if not facility:
        return jsonify({'error': 'Facility not found'}), 404

    facility.is_active = False
    db.session.commit()
    return jsonify({'message': 'Facility deactivated'}), 200


@facility_bp.route('/cities', methods=['GET'])
def get_cities():
    cities = db.session.query(Facility.city).filter_by(is_active=True).distinct().all()
    return jsonify({'cities': [c[0] for c in cities]}), 200