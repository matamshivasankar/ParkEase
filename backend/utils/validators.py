import re
from backend.config import Config

def validate_registration(data):
    if not data.get('full_name') or len(data['full_name'].strip()) < 2:
        return 'Full name must be at least 2 characters'

    email = data.get('email', '').strip().lower()
    if not email or not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
        return 'Invalid email format'

    phone = data.get('phone', '').strip()
    if not phone or not re.match(r'^[6-9]\d{9}$', phone):
        return 'Invalid phone number. Must be 10 digits starting with 6-9'

    password = data.get('password', '')
    if not password or len(password) < 8:
        return 'Password must be at least 8 characters'
    if not re.search(r'[A-Z]', password):
        return 'Password must contain at least one uppercase letter'
    if not re.search(r'\d', password):
        return 'Password must contain at least one number'
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return 'Password must contain at least one special character'

    if data.get('vehicle_no'):
        vehicle_no = data['vehicle_no'].strip().upper()
        if not re.match(r'^[A-Z]{2}\d{2}[A-Z]{1,2}\d{1,4}$', vehicle_no):
            return 'Invalid vehicle number format (e.g., MH12AB1234)'

    return None


def validate_login(data):
    email = data.get('email', '').strip().lower()
    if not email or not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
        return 'Invalid email format'

    password = data.get('password', '')
    if not password:
        return 'Password is required'

    return None


def validate_vehicle(data):
    vehicle_no = data.get('vehicle_no', '').strip().upper()
    if not vehicle_no:
        return 'Vehicle number is required'
    if not re.match(r'^[A-Z]{2}\d{2}[A-Z]{1,2}\d{1,4}$', vehicle_no):
        return 'Invalid vehicle number format (e.g., MH12AB1234)'

    vehicle_type = data.get('vehicle_type')
    if not vehicle_type or vehicle_type not in Config.VEHICLE_TYPES:
        return f'Invalid vehicle type. Must be one of: {", ".join(Config.VEHICLE_TYPES)}'

    return None