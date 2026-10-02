import sys
sys.path.insert(0, '.')

from backend.app import create_app
from backend.config import Config

app = create_app()
print('App config names:', list(app.config.keys()))
print('JWT_TOKEN_LOCATION:', app.config.get('JWT_TOKEN_LOCATION'))
print('JWT_SECRET_KEY:', app.config.get('JWT_SECRET_KEY'))
print('SECRET_KEY:', app.config.get('SECRET_KEY'))