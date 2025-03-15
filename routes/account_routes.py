from flask import Blueprint, request, jsonify, g
from utils import helpers
from utils.auth import admin_required, token_required
from utils.validators import validate_required_fields
from services.account_service import AccountService

account_bp = Blueprint('account_bp', __name__, url_prefix='/revoubank/accounts')
account_service = AccountService()

@account_bp.route('/all', methods=['GET'])
@token_required
@admin_required
def get_all_accounts_all_users():
    user_id = g.current_user['id']
    accounts = account_service.get_all_accounts(user_id)
    return jsonify([dict(account) for account in accounts])

@account_bp.route('/<string:user_id>', methods=['GET'])
@token_required
def get_all_accounts_by_user(user_id):
    is_owner, error_response, status_code = helpers.check_user_owner(user_id)
    if not is_owner:
        return error_response, status_code
    accounts = account_service.get_user_accounts(user_id)
    return jsonify([dict(account) for account in accounts])

@account_bp.route('/<string:account_id>/info', methods=['GET'])
@token_required
def get_account_details(account_id):
    is_owner, error_response, status_code = helpers.check_account_owner(account_id)
    if not is_owner:
        return error_response, status_code
    success, response_data, status_code = account_service.get_info_accounts(account_id)
    return jsonify(response_data), status_code

@account_bp.route('/<string:user_id>/create', methods=['POST'])
@token_required
def create_account_in_user(user_id):
    is_owner, error_response, status_code = helpers.check_user_owner(user_id)
    if not is_owner:
        return error_response, status_code
    data = request.json
    valid, message = validate_required_fields(data, ['account_type', 'currency'])
    if not valid:
        return jsonify({'message': message}), 400
    success, message, account_id = account_service.create_account(
        userid=user_id,
        account_name=data.get('account_name', ''),
        account_type=data.get('account_type'),
        currency= data.get('currency'),
        initial_balance=data.get('initial_balance', 0),
        status='active'
    )
    if not success:
        return jsonify({'message': message}), 400
    return jsonify({
        'message': 'Account created successfully!',
        'account_id': account_id
    }), 201

@account_bp.route('/<string:account_id>', methods=['PUT'])
@token_required
def update_account(account_id):
    is_owner, error_response, status_code = helpers.check_account_owner(account_id)
    if not is_owner:
        return error_response, status_code
    return account_service.update_account_info(account_id)

@account_bp.route('/<string:account_id>', methods=['DELETE'])
@token_required
def delete_account(account_id):
    is_owner, error_response, status_code = helpers.check_account_owner(account_id)
    if not is_owner:
        return error_response, status_code
    success, response, status_code = account_service.delete_account(account_id)
    if not success:
        return response, status_code
    return response, status_code

@account_bp.route('/<string:account_id>/status', methods=['PUT'])
@token_required
@admin_required
def update_account_status(account_id):
    is_owner, error_response, status_code = helpers.check_account_owner(account_id)
    if not is_owner:
        return error_response, status_code
    success, response, status_code = account_service.close_account(account_id)
    if not success:
        return response, status_code
    return response, status_code

@account_bp.route('/<string:account_id>/balance', methods=['GET'])
@token_required
def get_balance_by_account_id(account_id):
    authorized, error_response, status_code = helpers.check_account_owner(account_id)
    if not authorized:
        return error_response, status_code
    balance = account_service.get_account_balance(account_id)
    if balance is None:
        return jsonify({'message': 'Account not found!'}), 404
    return jsonify({
        'account_id': account_id,
        'balance': balance
    })
