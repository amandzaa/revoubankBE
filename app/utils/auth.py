import os
from datetime import datetime, timedelta
from functools import wraps

import jwt
from flask import request, jsonify, current_app, g
from werkzeug.security import check_password_hash, generate_password_hash
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from app.models.user import User  # Assuming you have a User model defined

class UserRepository:
    def __init__(self):
        # Create SQLAlchemy engine and session
        self.engine = create_engine(os.getenv('DATABASE_URL'))
        self.session = Session(self.engine)

    def find_by_id(self, user_id):
        try:
            user = self.session.query(User).filter(User.id == user_id).first()
            return user.to_dict() if user else None
        except Exception as e:
            print(f"Error finding user: {e}")
            return None

    def find_by_username(self, username):
        try:
            user = self.session.query(User).filter(User.username == username).first()
            return user.to_dict() if user else None
        except Exception as e:
            print(f"Error finding user: {e}")
            return None

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
            current_user = user_repo.find_by_id(data['user_id'])
            
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
        if not g.current_user.get('is_admin', False):
            return jsonify({'message': 'Admin access required!'}), 403
        return f(*args, **kwargs)
    return decorated