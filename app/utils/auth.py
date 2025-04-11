import os
from datetime import datetime, timedelta
from functools import wraps

import jwt
from flask import request, jsonify, current_app, g
from werkzeug.security import check_password_hash, generate_password_hash
from app.repositories.user import UserRepository

def generate_token(user_id):
    expiration = datetime.utcnow() + timedelta(minutes=current_app.config.get('JWT_EXPIRATION_MINUTES', 60))
    payload = {
        'user_id': user_id,
        'exp': expiration
    }
    secret_key = os.getenv('SECRET_KEY')
    if not secret_key:
        raise ValueError("No SECRET_KEY set for JWT encoding")
    
    token = jwt.encode(
        payload,
        str(secret_key),
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
            
            # Decode the token
            data = jwt.decode(token, str(secret_key), algorithms=["HS256"])
            
            # Fetch the current user
            user_repo = UserRepository()
            print(f"cek dataa{data['user_id']}")
            current_user = user_repo.find_by_id(data['user_id'])
            print(f"current user {current_user}")
            
            if not current_user:
                return jsonify({'message': 'User not foundxxxx!'}), 401
            
            g.current_user = current_user.to_dict() 
        
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token has expired!'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Invalid token!'}), 401
        
        return f(*args, **kwargs)
    return decorated

def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        # First, make sure we have a current_user set by token_required
        if not hasattr(g, 'current_user'):
            return jsonify({'message': 'Authentication required!'}), 401
        
        # Check admin status based on your database structure
        # If current_user is an SQLAlchemy model instance:
        if hasattr(g.current_user, 'is_admin'):
            is_admin = g.current_user.is_admin
        # If current_user is a dictionary (from to_dict()):
        elif isinstance(g.current_user, dict) and 'is_admin' in g.current_user:
            is_admin = g.current_user['is_admin']
        else:
            is_admin = False
            
        if not is_admin:
            return jsonify({'message': 'Admin access required!'}), 403
            
        return f(*args, **kwargs)
    return decorated