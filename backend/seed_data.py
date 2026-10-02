"""Seed ParkEase with one admin, a demo user and 20 facilities.

Facilities cover 10 cities with 2 sites in each city.

Usage:
    python backend/seed_data.py            # skip if an admin already exists
    python backend/seed_data.py --reset    # drop everything and reseed
"""

import json
import sys

from backend.app import create_app
from backend.models import db, User, Facility, Slot

ADMIN_EMAIL = 'admin@parkease.com'
ADMIN_PASSWORD = 'Admin@123'
DEMO_EMAIL = 'demo@parkease.com'
DEMO_PASSWORD = 'Demo@123'

CITY_CODES = {
    'Delhi': 'DEL',
    'Mumbai': 'MUM',
    'Bengaluru': 'BLR',
    'Chennai': 'MAA',
    'Kolkata': 'CCU',
    'Hyderabad': 'HYD',
    'Pune': 'PUN',
    'Ahmedabad': 'AMD',
    'Jaipur': 'JAI',
    'Lucknow': 'LKO',
}

FACILITIES_DATA = [
    # Delhi
    {
        'name': 'ParkEase Cyber City',
        'street': '101 Cyber Hub',
        'area': 'Gurgaon',
        'city': 'Delhi',
        'pincode': '122002',
        'latitude': 28.4595,
        'longitude': 77.0266,
        'total_car': 80, 'total_bike': 100, 'total_truck': 10, 'total_ev': 10,
        'rate_car_hourly': 45, 'rate_bike_hourly': 35, 'rate_truck_hourly': 65, 'rate_ev_hourly': 40,
        'monthly_car': 9000, 'monthly_bike': 6000, 'monthly_truck': 13000, 'monthly_ev': 7000,
        'amenities': ['CCTV', 'EV Charging', 'Security Guard', 'Restrooms', 'WiFi', 'Cafeteria'],
        'open_time': '06:00', 'close_time': '22:00',
        'rating': 4.6
    },
    {
        'name': 'ParkEase Connaught Place',
        'street': '12 Janpath Lane',
        'area': 'Connaught Place',
        'city': 'Delhi',
        'pincode': '110001',
        'latitude': 28.6315,
        'longitude': 77.2167,
        'total_car': 45, 'total_bike': 70, 'total_truck': 4, 'total_ev': 6,
        'rate_car_hourly': 60, 'rate_bike_hourly': 40, 'rate_truck_hourly': 80, 'rate_ev_hourly': 45,
        'monthly_car': 14000, 'monthly_bike': 7500, 'monthly_truck': 16000, 'monthly_ev': 9000,
        'amenities': ['CCTV', 'Valet', 'Security Guard', 'Restrooms', 'Car Wash'],
        'open_time': '07:00', 'close_time': '21:00',
        'rating': 4.4
    },
    # Mumbai
    {
        'name': 'ParkEase Marine Plaza',
        'street': '202 Marine Drive',
        'area': 'Churchgate',
        'city': 'Mumbai',
        'pincode': '400020',
        'latitude': 18.9435,
        'longitude': 72.8237,
        'total_car': 60, 'total_bike': 120, 'total_truck': 5, 'total_ev': 10,
        'rate_car_hourly': 55, 'rate_bike_hourly': 45, 'rate_truck_hourly': 75, 'rate_ev_hourly': 50,
        'monthly_car': 12000, 'monthly_bike': 8000, 'monthly_truck': 18000, 'monthly_ev': 10000,
        'amenities': ['CCTV', 'EV Charging', 'Security Guard', 'Restrooms', 'Valet', 'Car Wash'],
        'open_time': '05:00', 'close_time': '23:00',
        'rating': 4.4
    },
    {
        'name': 'ParkEase Andheri East',
        'street': '301 MIDC Road',
        'area': 'Andheri East',
        'city': 'Mumbai',
        'pincode': '400069',
        'latitude': 19.1136,
        'longitude': 72.8697,
        'total_car': 75, 'total_bike': 95, 'total_truck': 8, 'total_ev': 12,
        'rate_car_hourly': 50, 'rate_bike_hourly': 35, 'rate_truck_hourly': 70, 'rate_ev_hourly': 45,
        'monthly_car': 9500, 'monthly_bike': 6500, 'monthly_truck': 14000, 'monthly_ev': 7500,
        'amenities': ['CCTV', 'EV Charging', 'Security Guard', 'Restrooms', 'WiFi', 'Valet'],
        'open_time': '06:00', 'close_time': '23:00',
        'rating': 4.5
    },
    # Bengaluru
    {
        'name': 'ParkEase Tech Park',
        'street': '123 IT Park Road',
        'area': 'Whitefield',
        'city': 'Bengaluru',
        'pincode': '560066',
        'latitude': 12.9698,
        'longitude': 77.7499,
        'total_car': 50, 'total_bike': 80, 'total_truck': 10, 'total_ev': 10,
        'rate_car_hourly': 40, 'rate_bike_hourly': 30, 'rate_truck_hourly': 60, 'rate_ev_hourly': 35,
        'monthly_car': 8000, 'monthly_bike': 5000, 'monthly_truck': 12000, 'monthly_ev': 6500,
        'amenities': ['CCTV', 'EV Charging', 'Security Guard', 'Restrooms', 'WiFi', 'Fire Safety'],
        'open_time': '06:00', 'close_time': '23:00',
        'rating': 4.5
    },
    {
        'name': 'ParkEase Mall Plaza',
        'street': '456 Mall Avenue',
        'area': 'Koramangala',
        'city': 'Bengaluru',
        'pincode': '560034',
        'latitude': 12.9352,
        'longitude': 77.6146,
        'total_car': 100, 'total_bike': 150, 'total_truck': 5, 'total_ev': 15,
        'rate_car_hourly': 50, 'rate_bike_hourly': 40, 'rate_truck_hourly': 70, 'rate_ev_hourly': 45,
        'monthly_car': 10000, 'monthly_bike': 7000, 'monthly_truck': 15000, 'monthly_ev': 8000,
        'amenities': ['CCTV', 'EV Charging', 'Security Guard', 'Restrooms', 'WiFi', 'Car Wash', 'Valet'],
        'open_time': '05:00', 'close_time': '24:00',
        'rating': 4.7
    },
    # Chennai
    {
        'name': 'ParkEase IT Corridor',
        'street': '303 OMR Road',
        'area': 'Thoraipakkam',
        'city': 'Chennai',
        'pincode': '600097',
        'latitude': 12.9348,
        'longitude': 80.2362,
        'total_car': 70, 'total_bike': 100, 'total_truck': 8, 'total_ev': 12,
        'rate_car_hourly': 35, 'rate_bike_hourly': 25, 'rate_truck_hourly': 55, 'rate_ev_hourly': 30,
        'monthly_car': 7000, 'monthly_bike': 4500, 'monthly_truck': 11000, 'monthly_ev': 6000,
        'amenities': ['CCTV', 'EV Charging', 'Security Guard', 'Restrooms', 'WiFi'],
        'open_time': '06:00', 'close_time': '22:00',
        'rating': 4.2
    },
    {
        'name': 'ParkEase T Nagar Hub',
        'street': '404 Ranganathan Street',
        'area': 'T. Nagar',
        'city': 'Chennai',
        'pincode': '600017',
        'latitude': 13.0418,
        'longitude': 80.2341,
        'total_car': 40, 'total_bike': 85, 'total_truck': 4, 'total_ev': 6,
        'rate_car_hourly': 38, 'rate_bike_hourly': 22, 'rate_truck_hourly': 58, 'rate_ev_hourly': 32,
        'monthly_car': 7500, 'monthly_bike': 4200, 'monthly_truck': 11500, 'monthly_ev': 6200,
        'amenities': ['CCTV', 'Security Guard', 'Restrooms', 'Car Wash', 'Valet'],
        'open_time': '06:30', 'close_time': '22:30',
        'rating': 4.1
    },
    # Kolkata
    {
        'name': 'ParkEase Salt Lake',
        'street': '404 Sector V',
        'area': 'Salt Lake',
        'city': 'Kolkata',
        'pincode': '700091',
        'latitude': 22.5726,
        'longitude': 88.4147,
        'total_car': 60, 'total_bike': 90, 'total_truck': 10, 'total_ev': 8,
        'rate_car_hourly': 30, 'rate_bike_hourly': 20, 'rate_truck_hourly': 50, 'rate_ev_hourly': 25,
        'monthly_car': 6000, 'monthly_bike': 4000, 'monthly_truck': 10000, 'monthly_ev': 5000,
        'amenities': ['CCTV', 'EV Charging', 'Security Guard', 'Restrooms'],
        'open_time': '07:00', 'close_time': '21:00',
        'rating': 4.1
    },
    {
        'name': 'ParkEase Park Street',
        'street': '505 Park Street',
        'area': 'Park Street',
        'city': 'Kolkata',
        'pincode': '700016',
        'latitude': 22.5535,
        'longitude': 88.3520,
        'total_car': 35, 'total_bike': 60, 'total_truck': 4, 'total_ev': 5,
        'rate_car_hourly': 42, 'rate_bike_hourly': 26, 'rate_truck_hourly': 58, 'rate_ev_hourly': 30,
        'monthly_car': 6800, 'monthly_bike': 3800, 'monthly_truck': 10500, 'monthly_ev': 5400,
        'amenities': ['CCTV', 'Security Guard', 'Restrooms', 'Valet', 'Car Wash'],
        'open_time': '08:00', 'close_time': '22:00',
        'rating': 4.0
    },
    # Hyderabad
    {
        'name': 'ParkEase Hitech City',
        'street': '505 Cyberabad',
        'area': 'Madhapur',
        'city': 'Hyderabad',
        'pincode': '500081',
        'latitude': 17.4435,
        'longitude': 78.3772,
        'total_car': 90, 'total_bike': 130, 'total_truck': 10, 'total_ev': 15,
        'rate_car_hourly': 40, 'rate_bike_hourly': 30, 'rate_truck_hourly': 60, 'rate_ev_hourly': 35,
        'monthly_car': 8000, 'monthly_bike': 5000, 'monthly_truck': 12000, 'monthly_ev': 6500,
        'amenities': ['CCTV', 'EV Charging', 'Security Guard', 'Restrooms', 'WiFi', 'Gym'],
        'open_time': '05:00', 'close_time': '23:00',
        'rating': 4.5
    },
    {
        'name': 'ParkEase Banjara Hills',
        'street': '606 Road No. 12',
        'area': 'Banjara Hills',
        'city': 'Hyderabad',
        'pincode': '500034',
        'latitude': 17.4126,
        'longitude': 78.4482,
        'total_car': 55, 'total_bike': 70, 'total_truck': 5, 'total_ev': 8,
        'rate_car_hourly': 48, 'rate_bike_hourly': 32, 'rate_truck_hourly': 68, 'rate_ev_hourly': 42,
        'monthly_car': 11000, 'monthly_bike': 5500, 'monthly_truck': 14500, 'monthly_ev': 7800,
        'amenities': ['CCTV', 'EV Charging', 'Valet', 'Restrooms', 'Car Wash', 'Cafeteria'],
        'open_time': '06:00', 'close_time': '23:30',
        'rating': 4.4
    },
    # Pune
    {
        'name': 'ParkEase Baner Hub',
        'street': '606 Baner Road',
        'area': 'Baner',
        'city': 'Pune',
        'pincode': '411045',
        'latitude': 18.5593,
        'longitude': 73.7796,
        'total_car': 50, 'total_bike': 80, 'total_truck': 8, 'total_ev': 10,
        'rate_car_hourly': 35, 'rate_bike_hourly': 25, 'rate_truck_hourly': 55, 'rate_ev_hourly': 30,
        'monthly_car': 7000, 'monthly_bike': 4500, 'monthly_truck': 11000, 'monthly_ev': 6000,
        'amenities': ['CCTV', 'EV Charging', 'Security Guard', 'Restrooms', 'WiFi'],
        'open_time': '06:00', 'close_time': '22:00',
        'rating': 4.3
    },
    {
        'name': 'ParkEase Hinjewadi Phase 2',
        'street': '707 Rajiv Gandhi Infotech Park',
        'area': 'Hinjewadi',
        'city': 'Pune',
        'pincode': '411057',
        'latitude': 18.5913,
        'longitude': 73.7389,
        'total_car': 85, 'total_bike': 110, 'total_truck': 12, 'total_ev': 14,
        'rate_car_hourly': 33, 'rate_bike_hourly': 22, 'rate_truck_hourly': 52, 'rate_ev_hourly': 28,
        'monthly_car': 6800, 'monthly_bike': 4200, 'monthly_truck': 10500, 'monthly_ev': 5700,
        'amenities': ['CCTV', 'EV Charging', 'Security Guard', 'Restrooms', 'WiFi', 'Shuttle Service'],
        'open_time': '05:30', 'close_time': '23:00',
        'rating': 4.6
    },
    # Ahmedabad
    {
        'name': 'ParkEase SG Highway',
        'street': '707 SG Road',
        'area': 'Bodakdev',
        'city': 'Ahmedabad',
        'pincode': '380054',
        'latitude': 23.0395,
        'longitude': 72.5072,
        'total_car': 40, 'total_bike': 70, 'total_truck': 10, 'total_ev': 8,
        'rate_car_hourly': 30, 'rate_bike_hourly': 20, 'rate_truck_hourly': 50, 'rate_ev_hourly': 25,
        'monthly_car': 6000, 'monthly_bike': 4000, 'monthly_truck': 10000, 'monthly_ev': 5000,
        'amenities': ['CCTV', 'Security Guard', 'Restrooms'],
        'open_time': '07:00', 'close_time': '21:00',
        'rating': 4.0
    },
    {
        'name': 'ParkEase Navrangpura',
        'street': '808 Stadium Road',
        'area': 'Navrangpura',
        'city': 'Ahmedabad',
        'pincode': '380009',
        'latitude': 23.0325,
        'longitude': 72.5689,
        'total_car': 48, 'total_bike': 65, 'total_truck': 6, 'total_ev': 7,
        'rate_car_hourly': 34, 'rate_bike_hourly': 22, 'rate_truck_hourly': 54, 'rate_ev_hourly': 28,
        'monthly_car': 6500, 'monthly_bike': 4200, 'monthly_truck': 10800, 'monthly_ev': 5400,
        'amenities': ['CCTV', 'EV Charging', 'Restrooms', 'Car Wash'],
        'open_time': '07:00', 'close_time': '22:00',
        'rating': 4.2
    },
    # Jaipur
    {
        'name': 'ParkEase Malviya Nagar',
        'street': '909 Malviya Nagar Road',
        'area': 'Malviya Nagar',
        'city': 'Jaipur',
        'pincode': '302017',
        'latitude': 26.8544,
        'longitude': 75.8132,
        'total_car': 45, 'total_bike': 60, 'total_truck': 6, 'total_ev': 6,
        'rate_car_hourly': 25, 'rate_bike_hourly': 15, 'rate_truck_hourly': 45, 'rate_ev_hourly': 22,
        'monthly_car': 5000, 'monthly_bike': 3200, 'monthly_truck': 9000, 'monthly_ev': 4200,
        'amenities': ['CCTV', 'Security Guard', 'Restrooms'],
        'open_time': '07:00', 'close_time': '21:00',
        'rating': 3.9
    },
    {
        'name': 'ParkEase Vaishali Nagar',
        'street': '1010 Vaishali Nagar Road',
        'area': 'Vaishali Nagar',
        'city': 'Jaipur',
        'pincode': '302021',
        'latitude': 26.9124,
        'longitude': 75.7373,
        'total_car': 52, 'total_bike': 72, 'total_truck': 7, 'total_ev': 8,
        'rate_car_hourly': 27, 'rate_bike_hourly': 16, 'rate_truck_hourly': 47, 'rate_ev_hourly': 23,
        'monthly_car': 5300, 'monthly_bike': 3400, 'monthly_truck': 9200, 'monthly_ev': 4400,
        'amenities': ['CCTV', 'EV Charging', 'Security Guard', 'Restrooms', 'WiFi'],
        'open_time': '06:30', 'close_time': '22:00',
        'rating': 4.1
    },
    # Lucknow
    {
        'name': 'ParkEase Gomti Nagar',
        'street': '1111 Gomti Nagar Road',
        'area': 'Gomti Nagar',
        'city': 'Lucknow',
        'pincode': '226010',
        'latitude': 26.8606,
        'longitude': 81.0083,
        'total_car': 50, 'total_bike': 80, 'total_truck': 6, 'total_ev': 8,
        'rate_car_hourly': 22, 'rate_bike_hourly': 12, 'rate_truck_hourly': 40, 'rate_ev_hourly': 20,
        'monthly_car': 4500, 'monthly_bike': 2800, 'monthly_truck': 8500, 'monthly_ev': 3800,
        'amenities': ['CCTV', 'Security Guard', 'Restrooms', 'WiFi'],
        'open_time': '07:00', 'close_time': '21:00',
        'rating': 3.8
    },
    {
        'name': 'ParkEase Hazratganj',
        'street': '1212 MG Road',
        'area': 'Hazratganj',
        'city': 'Lucknow',
        'pincode': '226001',
        'latitude': 26.8509,
        'longitude': 80.9498,
        'total_car': 35, 'total_bike': 55, 'total_truck': 4, 'total_ev': 5,
        'rate_car_hourly': 24, 'rate_bike_hourly': 14, 'rate_truck_hourly': 42, 'rate_ev_hourly': 21,
        'monthly_car': 4800, 'monthly_bike': 3000, 'monthly_truck': 8800, 'monthly_ev': 4000,
        'amenities': ['CCTV', 'Security Guard', 'Restrooms', 'Valet'],
        'open_time': '07:30', 'close_time': '21:30',
        'rating': 3.9
    },
]

