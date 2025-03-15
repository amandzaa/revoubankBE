from flask import Blueprint, request, jsonify
from utils import helpers
from utils.auth import admin_required, token_required
from services.transaction_service import TransactionService

transaction_bp = Blueprint('transaction_bp', __name__, url_prefix='/revoubank/transactions')

@transaction_bp.route('/all', methods=['GET'])
@token_required
@admin_required
def get_all_transactions_all_users():
    account_id = request.args.get('account_id')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    transactions = TransactionService.get_all_transactions(
        account_id=account_id,
        start_date=start_date,
        end_date=end_date
    )
    return jsonify(transactions)

@transaction_bp.route('/<string:user_id>', methods=['GET'])
@token_required
def get_all_transactions_by_account_id(user_id):
    authorized, error_message, status_code = helpers.check_user_owner(user_id)
    if not authorized:
        return error_message, status_code
    account_id = request.args.get('account_id')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    transactions = TransactionService.get_user_transactions(
        user_id=user_id,
        account_id=account_id,
        start_date=start_date,
        end_date=end_date
    )
    return jsonify(transactions)

@transaction_bp.route('/<string:transaction_id>/info', methods=['GET'])
@token_required
def get_transaction_info_by_transaction_id(transaction_id):
    authorized, transaction, error_message = TransactionService.check_transaction_auth(transaction_id)
    if not authorized:
        return jsonify({'message': transaction}), error_message
    success, response_data, status_code = TransactionService.get_transaction_by_id(transaction_id)
    return jsonify(response_data), status_code

@transaction_bp.route('/create', methods=['POST'])
@token_required
def create_transaction():
    data = request.json
    success, result, status_code = TransactionService.create_transaction(data)
    if not success:
        return jsonify({'message': result}), status_code
    return jsonify(result), status_code
