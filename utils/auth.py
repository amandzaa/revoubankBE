import os
from datetime import datetime, timedelta
from functools import wraps
import jwt
from flask import request, jsonify, current_app, g
from werkzeug.security import check_password_hash, generate_password_hash
from repositories.user_repository import UserRepository

def generate_token(user_id):
    # expiration = datetime.utcnow() + timedelta(days=current_app.config.get('JWT_EXPIRATION_DAYS', 1))
    expiration = datetime.utcnow() + timedelta(minutes=current_app.config.get('JWT_EXPIRATION_MINUTES', 60))
    payload = {
        'user_id': user_id,
        'exp': expiration
    }
    secret_key = os.getenv('SECRET_KEY')
    if not secret_key:
        raise ValueError("No SECRET_KEY set for JWT encoding")
    secret_key = str(secret_key)
    token = jwt.encode(
        payload,
        secret_key,
        algorithm="HS256"
    )
    return token

def hash_password(password):
    return generate_password_hash(password)

def verify_password(stored_password, provided_password):
    return check_password_hash(stored_password, provided_password)

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            if auth_header.startswith('Bearer '):
                token = auth_header.split(' ')[1]
        if not token:
            return jsonify({'message': 'Token is missing!'}), 401

        try:
            secret_key = os.getenv('SECRET_KEY')
            if not secret_key:
                raise ValueError("No SECRET_KEY set for JWT encoding")
            secret_key = str(secret_key)
            # Decode the token
            data = jwt.decode(token, secret_key, algorithms=["HS256"])
            print("Token Payload:", data)  # Debugging
            # Fetch the current user
            user_repo = UserRepository()
            current_user = user_repo.find_by_id(data['user_id'])
            print("Current User:", current_user)  # Debugging
            if not current_user:
                return jsonify({'message': 'User not found!'}), 401
            g.current_user = current_user
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token has expired!'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Invalid token!'}), 401

        return f(*args, **kwargs)
    return decorated

def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not g.current_user.get('is_admin', False):  # Ensure 'is_admin' is in the user object
            return jsonify({'message': 'Admin access required!'}), 403
        return f(*args, **kwargs)
    return decorated