SLOT_PREFIXES = [('Car', 'C'), ('Bike', 'B'), ('Truck', 'T'), ('EV', 'E')]
TOTAL_KEYS = ['total_car', 'total_bike', 'total_truck', 'total_ev']


def create_users():
    admin = User(
        user_id='PKR-2024-00000',
        full_name='ParkEase Admin',
        email=ADMIN_EMAIL,
        phone='9999999999',
        role='admin',
        is_verified=True
    )
    admin.set_password(ADMIN_PASSWORD)
    db.session.add(admin)

    demo_user = User(
        user_id='PKR-2024-00001',
        full_name='Demo User',
        email=DEMO_EMAIL,
        phone='9876543210',
        role='user',
        is_verified=True
    )
    demo_user.set_password(DEMO_PASSWORD)
    db.session.add(demo_user)


def create_facilities():
    city_seq = {}

    for fdata in FACILITIES_DATA:
        city = fdata['city']
        city_seq[city] = city_seq.get(city, 0) + 1
        facility_id = f"FAC-{CITY_CODES[city]}-{city_seq[city]:02d}"

        totals = {k: fdata[k] for k in TOTAL_KEYS}
        facility = Facility(
            facility_id=facility_id,
            amenities=json.dumps(fdata['amenities']),
            **{**{k: v for k, v in fdata.items() if k != 'amenities'},
               **totals,
               **{f'available_{k[6:]}': v for k, v in totals.items()}}
        )
        db.session.add(facility)
        db.session.flush()

        for vtype, prefix in SLOT_PREFIXES:
            for i in range(1, facility.get_total_count(vtype) + 1):
                db.session.add(Slot(
                    facility_id=facility.id,
                    slot_code=f"{prefix}{i}",
                    vehicle_type=vtype
                ))


def seed_data(reset=False):
    app = create_app()
    with app.app_context():
        if reset:
            print("Dropping existing tables...")
            db.drop_all()
            db.create_all()
        elif User.query.filter_by(email=ADMIN_EMAIL).first():
            print(f"Admin '{ADMIN_EMAIL}' already exists. Skipping seed.")
            print("Run 'python backend/seed_data.py --reset' to wipe and reseed.")
            return

        create_users()
        create_facilities()
        db.session.commit()

        cities = db.session.query(Facility.city).distinct().count()
        facilities = Facility.query.count()
        slots = Slot.query.count()

        print("Seed data created successfully!")
        print(f"{cities} cities &middot; {facilities} facilities &middot; {slots} slots")
        print(f"Admin: {ADMIN_EMAIL} / {ADMIN_PASSWORD}")
        print(f"Demo User: {DEMO_EMAIL} / {DEMO_PASSWORD}")


if __name__ == '__main__':
    seed_data(reset='--reset' in sys.argv)
