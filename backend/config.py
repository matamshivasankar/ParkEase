import os
from datetime import timedelta

# Base directory for everything the app writes at runtime (uploads, receipts,
# QR codes, screenshots). Override DATA_DIR to point these at a persistent
# volume / Render Disk so they survive a redeploy.
_DATA_DIR = os.environ.get('DATA_DIR', os.path.dirname(os.path.abspath(__file__)))


def _database_url():
    """Return the SQLAlchemy connection string.

    Render (like Heroku) injects ``DATABASE_URL`` using the legacy
    ``postgres://`` scheme, which SQLAlchemy 2.x rejects. Normalise it to
    ``postgresql://``; leave anything else untouched.
    """
    url = os.environ.get('DATABASE_URL', 'sqlite:///parkease.db')
    if url.startswith('postgres://'):
        url = 'postgresql://' + url[len('postgres://'):]
    return url


def _cors_origins():
    """Comma-separated allowed origins.

    When CORS_ORIGINS is not set explicitly, allow local development plus the
    public URL Render assigns the service (RENDER_EXTERNAL_URL), so the bundled
    frontend and the Socket.IO handshake work out of the box in production.
    """
    configured = os.environ.get('CORS_ORIGINS')
    if configured:
        return [origin.strip() for origin in configured.split(',') if origin.strip()]

    origins = ['http://localhost:5000', 'http://127.0.0.1:5000']
    render_url = os.environ.get('RENDER_EXTERNAL_URL')
    if render_url:
        origins.append(render_url.rstrip('/'))
    return origins


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'parkease-secret-key-change-in-production')
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'parkease-jwt-secret-change-in-production')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=24)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    JWT_TOKEN_LOCATION = ['cookies', 'headers']
    JWT_COOKIE_CSRF_PROTECT = True
    JWT_COOKIE_SECURE = False  # True in production
    JWT_CSRF_IN_COOKIES = True
    JWT_COOKIE_SAMESITE = 'Lax'
    JWT_ACCESS_COOKIE_PATH = '/'
    JWT_REFRESH_COOKIE_PATH = '/api/auth/refresh'

    SQLALCHEMY_DATABASE_URI = _database_url()
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False

    CORS_ORIGINS = _cors_origins()

    RATELIMIT_DEFAULT = os.environ.get('RATELIMIT_DEFAULT', '200 per minute')
    RATELIMIT_STORAGE_URL = os.environ.get('RATELIMIT_STORAGE_URL', 'memory://')

    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', 587))
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')

    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER', os.path.join(_DATA_DIR, 'uploads'))
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024

    BASE_RATES = {
        'Car': {'hourly': 40, 'daily': 400, 'monthly': 8000},
        'Bike': {'hourly': 30, 'daily': 300, 'monthly': 5000},
        'Truck': {'hourly': 60, 'daily': 600, 'monthly': 12000},
        'EV': {'hourly': 35, 'daily': 350, 'monthly': 6500},
    }

    DISCOUNTS = {
        'weekend': 0.15,
        'weekly': 0.10,
        'monthly': 0.20,
        'early_bird': 0.05,
    }
    GST_RATE = 0.18

    # All timestamps are stored as naive UTC; this is the timezone used for
    # business rules such as weekend / early-bird discounts.
    LOCAL_TIMEZONE = os.environ.get('LOCAL_TIMEZONE', 'Asia/Kolkata')

    CITIES = [
        'Delhi', 'Mumbai', 'Bengaluru', 'Chennai', 'Kolkata',
        'Hyderabad', 'Pune', 'Ahmedabad', 'Jaipur', 'Lucknow'
    ]

    VEHICLE_TYPES = ['Car', 'Bike', 'Truck', 'EV']

    PAYMENT_METHODS = ['card', 'upi', 'wallet', 'netbanking']

    BOOKING_STATUS = ['reserved', 'confirmed', 'active', 'completed', 'cancelled']
    PAYMENT_STATUS = ['pending', 'paid', 'refunded', 'failed']

    SLOT_LOCK_DURATION = 10

    RECEIPT_FOLDER = os.environ.get('RECEIPT_FOLDER', os.path.join(_DATA_DIR, 'receipts'))

    QR_CODE_FOLDER = os.environ.get('QR_CODE_FOLDER', os.path.join(_DATA_DIR, 'qr_codes'))

    SCREENSHOT_FOLDER = os.environ.get('SCREENSHOT_FOLDER', os.path.join(_DATA_DIR, 'screenshots'))

class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_ECHO = True

class ProductionConfig(Config):
    DEBUG = False
    JWT_COOKIE_SECURE = True
    JWT_COOKIE_SAMESITE = 'None'

class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False
    JWT_COOKIE_CSRF_PROTECT = False
    # Uploads during tests go to a scratch folder so runs never litter
    # backend/screenshots with throwaway 1x1 pixels.
    SCREENSHOT_FOLDER = os.path.join(
        os.environ.get('TEMP', os.path.dirname(os.path.abspath(__file__))),
        'parkease-test-screenshots'
    )

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}