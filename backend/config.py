import os
from datetime import timedelta

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'parkease-secret-key-change-in-production')
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'parkease-jwt-secret-change-in-production')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=24)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    JWT_TOKEN_LOCATION = ['headers', 'cookies']
    JWT_COOKIE_CSRF_PROTECT = False
    JWT_COOKIE_SECURE = False
    JWT_CSRF_IN_COOKIES = False

    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///parkease.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False

    CORS_ORIGINS = os.environ.get('CORS_ORIGINS', 'http://localhost:5000,http://127.0.0.1:5000').split(',')

    RATELIMIT_DEFAULT = "200 per minute"
    RATELIMIT_STORAGE_URL = "memory://"

    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', 587))
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')

    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
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

    RECEIPT_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'receipts')

    QR_CODE_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'qr_codes')

    SCREENSHOT_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'screenshots')

class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_ECHO = True

class ProductionConfig(Config):
    DEBUG = False
    JWT_COOKIE_SECURE = True

class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False
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