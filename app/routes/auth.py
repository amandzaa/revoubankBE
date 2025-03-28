from flask import Blueprint, request, jsonify
from app.services.auth import AuthService
from app.utils.database_session_manager import get_db_session

auth_bp = Blueprint('auth_bp', __name__, url_prefix='/revoubank')

@auth_bp.route('/login', methods=['POST'])
def login_user():
    if not request.is_json:
        return jsonify({'message': 'Content-Type must be application/json'}), 415
    
    data = request.json
    if not data:
        return jsonify({'message': 'Invalid request data'}), 400
    
    # Get the current database session
    db_session = get_db_session()
    
    try:
        # Create AuthService with the session
        auth_service = AuthService(db_session)
        
        success, result, status_code = auth_service.login(
            email=data.get('email'),
            password=data.get('password')
        )
        
        if not success:
            if isinstance(result, dict) and 'message' in result:
                return jsonify(result), status_code
            else:
                return jsonify({'message': str(result), 'error': 'login_failed'}), status_code
        
        return jsonify(result), status_code
    
    except Exception as e:
        # Rollback the session in case of an unexpected error
        db_session.rollback()
        return jsonify({'message': 'An unexpected error occurred', 'error': str(e)}), 500

@auth_bp.route('/register', methods=['POST'])
def register():
    if not request.is_json:
        return jsonify({'message': 'Content-Type must be application/json'}), 415
    
    data = request.json
    if not data:
        return jsonify({'message': 'Invalid request data'}), 400
    
    # Get the current database session
    db_session = get_db_session()
    
    try:
        # Create AuthService with the session
        auth_service = AuthService(db_session)
        
        success, result, status_code = auth_service.register(data)
        
        if not success:
            if isinstance(result, dict) and 'message' in result:
                return jsonify(result), status_code
            else:
                return jsonify({'message': str(result), 'error': 'registration_failed'}), status_code
        
        return jsonify(result), status_code
    
    except Exception as e:
        # Rollback the session in case of an unexpected error
        db_session.rollback()
        return jsonify({'message': 'An unexpected error occurred', 'error': str(e)}), 500