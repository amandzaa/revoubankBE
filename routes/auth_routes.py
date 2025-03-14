from flask import Blueprint, request, jsonify
from services.auth_service import AuthService

auth_service = AuthService()
auth_bp = Blueprint('auth_bp', __name__, url_prefix='/revoubank')

@auth_bp.route('/login', methods=['POST'])
def login_user():
    if not request.is_json:
        return jsonify({'message': 'Content-Type must be application/json'}), 415
    data = request.json
    if not data:
        return jsonify({'message': 'Invalid request data'}), 400
    success, result, status_code = auth_service.login(
        email=data.get('email'),
        password=data.get('password')
    )
    if not success:
        if isinstance(result, dict) and 'message' in result:
            return jsonify(result), status_code
        else:
            return jsonify({'message': str(result), 'error': 'registration_failed'}), status_code
    return jsonify(result), status_code

@auth_bp.route('/register', methods=['POST'])
def register():
    if not request.is_json:
        return jsonify({'message': 'Content-Type must be application/json'}), 415
    data = request.json
    if not data:
        return jsonify({'message': 'Invalid request data'}), 400
    success, result, status_code = auth_service.register(data)
    if not success:
        if isinstance(result, dict) and 'message' in result:
            return jsonify(result), status_code
        else:
            return jsonify({'message': str(result), 'error': 'registration_failed'}), status_code
    return jsonify(result), status_code
