from flask import Blueprint, request, jsonify
from app.services.auth import AuthService
from app.utils.database_session_manager import get_db_session

auth_bp = Blueprint('auth_bp', __name__, url_prefix='/revoubank')

@auth_bp.route('/login', methods=['POST'])
def login_user():
    if not request.is_json:
        return jsonify({'message': 'Content-Type must be application/json'}), 415

    data = request.get_json()
    if not data:
        return jsonify({'message': 'Invalid request data'}), 400

    db_session = get_db_session()

    try:
        auth_service = AuthService(db_session)

        success, result, status_code = auth_service.login(
            email=data.get('email'),
            password=data.get('password')
        )

        return jsonify(result), status_code

    except Exception as e:
        db_session.rollback()
        return jsonify({
            'message': 'An unexpected error occurred',
            'error': str(e)
        }), 500

@auth_bp.route('/register', methods=['POST'])
def register():
    if not request.is_json:
        return jsonify({'message': 'Content-Type must be application/json'}), 415

    data = request.get_json()
    if not data:
        return jsonify({'message': 'Invalid request data'}), 400

    db_session = get_db_session()

    try:
        auth_service = AuthService(db_session)

        success, result, status_code = auth_service.register(data)

        return jsonify(result), status_code

    except Exception as e:
        db_session.rollback()
        return jsonify({
            'message': 'An unexpected error occurred',
            'error': str(e)
        }), 500

@auth_bp.route('/ping', methods=['GET'])
def ping():
    return jsonify({'message': 'pong'}), 200
