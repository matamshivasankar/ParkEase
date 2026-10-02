from .auth_routes import auth_bp
from .user_routes import user_bp
from .facility_routes import facility_bp
from .booking_routes import booking_bp
from .payment_routes import payment_bp
from .notification_routes import notification_bp
from .admin_routes import admin_bp

def register_routes(app):
    app.register_blueprint(auth_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(facility_bp)
    app.register_blueprint(booking_bp)
    app.register_blueprint(payment_bp)
    app.register_blueprint(notification_bp)
    app.register_blueprint(admin_bp)