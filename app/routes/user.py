from flask import Blueprint, g, request, jsonify
from app.utils.database_session_manager import get_db_session
from app.utils.auth import admin_required, token_required
from app.services.user import UserService

user_bp = Blueprint('user_bp', __name__, url_prefix='/revoubank/users')

@user_bp.route('/<int:user_id>', methods=['GET'])
@token_required
def get_user_profile(user_id):
    # Get database session
    db_session = get_db_session()
    
    try:
        user_service = UserService(db_session)
        success, response_data, status_code = user_service.get_info_user(user_id)
        return jsonify(response_data), status_code
    except Exception as e:
        return jsonify({'message': str(e)}), 500
    finally:
        db_session.close()

@user_bp.route('/<int:user_id>', methods=['PUT'])
@token_required
def update_user_profile(user_id):
    # Get request data
    data = request.json
    print(f"cek data{data}")
    
    # Get database session
    db_session = get_db_session()
    
    try:
        user_service = UserService(db_session)
        success, message, changes = user_service.update_user(user_id, data)
        
        if not success:
            db_session.rollback()
            return jsonify({'message': message}), 400
        
        db_session.commit()
        return jsonify({
            'message': 'Profile updated successfully!',
            'user_id': user_id,
            'changes': changes
        }), 200
    except Exception as e:
        db_session.rollback()
        return jsonify({'message': str(e)}), 500
    finally:
        db_session.close()

@user_bp.route('/all', methods=['GET'])
@token_required
@admin_required
def get_all_users():
    # Get database session
    db_session = get_db_session()
    
    try:
        user_service = UserService(db_session)
        users = user_service.get_all_users()
        
        users_list = [{
            'id': user.id,
            'username': user.username,
            'email': user.email
        } for user in users]
        
        return jsonify({"users": users_list})
    except Exception as e:
        return jsonify({'message': str(e)}), 500
    finally:
        db_session.close()

@user_bp.route('/<int:user_id>', methods=['DELETE'])
@token_required
def delete_user(user_id):
    # Get database session
    db_session = get_db_session()
    
    try:
        user_service = UserService(db_session)
        success, message = user_service.delete_user(user_id)
        
        if not success:
            db_session.rollback()
            return jsonify({'message': message}), 400
        
        db_session.commit()
        return jsonify({'message': message}), 200
    except Exception as e:
        db_session.rollback()
        return jsonify({'message': str(e)}), 500
    finally:
        db_session.close()
    
@user_bp.route('/debug-user', methods=['GET'])
@token_required
def debug_user():
    user_data = {
        'type': str(type(g.current_user)),
        'dir': str(dir(g.current_user)),
        'is_dict': isinstance(g.current_user, dict)
    }
    
    # If it's a dictionary
    if isinstance(g.current_user, dict):
        user_data['keys'] = list(g.current_user.keys())
    # If it's an object
    else:
        try:
            user_data['has_is_admin'] = hasattr(g.current_user, 'is_admin')
            if hasattr(g.current_user, 'is_admin'):
                user_data['is_admin_value'] = g.current_user.is_admin
        except:
            pass
    
    return jsonify(user_data), 200