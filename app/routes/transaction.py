from flask import Blueprint, request, jsonify
from app.utils import helpers
from app.utils.auth import admin_required, token_required
from app.utils.database_session_manager import get_db_session
from app.services.transaction import TransactionService

transaction_bp = Blueprint('transaction_bp', __name__, url_prefix='/revoubank/transactions')

@transaction_bp.route('/all', methods=['GET'])
@token_required
@admin_required
def get_all_transactions_all_users():
    # Get database session
    db_session = get_db_session()
    
    # Create service instance
    transaction_service = TransactionService(db_session)
    
    # Parse query parameters
    account_id = request.args.get('account_id')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    try:
        # Convert dates if needed (you might want to add date parsing logic)
        transactions = transaction_service.get_all_transactions(
            account_id=account_id,
            start_date=start_date,
            end_date=end_date
        )
        
        # Convert transactions to list of dictionaries if needed
        return jsonify([transaction.to_dict() for transaction in transactions])
    
    except Exception as e:
        return jsonify({'message': str(e)}), 500
    finally:
        db_session.close()

@transaction_bp.route('/<string:user_id>', methods=['GET'])
@token_required
def get_all_transactions_by_account_id(user_id):
    # Check user authorization
    authorized, error_message, status_code = helpers.check_user_owner(user_id)
    if not authorized:
        return error_message, status_code
    
    # Get database session
    db_session = get_db_session()
    
    # Create service instance
    transaction_service = TransactionService(db_session)
    
    # Parse query parameters
    account_id = request.args.get('account_id')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    try:
        # Convert dates if needed (you might want to add date parsing logic)
        transactions = transaction_service.get_user_transactions(
            user_id=user_id,
            account_id=account_id,
            start_date=start_date,
            end_date=end_date
        )
        
        # Convert transactions to list of dictionaries if needed
        return jsonify([transaction.to_dict() for transaction in transactions])
    
    except Exception as e:
        return jsonify({'message': str(e)}), 500
    finally:
        db_session.close()

@transaction_bp.route('/<string:transaction_id>/info', methods=['GET'])
@token_required
def get_transaction_info_by_transaction_id(transaction_id):
    # Get database session
    db_session = get_db_session()
    
    # Create service instance
    transaction_service = TransactionService(db_session)
    
    try:
        # Check transaction authorization
        authorized, transaction, error_message = transaction_service.check_transaction_auth(transaction_id)
        if not authorized:
            return jsonify({'message': error_message}), 403
        
        # Get transaction details
        success, response_data, status_code = transaction_service.get_transaction_by_id(transaction_id)
        
        return jsonify(response_data), status_code
    
    except Exception as e:
        return jsonify({'message': str(e)}), 500
    finally:
        db_session.close()

@transaction_bp.route('/create', methods=['POST'])
@token_required
def create_transaction():
    # Get database session
    db_session = get_db_session()
    
    # Create service instance
    transaction_service = TransactionService(db_session)
    
    # Get request data
    data = request.json
    
    try:
        # Create transaction
        success, result, status_code = transaction_service.create_transaction(data)
        
        # Commit the transaction if successful
        if success:
            db_session.commit()
        else:
            db_session.rollback()
        
        # Return response
        if not success:
            return jsonify({'message': result}), status_code
        
        return jsonify(result), status_code
    
    except Exception as e:
        db_session.rollback()
        return jsonify({'message': str(e)}), 500
    finally:
        db_session.close()