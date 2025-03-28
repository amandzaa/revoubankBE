from datetime import datetime
from typing import Tuple, List, Dict, Any, Optional
from flask import g, request, jsonify
from sqlalchemy.orm import Session

from app.repositories.account import AccountRepository
from app.utils.database_session_manager import get_db_session

class AccountService:
    def __init__(self, session: Optional[Session] = None):
        self.db_session = session or get_db_session()
        self.repository = AccountRepository(self.db_session)
    
    def get_account_balance(self, account_id: str) -> Optional[float]:
        account = self.repository.find_by_id(account_id)
        return account.balance if account else None
    
    def update_account_balance(self, account_id: str, amount: float, is_credit: bool = True) -> Tuple[bool, str, Optional[float]]:
        if amount <= 0:
            return False, "Amount must be positive", None
        
        # Get account from repository
        account = self.repository.find_by_id(account_id)
        if not account:
            return False, "Account not found", None
        
        # Check if account is active
        if account.status != 'active':
            return False, f"Cannot modify balance of {account.status} account", None
        
        current_balance = account.balance
        
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
    
    def create_account(self, user_id: str, account_name: str, account_type: str, 
                       currency: str, initial_balance: float = 0, 
                       status: str = 'active') -> Tuple[bool, str, Optional[str]]:
        valid_types = ['checking', 'savings', 'investment']
        if account_type not in valid_types:
            return False, f"Invalid account type. Must be one of: {', '.join(valid_types)}", None
        
        # Create account through repository
        return self.repository.create(
            user_id, 
            account_type, 
            account_name, 
            currency, 
            initial_balance, 
            status
        )
    
    def close_account(self, account_id: str) -> Tuple[bool, Any, int]:
        """
        Close an account
        
        :param account_id: ID of the account to close
        :return: Tuple of (success, response, status_code)
        """
        account = self.repository.find_by_id(account_id)
        if not account:
            return False, jsonify({'message': 'Account not found!'}), 404
        
        if account.balance > 0:
            return False, jsonify({'message': 'Cannot close account with positive balance!'}), 400
        
        # Close account through repository
        success, message = self.repository.update_status(account_id, 'closed')
        if not success:
            return False, jsonify({'message': message}), 500
        
        return True, jsonify({'message': 'Account closed successfully'}), 200
    
    def get_user_accounts(self, user_id: Optional[str] = None) -> List[Any]:
        if user_id is None:
            user_id = g.current_user['id']
        return self.repository.find_by_user_id(user_id)
    
    def get_all_accounts(self) -> List[Any]:
        return self.repository.find_all_accounts()
    
    def get_account_info(self, account_id: str) -> Tuple[bool, Dict[str, Any], int]:
        account_info = self.repository.find_account_info(account_id)
        if not account_info:
            return False, {'message': 'Account not found!'}, 404
        
        return True, account_info, 200
    
    def delete_account(self, account_id: str) -> Tuple[bool, Any, int]:
        account = self.repository.find_by_id(account_id)
        if not account:
            return False, jsonify({'message': 'Account not found!'}), 404
        
        if account.balance > 0:
            return False, jsonify({'message': 'Cannot delete account with positive balance!'}), 400
        
        success, message = self.repository.delete(account_id)
        if not success:
            return False, jsonify({'message': message}), 500
        
        return True, jsonify({'message': 'Account deleted successfully'}), 200
    
    def update_account_info(self, account_id: str) -> Dict[str, str]:
        data = request.json
        if not data:
            raise ValueError('No data provided!')
        
        updates = {}
        allowed_fields = ['account_name', 'account_type', 'currency', 'status']
        for field in allowed_fields:
            if field in data and data[field]:
                updates[field] = data[field]
        
        if not updates:
            raise ValueError('No valid fields to update!')
        
        # Add updated_at timestamp
        updates['updated_at'] = datetime.now()
        
        return self.repository.update_account(account_id, updates)