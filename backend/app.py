from flask import Flask, jsonify, send_from_directory, request
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, decode_token
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from werkzeug.middleware.proxy_fix import ProxyFix
import os
import re

from backend.config import config
from backend.models import db
from backend.routes import register_routes

# SocketIO initialized lazily
socketio = None

# sid -> user id, populated by the authenticated socket handshake
socket_users = {}

SCREENSHOT_NAME_RE = re.compile(r'^screenshot_(BKG-\d{4}-\d{5})_\d{8}_\d{6}\.[A-Za-z0-9]+$')

def _user_from_token(token):
    """Resolve a raw JWT to a User, or None if the token is unusable."""
    if not token:
        return None
    try:
        identity = decode_token(token).get('sub')
        user_id = int(identity)
    except Exception:
        return None
    from backend.models import User
    return User.query.get(user_id)


def create_app(config_name=None, with_socketio=False):
    global socketio
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'default')

    app = Flask(__name__, static_folder='../frontend')
    app.config.from_object(config[config_name])

    app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

    db.init_app(app)
    jwt = JWTManager(app)
    CORS(app, origins=app.config['CORS_ORIGINS'], supports_credentials=True)

    limiter = Limiter(
        get_remote_address,
        app=app,
        default_limits=[app.config['RATELIMIT_DEFAULT']],
        storage_uri=app.config['RATELIMIT_STORAGE_URL']
    )

    register_routes(app)

    @app.route('/')
    def index():
        return send_from_directory('../frontend', 'index.html')

    @app.route('/<path:path>')
    def static_files(path):
        return send_from_directory('../frontend', path)

    @app.route('/api/health')
    def health_check():
        return jsonify({'status': 'healthy', 'service': 'ParkEase API'}), 200

    @app.route('/screenshots/<path:filename>')
    def serve_screenshot(filename):
        """Payment screenshots: admin only, or the user who owns the booking.

        The filename encodes the booking id, so ownership can be checked without
        a database lookup keyed on attacker-controlled input.
        """
        token = request.headers.get('Authorization', '').removeprefix('Bearer ').strip()
        if not token:
            token = request.cookies.get('access_token_cookie')
        user = _user_from_token(token)
        if not user:
            return jsonify({'error': 'Authentication required'}), 401

        if user.role != 'admin':
            match = SCREENSHOT_NAME_RE.match(os.path.basename(filename))
            if not match:
                return jsonify({'error': 'Not found'}), 404
            from backend.models import Booking
            booking = Booking.query.filter_by(booking_id=match.group(1)).first()
            if not booking or booking.user_id != user.id:
                return jsonify({'error': 'Unauthorized'}), 403

        return send_from_directory(app.config['SCREENSHOT_FOLDER'], filename)

    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return jsonify({'error': 'Token has expired'}), 401

    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return jsonify({'error': 'Invalid token'}), 401

    @jwt.unauthorized_loader
    def missing_token_callback(error):
        return jsonify({'error': 'Authorization token required'}), 401

    if with_socketio:
        from flask_socketio import SocketIO
        socketio = SocketIO()
        socketio.init_app(app, cors_allowed_origins=app.config['CORS_ORIGINS'], async_mode='threading')

        @socketio.on('connect')
        def on_connect(auth=None):
            """Authenticate the handshake and subscribe to the user's rooms.

            The client passes its access token as `auth: { token }`. Joining the
            personal rooms here (rather than from a separate client event) means
            notifications reach every tab without the client having to ask.
            """
            token = (auth or {}).get('token') if isinstance(auth, dict) else None
            user = _user_from_token(token)
            if not user:
                return False  # reject the connection

            from flask import request as flask_request
            from flask_socketio import join_room
            sid = flask_request.sid
            socket_users[sid] = user.id
            join_room(f'user_{user.id}')
            if user.role == 'admin':
                join_room('admins')
            return True

        @socketio.on('disconnect')
        def on_disconnect(*args):
            from flask import request as flask_request
            socket_users.pop(getattr(flask_request, 'sid', None), None)

        # SocketIO events
        @socketio.on('join_booking')
        def on_join_booking(data):
            from flask import request as flask_request
            from flask_socketio import join_room
            if socket_users.get(flask_request.sid) is None:
                return {'status': 'unauthorized'}
            booking_id = data.get('booking_id')
            if booking_id:
                join_room(f'booking_{booking_id}')
                return {'status': 'joined', 'booking_id': booking_id}

        @socketio.on('leave_booking')
        def on_leave_booking(data):
            from flask import request as flask_request
            from flask_socketio import leave_room
            if socket_users.get(flask_request.sid) is None:
                return {'status': 'unauthorized'}
            booking_id = data.get('booking_id')
            if booking_id:
                leave_room(f'booking_{booking_id}')
                return {'status': 'left', 'booking_id': booking_id}

    with app.app_context():
        db.create_all()

    return app


if __name__ == '__main__':
    app = create_app(with_socketio=True)
    if socketio:
        socketio.run(app, host='0.0.0.0', port=5000, debug=True)
    else:
        app.run(host='0.0.0.0', port=5000, debug=True)