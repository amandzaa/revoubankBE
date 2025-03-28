from flask import g, jsonify
from app.repositories.account import AccountRepository
from app.repositories.user import UserRepository

def check_account_owner(account_id):
    if not account_id:
        return False, jsonify({'message': 'Account ID is required!'}), 400

    account_repository = AccountRepository()
    account = account_repository.find_by_id(account_id)

    if not account:
        return False, jsonify({'message': 'Account not found!'}), 404

    current_user = g.current_user

    if current_user.get('is_admin', False):
        return True, None, None  # Admin users can access any account

    # Check if the current user is the owner of the account
    if account['user_id'] != current_user['id']:
        return False, jsonify({'message': 'Unauthorized access to this account!'}), 403

    return True, None, None

def check_user_owner(user_id):
    if not user_id:
        return False, jsonify({'message': 'User ID is required!'}), 400

    user_repository = UserRepository()
    user = user_repository.find_by_id(user_id)

    if not user:
        return False, jsonify({'message': 'User not found!'}), 404

    current_user = g.current_user

    if current_user.get('is_admin', False):
        return True, None, None  # Admin users can access any user account

    if current_user['id'] != user_id:
        return False, jsonify({'message': 'Unauthorized access to this user account!'}), 403

    return True, None, None