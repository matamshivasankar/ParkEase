import sys
sys.path.insert(0, '.')

from backend.config import Config

print('JWT_TOKEN_LOCATION:', Config.JWT_TOKEN_LOCATION)
print('JWT_SECRET_KEY:', Config.JWT_SECRET_KEY)
print('JWT_ACCESS_TOKEN_EXPIRES:', Config.JWT_ACCESS_TOKEN_EXPIRES)
print('VEHICLE_TYPES:', Config.VEHICLE_TYPES)
print('CITIES:', Config.CITIES)