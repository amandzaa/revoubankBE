from flask import Blueprint, request, jsonify
from utils.auth import admin_required, token_required
from services.user_service import UserService
from . import user_bp

user_bp = Blueprint('user_bp', __name__, url_prefix='/revoubank/users')
user_service = UserService()
@user_bp.route('/<string:user_id>', methods=['GET'])
@token_required
def get_user_profile(user_id):
    success, response_data, status_code = user_service.get_info_user(user_id)
    # Return the appropriate response
    return jsonify(response_data), status_code

@user_bp.route('/<string:user_id>', methods=['PUT'])
@token_required
def update_user_profile(user_id):
    data = request.json
    success, message, changes = user_service.update_user(user_id, data)
    if not success:
        return jsonify({'message': message}), 400
    return jsonify({
        'message': 'Profile updated successfully!',
        'user_id': user_id,
        'changes': changes
    }), 200

@user_bp.route('/all', methods =['GET'])
@token_required
@admin_required
def get_all_users():
    users = user_service.get_all_users()
    users_list = [{
        'id': user['id'],
        'name': user['name'],
        'email': user['email']
    } for user in users]
    return jsonify({"users": users_list})
