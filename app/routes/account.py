import re
from flask import Blueprint, request, jsonify, g
from app.utils import helpers
from app.utils.auth import admin_required, token_required
from app.utils.validator_schemas import validate_required_fields
from app.services.account import AccountService
from app.utils.database_session_manager import db_session_manager

account_bp = Blueprint('account_bp', __name__, url_prefix='/revoubank/accounts')

@account_bp.route('/all', methods=['GET'])
@token_required
@admin_required
def get_all_accounts_all_users():
    with db_session_manager.session_scope():
        account_service = AccountService()
        accounts = account_service.get_all_accounts()
        account_list = [account.to_dict() for account in accounts]
        return jsonify(account_list), 200

@account_bp.route('/<string:user_id>', methods=['GET'])
@token_required
def get_all_accounts_by_user(user_id):
    is_owner, error_response, status_code = helpers.check_user_owner(user_id)
    if not is_owner:
        return error_response, status_code
    with db_session_manager.session_scope():
        account_service = AccountService()
        accounts = account_service.get_user_accounts(user_id)
        account_list = [account.to_dict() for account in accounts]
        return jsonify(account_list), 200

@account_bp.route('/<string:identifier>/info', methods=['GET'])
@token_required
def get_account_details_by_identifier(identifier):
    # Check if it's an account number or account id
    is_account_number = bool(re.fullmatch(r"ACC-\d+-\d+", identifier))
    is_owner, error_response, status_code = helpers.check_account_owner_by_identifier(
        identifier, is_account_number=is_account_number)
    if not is_owner:
        return error_response, status_code
    with db_session_manager.session_scope():
        account_service = AccountService()
        success, response_data, status_code = account_service.get_account_info_by_identifier(
            identifier, is_account_number=is_account_number)
        return jsonify(response_data), status_code

@account_bp.route('/<string:identifier>', methods=['PUT'])
@token_required
def update_account_by_identifier(identifier):
    is_account_number = bool(re.fullmatch(r"ACC-\d+-\d+", identifier))
    is_owner, error_response, status_code = helpers.check_account_owner_by_identifier(
        identifier, is_account_number=is_account_number)
    if not is_owner:
        return error_response, status_code
    with db_session_manager.session_scope():
        account_service = AccountService()
        try:
            result = account_service.update_account_info_by_identifier(
                identifier, is_account_number=is_account_number)
            return jsonify(result), 200
        except ValueError as e:
            return jsonify({'message': str(e)}), 400

@account_bp.route('/<string:identifier>', methods=['DELETE'])
@token_required
def delete_account_by_identifier(identifier):
    is_account_number = bool(re.fullmatch(r"ACC-\d+-\d+", identifier))
    is_owner, error_response, status_code = helpers.check_account_owner_by_identifier(
        identifier, is_account_number=is_account_number)
    if not is_owner:
        return error_response, status_code
    with db_session_manager.session_scope():
        account_service = AccountService()
        success, response, status_code = account_service.delete_account_by_identifier(
            identifier, is_account_number=is_account_number)
        if not success:
            return response, status_code
        return response, status_code
    
def generate_account_number():
    import random
    import time
    timestamp = int(time.time())
    random_num = random.randint(1000, 9999)
    return f"ACC-{timestamp}-{random_num}"

# @account_bp.route('/<string:account_id>/info', methods=['GET'])
# @token_required
# def get_account_details(account_id):
#     is_owner, error_response, status_code = helpers.check_account_owner(account_id)
#     if not is_owner:
#         return error_response, status_code
    
#     with db_session_manager.session_scope():
#         account_service = AccountService()
#         success, response_data, status_code = account_service.get_account_info(account_id)
#         return jsonify(response_data), status_code

# @account_bp.route('/<string:user_id>/create', methods=['POST'])
# @token_required
# def create_account_in_user(user_id):
#     is_owner, error_response, status_code = helpers.check_user_owner(user_id)
#     if not is_owner:
#         return error_response, status_code
    
#     data = request.json
#     valid, message = validate_required_fields(data, ['account_type', 'account_name', 'currency'])
#     if not valid:
#         return jsonify({'message': message}), 400
    
#     # Generate a unique account number if not provided
#     account_number = data.get('account_number')
#     if not account_number:
#         # Generate a unique account number
#         account_number = generate_account_number()
    
#     with db_session_manager.session_scope():
#         account_service = AccountService()
#         success, message, account_id = account_service.create_account(
#             user_id=user_id,
#             account_name=data.get('account_name'),
#             account_type=data.get('account_type'),
#             account_number=account_number,
#             currency=data.get('currency'),
#             initial_balance=data.get('initial_balance', 0)
#         )
        
#         if not success:
#             return jsonify({'message': message}), 400
        
#         return jsonify({
#             'message': 'Account created successfully!',
#             'account_id': account_id
#         }), 201


# @account_bp.route('/<string:account_id>', methods=['PUT'])
# @token_required
# def update_account(account_id):
#     is_owner, error_response, status_code = helpers.check_account_owner(account_id)
#     if not is_owner:
#         return error_response, status_code
#     with db_session_manager.session_scope():
#         account_service = AccountService()
#         try:
#             result = account_service.update_account_info(account_id)
#             return jsonify(result), 200
#         except ValueError as e:
#             return jsonify({'message': str(e)}), 400

# @account_bp.route('/<string:account_id>', methods=['DELETE'])
# @token_required
# def delete_account(account_id):
#     is_owner, error_response, status_code = helpers.check_account_owner(account_id)
#     if not is_owner:
#         return error_response, status_code
#     with db_session_manager.session_scope():
#         account_service = AccountService()
#         success, response, status_code = account_service.delete_account(account_id)
#         if not success:
#             return response, status_code
#         return response, status_code