from datetime import datetime
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from app.models.transaction import Transaction
from app.models.account import Account

class TransactionRepository:
    def __init__(self, db: Session = None):
        from app.utils.database_session_manager import get_db_session
        self.db = db if db is not None else get_db_session()

    def find_by_id(self, transaction_id: str) -> Optional[dict]:
        transaction = self.db.query(Transaction).filter(Transaction.id == transaction_id).first()
        return transaction.to_dict() if transaction else None

    def find_by_account_id(
        self, 
        account_id: str, 
        start_date: Optional[datetime] = None, 
        end_date: Optional[datetime] = None
    ) -> List[Transaction]:
        query = self.db.query(Transaction).filter(Transaction.account_id == account_id)
        
        if start_date:
            query = query.filter(Transaction.transaction_date >= start_date)
        
        if end_date:
            query = query.filter(Transaction.transaction_date <= end_date)
        
        return query.order_by(Transaction.transaction_date.desc()).all()

    def find_by_user_id(
        self, 
        user_id: str, 
        account_id: Optional[str] = None, 
        start_date: Optional[datetime] = None, 
        end_date: Optional[datetime] = None
    ) -> List[Transaction]:
        query = (
            self.db.query(Transaction)
            .join(Transaction.account)
            .filter(Account.user_id == user_id)
        )
        
        if account_id:
            query = query.filter(Transaction.account_id == account_id)
        
        if start_date:
            query = query.filter(Transaction.transaction_date >= start_date)
        
        if end_date:
            query = query.filter(Transaction.transaction_date <= end_date)
        
        return query.order_by(Transaction.transaction_date.desc()).all()

    def create(
        self, 
        account_id: str, 
        transaction_type: str, 
        amount: float, 
        description: Optional[str] = None, 
        linked_transaction_id: Optional[str] = None
    ) -> Optional[dict]:
        try:
            new_transaction = Transaction(
                account_id=account_id,
                transaction_type=transaction_type,
                amount=amount,
                description=description,
                linked_transaction_id=linked_transaction_id
            )
            
            self.db.add(new_transaction)
            self.db.commit()
            self.db.refresh(new_transaction)
            
            return new_transaction.to_dict()
        except SQLAlchemyError as e:
            self.db.rollback()
            print(f"Transaction creation failed: {str(e)}")
            return None

    def update_linked_transaction(
        self, 
        transaction_id: str, 
        linked_transaction_id: str
    ) -> bool:
        try:
            transaction = self.db.query(Transaction).filter(
                Transaction.id == transaction_id
            ).first()
            
            if not transaction:
                return False
            
            transaction.linked_transaction_id = linked_transaction_id
            self.db.commit()
            return True
        except SQLAlchemyError as e:
            self.db.rollback()
            print(f"Linked transaction update failed: {str(e)}")
            return False

    def get_transaction_summary(
        self, 
        user_id: str, 
        start_date: Optional[datetime] = None, 
        end_date: Optional[datetime] = None
    ) -> dict:
        query = (
            self.db.query(Transaction)
            .join(Transaction.account)
            .filter(Account.user_id == user_id)
        )
        
        if start_date:
            query = query.filter(Transaction.transaction_date >= start_date)
        
        if end_date:
            query = query.filter(Transaction.transaction_date <= end_date)
        
        # Calculate summary
        transactions = query.all()
        
        return {
            'total_transactions': len(transactions),
            'total_amount': sum(t.amount for t in transactions),
            'transactions_by_type': self._summarize_by_type(transactions)
        }

    def _summarize_by_type(self, transactions: List[Transaction]) -> dict:
        summary = {}
        for transaction in transactions:
            if transaction.transaction_type not in summary:
                summary[transaction.transaction_type] = {
                    'count': 0,
                    'total_amount': 0
                }
            
            summary[transaction.transaction_type]['count'] += 1
            summary[transaction.transaction_type]['total_amount'] += transaction.amount
        
        return summary