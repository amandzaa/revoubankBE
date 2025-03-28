import uuid
from datetime import datetime
from typing import Optional, List, Tuple
from flask import g
from sqlalchemy.orm import Session
from app.repositories.transaction import TransactionRepository
from app.utils import helpers
from app.utils.validator_schemas import TransactionCreate
from pydantic import ValidationError

class TransactionService:
    def __init__(self, db_session: Session):
        self.transaction_repository = TransactionRepository(db_session)

    def check_transaction_auth(self, transaction_id: str):
        """Check if the current user is authorized to access a transaction."""
        transaction = self.transaction_repository.find_by_id(transaction_id)
        
        if not transaction:
            return False, "Transaction not found!", 404
        
        # Assuming the transaction dict has an 'account' key with 'user_id'
        if transaction.get('account', {}).get('user_id') != g.current_user['id']:
            return False, "Unauthorized access to transaction!", 403
        
        return True, transaction, None

    def get_all_transactions(
        self, 
        account_id: str, 
        start_date: Optional[datetime] = None, 
        end_date: Optional[datetime] = None
    ) -> List[dict]:
        """Get transactions for a specific account with optional date filtering."""
        return [transaction.to_dict() for transaction in 
                self.transaction_repository.find_by_account_id(
                    account_id, 
                    start_date, 
                    end_date
                )]

    def get_user_transactions(
        self, 
        user_id: str, 
        account_id: Optional[str] = None, 
        start_date: Optional[datetime] = None, 
        end_date: Optional[datetime] = None
    ) -> List[dict]:
        """Get transactions for a specific user with optional filtering."""
        return [transaction.to_dict() for transaction in 
                self.transaction_repository.find_by_user_id(
                    user_id, 
                    account_id, 
                    start_date, 
                    end_date
                )]

    def get_transaction_by_id(self, transaction_id: str) -> Tuple[bool, dict, int]:
        """Retrieve a transaction by its ID with authorization check."""
        authorized, transaction, error_message = self.check_transaction_auth(transaction_id)
        
        if not authorized:
            return False, error_message, 403
        
        return True, transaction, 200

    def create_transaction(self, data: dict) -> Tuple[bool, dict, int]:
        """Create a new transaction with Pydantic validation."""
        try:
            # Additional fields validation using Pydantic
            # For transfer, you might need to adjust the schema or validate destination account separately
            if data.get('transaction_type') == 'transfer':
                # Ensure destination account ID is present
                if not data.get('destination_account_id'):
                    return False, 'Destination account ID is required for transfers!', 400
            
            # Validate the transaction data against the TransactionCreate schema
            validated_data = TransactionCreate(**{
                'account_id': data.get('account_id'),
                'amount': data.get('amount'),
                'transaction_type': data.get('transaction_type'),
                'currency': data.get('currency', 'USD'),  # Default currency if not provided
                'description': data.get('description', '')
            })

            # Check account authorization
            account_id = validated_data.account_id
            authorized, error_message, status_code = helpers.check_account_owner(account_id)
            if not authorized:
                return False, error_message, status_code

            try:
                # Create the primary transaction
                primary_transaction = self.transaction_repository.create(
                    account_id=validated_data.account_id,
                    transaction_type=validated_data.transaction_type,
                    amount=validated_data.amount,
                    description=validated_data.description
                )

                if not primary_transaction:
                    return False, 'Transaction creation failed', 500

                # Handle transfer specific logic
                if validated_data.transaction_type == 'transfer':
                    destination_account_id = data.get('destination_account_id')
                    # Create linked destination transaction
                    destination_transaction = self.transaction_repository.create(
                        account_id=destination_account_id,
                        transaction_type='deposit',
                        amount=validated_data.amount,
                        description=f"Transfer from account {account_id}",
                        linked_transaction_id=primary_transaction['id']
                    )

                    # Update primary transaction with linked transaction
                    if destination_transaction:
                        self.transaction_repository.update_linked_transaction(
                            primary_transaction['id'], 
                            destination_transaction['id']
                        )

                return True, {
                    'message': 'Transaction completed successfully!',
                    'transaction_id': primary_transaction['id']
                }, 201

            except Exception as e:
                return False, f'Transaction failed: {str(e)}', 500

        except ValidationError as e:
            # Handle Pydantic validation errors
            error_details = e.errors()
            error_messages = [f"{err['loc'][0]}: {err['msg']}" for err in error_details]
            return False, f"Validation failed: {', '.join(error_messages)}", 400

    def get_transaction_summary(
        self, 
        user_id: str, 
        start_date: Optional[datetime] = None, 
        end_date: Optional[datetime] = None
    ) -> dict:
        """Get transaction summary for a user."""
        return self.transaction_repository.get_transaction_summary(
            user_id, 
            start_date, 
            end_date
        )