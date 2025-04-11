from datetime import datetime, timedelta
from typing import Optional, List, Tuple
from flask import g, jsonify
from sqlalchemy.orm import Session
from app.models.transaction import TransactionType
from app.repositories.account import AccountRepository
from app.repositories.transaction import TransactionRepository
from app.utils import helpers
from sqlalchemy.exc import SQLAlchemyError

from app.utils.database_session_manager import DatabaseSessionManager, get_db_session

class TransactionService:
    def __init__(self, db_session: Session):
        self.transaction_repository = TransactionRepository(db_session)

    def check_transaction_auth(self, transaction_id: str):
        if not transaction_id:
            return False, jsonify({'message': 'Transaction ID is required!'}), 400
        
        # Convert transaction_id to int if it's a string
        try:
            transaction_id_int = int(transaction_id) if isinstance(transaction_id, str) else transaction_id
        except ValueError:
            return False, jsonify({'message': 'Invalid Transaction ID format!'}), 400
        
        # Use the session_scope context manager
        db_session_manager = DatabaseSessionManager()
        with db_session_manager.session_scope():
            # Get the current database session
            session = get_db_session()
            
            # Properly initialize the repository with the session
            transaction_repository = TransactionRepository(db=session)
            transaction = transaction_repository.find_by_id(transaction_id_int)
            
            if not transaction:
                return False, jsonify({'message': 'Transaction not found!'}), 404
            
            current_user = g.current_user
            
            # Check if user is admin
            if current_user.get('is_admin', False):
                return True, None, None  # Admin users can access any transaction
            
            # Convert current user ID to int for comparison if needed
            current_user_id = int(current_user['id']) if isinstance(current_user['id'], str) else current_user['id']
            
            # Get the account repository to check ownership
            account_repository = AccountRepository(db=session)
            
            # Check if user owns either the source or destination account
            if transaction.from_account_id:
                from_account = account_repository.find_by_id(transaction.from_account_id)
                if from_account and from_account.user_id == current_user_id:
                    return True, None, None
                    
            if transaction.to_account_id:
                to_account = account_repository.find_by_id(transaction.to_account_id)
                if to_account and to_account.user_id == current_user_id:
                    return True, None, None
            
            # If we reach here, the user doesn't own either account
            return False, jsonify({'message': 'Unauthorized access to this transaction!'}), 403

    # def get_all_transactions(
    #     self, 
    #     account_id: str, 
    #     start_date: Optional[datetime] = None, 
    #     end_date: Optional[datetime] = None
    # ) -> List[dict]:
    #     """Get transactions for a specific account with optional date filtering."""
    #     return [transaction.to_dict() for transaction in 
    #             self.transaction_repository.find_by_account_id(
    #                 account_id, 
    #                 start_date, 
    #                 end_date
    #             )]
    
    def get_all_transactions_admin(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[dict]:
        """Get all transactions in the system (admin only)."""
        return [transaction.to_dict() for transaction in 
                self.transaction_repository.get_all_transactions(
                    start_date, 
                    end_date
                )]

    def get_user_transactions(self, user_id, account_id=None, start_date=None, end_date=None):
        """Get transactions for a specific user, optionally filtered by account and date range."""
        try:
            # Parse dates if they're strings
            parsed_start_date = None
            parsed_end_date = None
            
            if start_date and isinstance(start_date, str):
                try:
                    parsed_start_date = datetime.strptime(start_date, "%Y-%m-%d")
                except ValueError:
                    pass
                    
            if end_date and isinstance(end_date, str):
                try:
                    parsed_end_date = datetime.strptime(end_date, "%Y-%m-%d")
                    # Add 1 day to include the entire end date
                    parsed_end_date = parsed_end_date + timedelta(days=1)
                except ValueError:
                    pass
            
            # Call repository method
            return self.transaction_repository.find_by_user_id(
                user_id=user_id,
                account_id=account_id,
                start_date=parsed_start_date,
                end_date=parsed_end_date
            )
            
        except Exception as e:
            print(f"Error getting user transactions: {str(e)}")
            raise

    def get_transaction_by_id(self, transaction_id: str) -> Tuple[bool, dict, int]:
        transaction_info = self.transaction_repository.find_transaction_info(transaction_id)
        if not transaction_info:
            return False, {'message': 'Account not found!'}, 404
        return True, transaction_info, 200

    def create_transaction(self, data: dict) -> Tuple[bool, dict, int]:
        try:
            # Extract data from request
            transaction_type = data.get('transaction_type') 
            amount = data.get('amount')
            description = data.get('description', '')
            
            from_account_identifier = data.get('from_account')
            to_account_identifier = data.get('to_account')

            # Check both from and to account formats
            from_is_acc_num = from_account_identifier and helpers.is_account_number_format(from_account_identifier)
            to_is_acc_num = to_account_identifier and helpers.is_account_number_format(to_account_identifier)

            # Only use account numbers if BOTH are account numbers (or only one exists and it's valid)
            use_account_numbers = (from_is_acc_num if from_account_identifier else True) and \
                                (to_is_acc_num if to_account_identifier else True)
            
            # Validate required fields
            if not transaction_type or transaction_type not in [t.value for t in TransactionType]:
                return False, f'Valid transaction type is required! Must be one of: {", ".join([t.value for t in TransactionType])}', 400
                
            if not amount or not isinstance(amount, (int, float)) or amount <= 0:
                return False, 'Valid positive amount is required!', 400
            
            account_repository = AccountRepository(self.db_session)
            
            def validate_and_get_account(identifier_key, error_message):
                if identifier_key not in data or not data.get(identifier_key):
                    return False, f'{error_message} is required!', 400, None
                
                account_identifier = data.get(identifier_key)
                
                # Get account by identifier
                if use_account_numbers:
                    account = account_repository.find_by_account_number(account_identifier)
                else:
                    account = account_repository.find_by_id(account_identifier)
                    
                # Verify account exists
                if not account:
                    account_type = "source" if identifier_key == "from_account" else "destination"
                    return False, f'{account_type.capitalize()} account not found!', 404, None
                    
                # Check authorization
                authorized, error_message, status_code = helpers.check_account_owner_by_identifier(
                    account_identifier, is_account_number=use_account_numbers)
                if not authorized:
                    return False, error_message, status_code, None
                    
                return True, "", 200, account
            
            # Initialize account IDs
            from_account_id = None
            to_account_id = None
            
            # Handle different transaction types
            if transaction_type == TransactionType.TRANSFER.value:
                # Validate and get source account
                success, message, status, from_account = validate_and_get_account(
                    'from_account', 'Source account identifier')
                if not success:
                    return False, message, status
                from_account_id = from_account.id
                
                # Validate and get destination account
                success, message, status, to_account = validate_and_get_account(
                    'to_account', 'Destination account identifier')
                if not success:
                    return False, message, status
                to_account_id = to_account.id
                
            elif transaction_type == TransactionType.DEPOSIT.value:
                # Only need destination account for deposits
                success, message, status, to_account = validate_and_get_account(
                    'to_account', 'Destination account identifier')
                if not success:
                    return False, message, status
                to_account_id = to_account.id
                
            elif transaction_type == TransactionType.WITHDRAWAL.value:
                # Only need source account for withdrawals
                success, message, status, from_account = validate_and_get_account(
                    'from_account', 'Source account identifier')
                if not success:
                    return False, message, status
                from_account_id = from_account.id
                    
            elif transaction_type == TransactionType.PAYMENT.value:
                # For payments, typically from user account to external entity
                success, message, status, from_account = validate_and_get_account(
                    'from_account', 'Source account identifier')
                if not success:
                    return False, message, status
                from_account_id = from_account.id
                    
            elif transaction_type == TransactionType.REFUND.value:
                # For refunds, typically to user account from external entity
                success, message, status, to_account = validate_and_get_account(
                    'to_account', 'Destination account identifier')
                if not success:
                    return False, message, status
                to_account_id = to_account.id
                    
            elif transaction_type == TransactionType.FEE.value:
                # Fees are deducted from a user's account
                success, message, status, from_account = validate_and_get_account(
                    'from_account', 'Source account identifier (for FEE)')
                if not success:
                    return False, message, status
                from_account_id = from_account.id

            elif transaction_type == TransactionType.INTEREST.value:
                # Interest is added to a user's account
                success, message, status, to_account = validate_and_get_account(
                    'to_account', 'Destination account identifier (for INTEREST)')
                if not success:
                    return False, message, status
                to_account_id = to_account.id
                    
            elif transaction_type == TransactionType.REVERSAL.value:
                original_transaction_id = data.get('original_transaction_id')
                
                if not original_transaction_id:
                    return False, 'Original transaction ID is required for reversals!', 400
                    
                original_transaction = self.transaction_repository.find_by_id(original_transaction_id)
                
                if not original_transaction:
                    return False, 'Original transaction not found!', 404

                # Reverse the direction of funds
                reversed_from_account_id = original_transaction.get('to_account_id')
                reversed_to_account_id = original_transaction.get('from_account_id')

                # Validate from_account using ID (we already know the ID here)
                if reversed_from_account_id:
                    authorized, error_message, status_code = helpers.check_account_owner(reversed_from_account_id)
                    if not authorized:
                        return False, error_message, status_code

                from_account_id = reversed_from_account_id
                to_account_id = reversed_to_account_id

            else:
                # Generic case for other transaction types
                from_account_id = data.get('from_account_id')
                to_account_id = data.get('to_account_id')
            
            # Transaction creation code
            new_transaction = self.transaction_repository.create(
                from_account_id=from_account_id,
                to_account_id=to_account_id,
                amount=amount,
                transaction_type=transaction_type,
                description=description
            )
            
            return True, {
                'message': 'Transaction completed successfully!',
                'transaction': new_transaction
            }, 201
                
        except ValueError as e:
            # Handle validation errors like insufficient funds
            return False, str(e), 400
        except SQLAlchemyError as e:
            # Handle database errors
            return False, f'Database error: {str(e)}', 500
        except Exception as e:
            # Handle other errors
            return False, f'Transaction failed: {str(e)}', 500

    # def get_transaction_summary(
    #     self, 
    #     user_id: str, 
    #     start_date: Optional[datetime] = None, 
    #     end_date: Optional[datetime] = None
    # ) -> dict:
    #     """Get transaction summary for a user."""
    #     return self.transaction_repository.get_transaction_summary(
    #         user_id, 
    #         start_date, 
    #         end_date
    #     )
    
    def check_transaction_auth_by_identifier(self, identifier: str, is_transaction_number: bool = False):
        if not identifier:
            return False, jsonify({'message': 'Transaction identifier is required!'}), 400
        
        # Get the transaction using the appropriate method
        print(f" cek identifier {is_transaction_number}")
        if is_transaction_number:
            transaction = self.transaction_repository.find_by_transaction_number(identifier)
        else:
            # Convert transaction_id to int if it's a string
            try:
                transaction_id_int = int(identifier) if isinstance(identifier, str) else identifier
            except ValueError:
                return False, jsonify({'message': 'Invalidxx Transaction ID format!'}), 400
            
            transaction = self.transaction_repository.find_by_id(transaction_id_int)
        
        if not transaction:
            return False, jsonify({'message': 'Transaction not found!'}), 404
        
        current_user = g.current_user
        
        # Check if user is admin
        if current_user.get('is_admin', False):
            return True, None, None  # Admin users can access any transaction
        
        # Convert current user ID to int for comparison if needed
        current_user_id = int(current_user['id']) if isinstance(current_user['id'], str) else current_user['id']
        
        # Get the account repository to check ownership
        db_session_manager = DatabaseSessionManager()
        with db_session_manager.session_scope():
            session = get_db_session()
            account_repository = AccountRepository(db=session)
            
            # Check if user owns either the source or destination account
            if transaction.from_account_id:
                from_account = account_repository.find_by_id(transaction.from_account_id)
                if from_account and from_account.user_id == current_user_id:
                    return True, None, None
                    
            if transaction.to_account_id:
                to_account = account_repository.find_by_id(transaction.to_account_id)
                if to_account and to_account.user_id == current_user_id:
                    return True, None, None
            
        # If we reach here, the user doesn't own either account
        return False, jsonify({'message': 'Unauthorized access to this transaction!'}), 403 
    
    def get_transaction_by_identifier(self, identifier: str, is_transaction_number: bool = False) -> Tuple[bool, dict, int]:
        if is_transaction_number:
            transaction = self.transaction_repository.find_by_transaction_number(identifier)
            if not transaction:
                return False, {'message': 'Transaction not found!'}, 404
            return True, transaction.to_dict(), 200
        else:
            return self.get_transaction_by_id(identifier)
    
    