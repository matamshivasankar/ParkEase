from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import (
    create_access_token, create_refresh_token,
    jwt_required, get_jwt_identity, get_jwt,
    set_access_cookies, set_refresh_cookies, unset_jwt_cookies
)
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import re

from backend.models import db, User
from backend.utils.validators import validate_registration, validate_login
from backend.middleware.auth_middleware import admin_required, get_current_user_id
from backend.utils.helpers import utcnow

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')

@auth_bp.route('/register', methods=['POST'])
@jwt_required(optional=True)  # Allow optional JWT, but don't require CSRF for registration
def register():
    # Disable CSRF for this endpoint since user doesn't have a session yet
    if hasattr(request, 'csrf_protect'):
        request.csrf_protect = False
    
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400

    validation_error = validate_registration(data)
    if validation_error:
        return jsonify({'error': validation_error}), 400

    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Email already registered'}), 409

    if User.query.filter_by(phone=data['phone']).first():
        return jsonify({'error': 'Phone number already registered'}), 409

    user = User(
        full_name=data['full_name'].strip(),
        email=data['email'].strip().lower(),
        phone=data['phone'].strip(),
        role='user'
    )
    user.set_password(data['password'])
    user.user_id = user.generate_user_id()

    db.session.add(user)
    db.session.commit()

    access_token = create_access_token(identity=str(user.id))
    refresh_token = create_refresh_token(identity=str(user.id))

    response = jsonify({
        'message': 'Registration successful',
        'user': user.to_dict(),
        'access_token': access_token,
        'refresh_token': refresh_token
    })
    set_access_cookies(response, access_token)
    set_refresh_cookies(response, refresh_token)

    return response, 201


@auth_bp.route('/login', methods=['POST'])
@jwt_required(optional=True)  # Allow optional JWT, but don't require CSRF for login
def login():
    # Disable CSRF for this endpoint since user doesn't have a session yet
    if hasattr(request, 'csrf_protect'):
        request.csrf_protect = False
    
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400

    validation_error = validate_login(data)
    if validation_error:
        return jsonify({'error': validation_error}), 400

    user = User.query.filter_by(email=data['email'].strip().lower()).first()
    if not user or not user.check_password(data['password']):
        return jsonify({'error': 'Invalid email or password'}), 401

    if user.is_blocked:
        return jsonify({'error': 'Account is blocked. Contact support.'}), 403

    user.last_login = utcnow()
    db.session.commit()

    access_token = create_access_token(identity=str(user.id))
    refresh_token = create_refresh_token(identity=str(user.id))

    response = jsonify({
        'message': 'Login successful',
        'user': user.to_dict(),
        'access_token': access_token,
        'refresh_token': refresh_token
    })
    set_access_cookies(response, access_token)
    set_refresh_cookies(response, refresh_token)

    return response, 200


@auth_bp.route('/logout', methods=['POST'])
def logout():
    response = jsonify({'message': 'Logged out successfully'})
    unset_jwt_cookies(response)
    return response, 200


@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    current_user_id = get_current_user_id()
    user = User.query.get(current_user_id)
    if not user or user.is_blocked:
        return jsonify({'error': 'User not found or blocked'}), 401

    access_token = create_access_token(identity=str(current_user_id))
    response = jsonify({'access_token': access_token})
    set_access_cookies(response, access_token)
    return response, 200


@auth_bp.route('/verify', methods=['GET'])
@jwt_required()
def verify_token():
    current_user_id = get_current_user_id()
    user = User.query.get(current_user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404

    if user.is_blocked:
        return jsonify({'error': 'Account is blocked'}), 403

    return jsonify({
        'valid': True,
        'user': user.to_dict()
    }), 200


@auth_bp.route('/change-password', methods=['PUT'])
@jwt_required()
def change_password():
    current_user_id = get_current_user_id()
    user = User.query.get(current_user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404

    data = request.get_json()
    if not data or not data.get('current_password') or not data.get('new_password'):
        return jsonify({'error': 'Current and new password required'}), 400

    if not user.check_password(data['current_password']):
        return jsonify({'error': 'Current password is incorrect'}), 401

    if len(data['new_password']) < 8:
        return jsonify({'error': 'New password must be at least 8 characters'}), 400

    if not re.search(r'[A-Z]', data['new_password']):
        return jsonify({'error': 'New password must contain at least one uppercase letter'}), 400

    if not re.search(r'\d', data['new_password']):
        return jsonify({'error': 'New password must contain at least one number'}), 400

    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', data['new_password']):
        return jsonify({'error': 'New password must contain at least one special character'}), 400

    user.set_password(data['new_password'])
    db.session.commit()

    return jsonify({'message': 'Password changed successfully'}), 200
