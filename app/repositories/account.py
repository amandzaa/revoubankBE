from datetime import datetime
from typing import Any, Optional, Tuple, List, Dict
from sqlalchemy import func
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from app.models.account import Account

class AccountRepository:
    def __init__(self, db: Session):
        from app.utils.database_session_manager import get_db_session
        self.db = db if db is not None else get_db_session()

    def find_by_id(self, account_id: str) -> Optional[Account]:
        return self.db.query(Account).filter(Account.id == account_id).first()
    
    def find_by_user_id(self, user_id: int) -> List[Account]:
        return self.db.query(Account).filter(Account.user_id == user_id).all()
    
    def find_all_accounts(self) -> List[Account]:
        return self.db.query(Account).all()
    
    def find_account_info(self, account_id: str) -> Optional[Dict]:
        account = self.db.query(Account).filter(Account.id == account_id).first()
        return account.to_dict() if account else None
    def find_by_account_number(self, account_number: str) -> Optional[Account]:
        return self.db.query(Account).filter(Account.account_number == account_number).first()
    
    def create(
        self, 
        user_id: str,
        account_name: str, 
        account_type: str,
        account_number: str,
        currency: str, 
        initial_balance: float = 0
    ) -> Tuple[bool, str, Optional[str]]:
        if initial_balance < 0:
            return False, "Initial balance cannot be negative", None
        
        try:
            # Convert user_id to integer
            user_id_int = int(user_id)
            
            # Get the next ID value
            max_id = self.db.query(func.max(Account.id)).scalar() or 0
            next_id = max_id + 1
            
            new_account = Account(
                id=next_id,  # Explicitly set the ID
                user_id=user_id_int,
                account_name=account_name,
                account_type=account_type,
                account_number=account_number,
                currency=currency,
                balance=initial_balance
            )
            
            self.db.add(new_account)
            self.db.commit()
            self.db.refresh(new_account)
            
            return True, "Account created successfully", new_account.id
        except SQLAlchemyError as e:
            self.db.rollback()
            return False, f"Failed to create account: {str(e)}", None
        except Exception as e:
            self.db.rollback()
            return False, f"An error occurred: {str(e)}", None
    
    def update_balance(self, account_id: str, new_balance: float) -> Tuple[bool, str]:
        try:
            account = self.db.query(Account).filter(Account.id == account_id).first()
            if not account:
                return False, "Account not found"
            
            account.balance = new_balance
            self.db.commit()
            return True, "Balance updated successfully"
        except SQLAlchemyError as e:
            self.db.rollback()
            return False, f"Failed to update balance: {str(e)}"
    
    def update_status(self, account_id: str, new_status: str) -> Tuple[bool, str]:
        valid_statuses = ['active', 'suspended', 'closed']
        if new_status not in valid_statuses:
            return False, f"Invalid status. Must be one of: {', '.join(valid_statuses)}"
        
        try:
            account = self.db.query(Account).filter(Account.id == account_id).first()
            if not account:
                return False, "Account not found"
            
            account.status = new_status
            self.db.commit()
            return True, f"Account status updated to {new_status}"
        except SQLAlchemyError as e:
            self.db.rollback()
            return False, f"Failed to update status: {str(e)}"
    
    def delete(self, account_id: str) -> Tuple[bool, str]:
        try:
            account = self.db.query(Account).filter(Account.id == account_id).first()
            if account:
                self.db.delete(account)
                self.db.commit()
                return True, "Account successfully deleted"
            return False, "Account not found"
        except SQLAlchemyError as e:
            self.db.rollback()
            return False, f"Failed to delete account: {str(e)}"
    
    def update_account(self, account_id: str, updates: Dict[str, Any]) -> Dict[str, str]:
        try:
            account = self.db.query(Account).filter(Account.id == account_id).first()
            if not account:
                raise ValueError("Account not found")
            
            # Update only allowed fields
            allowed_fields = ['account_name', 'account_type', 'currency', 'status']
            for field, value in updates.items():
                if field in allowed_fields and hasattr(account, field):
                    setattr(account, field, value)
            
            # Update timestamp
            account.updated_at = datetime.now()
            
            self.db.commit()
            return {'message': 'Account updated successfully!'}
        except SQLAlchemyError as e:
            self.db.rollback()
            raise ValueError(f"Failed to update account: {str(e)}")