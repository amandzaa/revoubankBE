from datetime import datetime
from flask import g, jsonify, request
from repositories.account_repository import AccountRepository
from utils import helpers
from utils.db import get_db

class AccountService:
    def __init__(self):
        self.repository = AccountRepository()
    
    def check_account_owner(self,account_id):
        """Check if the current user owns the specified account."""
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT user_id FROM accounts WHERE id = ?", (account_id,))
        account = cursor.fetchone()
        print(account)
        if not account:
            return False, "Account not found!", 404
        current_user = g.current_user
        if current_user.get('is_admin', False):
            return True, None, None
        if account['user_id'] != g.current_user['id']:
            return False, "Unauthorized access to account!", 403
        return True, None, None
    
    def get_account_balance(self, account_id):
        account = self.repository.find_by_id(account_id)
        if not account:
            return None
        return account['balance']
    
    def update_account_balance(self, account_id, amount, is_credit=True):
        if amount <= 0:
            return False, "Amount must be positive", None
        # Get account from repository
        account = self.repository.find_by_id(account_id)
        if not account:
            return False, "Account not found", None
        # Check if account is active
        if account['status'] != 'active':
            return False, f"Cannot modify balance of {account['status']} account", None
        current_balance = account['balance']
        # Calculate new balance
        if is_credit:
            new_balance = current_balance + amount
        else:
            # Check for sufficient funds for debit operations
            if current_balance < amount:
                return False, "Insufficient funds", current_balance
            new_balance = current_balance - amount
        # Update the balance through the repository
        success, message = self.repository.update_balance(account_id, new_balance)
        if not success:
            return False, message, current_balance
        return True, "Balance updated successfully", new_balance
    
    def create_account(self, userid, account_name, account_type, currency, initial_balance, status):
        # Validate account type
        valid_types = ['checking', 'savings', 'investment']
        if account_type not in valid_types:
            return False, f"Invalid account type. Must be one of: {', '.join(valid_types)}", None
        # Create account through repository
        return self.repository.create(userid, account_type, account_name, currency, initial_balance, status)
    
    def close_account(self, account_id):
        is_owner, error_response, status_code = self.check_account_owner(account_id)
        if not is_owner:
            return False, error_response, status_code
        # Get account balance
        account = self.repository.find_by_id(account_id)
        if account['balance'] > 0:
            return False, jsonify({'message': 'Cannot close account with positive balance!'}), 400
        data = request.json
        if not data:
            return jsonify({'message': 'No data provided!'}), 400
        updates = {}
        allowed_fields = ['account_name', 'account_type', 'status']
        for field in allowed_fields:
            if field in data and data[field]:
                updates[field] = data[field]
        if not updates:
            return jsonify({'message': 'No valid fields to update!'}), 400
        # Add updated_at timestamp
        updates['updated_at'] = datetime.now()
        # Close account through repository
        success, message = self.repository.update_status(account_id, 'closed')
        if not success:
            return False, jsonify({'message': message}), 500
        return True, jsonify({'message': 'Account closed successfully'}), 200
    
    def get_user_accounts(self, user_id=None):
        if user_id is None:
            user_id = g.current_user['id']
        return self.repository.find_by_user_id(user_id)
    
    def get_all_accounts(self, user_id=None):
        if user_id is None:
            user_id = g.current_user['id']
        return self.repository.find_all_accounts()
    
    def get_info_accounts(self, account_id):
        print(f"fetching account from service: {account_id}")
        account_info = self.repository.find_by_id(account_id)
        if not account_info:
            return False, {'message': 'Account not found!'}, 404
        else:
            account_info = dict(account_info)
        return True, account_info, 200
    
    def delete_account(self, account_id):
        is_owner, error_response, status_code = self.check_account_owner(account_id)
        if not is_owner:
            return False, error_response, status_code
        # Get account balance
        account = self.repository.find_by_id(account_id)
        if account['balance'] > 0:
            return False, jsonify({'message': 'Cannot close account with positive balance!'}), 400
        # delete account through repository
        success, message = self.repository.delete(account_id)
        if not success:
            return False, jsonify({'message': message}), 500
        return True, jsonify({'message': 'Account deleted successfully'}), 200
    
    def update_account_info(self, account_id):
        authorized, error_response, status_code = self.check_account_owner(account_id)
        if not authorized:  
            return error_response, status_code
        data = request.json
        if not data:
            return jsonify({'message': 'No data provided!'}), 400
        updates = {}
        allowed_fields = ['account_name', 'account_type', 'status']
        for field in allowed_fields:
            if field in data and data[field]:
                updates[field] = data[field]
        if not updates:
            return jsonify({'message': 'No valid fields to update!'}), 400
        # Add updated_at timestamp
        updates['updated_at'] = datetime.now()
        return self.repository.update_account(account_id, updates)
    