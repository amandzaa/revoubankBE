from datetime import datetime
from decimal import Decimal
from typing import Dict, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import or_
from app.models.transaction import Transaction
from app.models.account import Account

class TransactionRepository:
    def __init__(self, db: Session = None):
        from app.utils.database_session_manager import get_db_session
        self.db = db if db is not None else get_db_session()

    def find_by_id(self, transaction_id: str) -> Optional[Transaction]:
        return self.db.query(Transaction).filter(Transaction.id == transaction_id).first()
   
    def find_transaction_info(self, transaction_id: str) -> Optional[Dict]:
        transaction = self.db.query(Transaction).filter(Transaction.id == transaction_id).first()
        return transaction.to_dict() if transaction else None
    
    def find_by_transaction_number(self, transaction_number: str) -> Optional[Transaction]:
        return self.db.query(Transaction).filter(Transaction.transaction_number == transaction_number).first()
    
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
        # Start with base query
        query = self.db.query(Transaction)
        
        # Find all accounts belonging to the user
        user_accounts = self.db.query(Account.id).filter(Account.user_id == user_id).all()
        account_ids = [acc.id for acc in user_accounts]
        
        if not account_ids:
            return []  # No accounts found for user
        
        # Filter transactions where user is sender or receiver
        query = query.filter(
            or_(
                Transaction.from_account_id.in_(account_ids),
                Transaction.to_account_id.in_(account_ids)
            )
        )
        
        # Filter by specific account if provided
        if account_id:
            query = query.filter(
                or_(
                    Transaction.from_account_id == account_id,
                    Transaction.to_account_id == account_id
                )
            )
        
        # Add date filters
        if start_date:
            query = query.filter(Transaction.created_at >= start_date)
        
        if end_date:
            query = query.filter(Transaction.created_at <= end_date)
        
        # Order by most recent first
        return query.order_by(Transaction.created_at.desc()).all()

    def create(
        self, 
        from_account_id: Optional[int] = None, 
        to_account_id: Optional[int] = None, 
        amount: float = 0.0, 
        transaction_type: str = "", 
        description: Optional[str] = None
    ) -> Optional[dict]:
        try:
            # Generate transaction number
            transaction_number = self._generate_transaction_number(transaction_type)
            decimal_amount = Decimal(str(amount))
            
            # Start a transaction
            new_transaction = Transaction(
                transaction_number=transaction_number,
                from_account_id=from_account_id,
                to_account_id=to_account_id,
                amount=decimal_amount,
                transaction_type=transaction_type,
                description=description
            )
            
            self.db.add(new_transaction)
            self.db.flush()  # This assigns an ID without committing
            
            # Update account balances based on transaction type
            if transaction_type == "deposit":
                if to_account_id:
                    to_account = self.db.query(Account).filter(Account.id == to_account_id).first()
                    if to_account:
                        to_account.balance += decimal_amount
            
            elif transaction_type == "withdrawal":
                if from_account_id:
                    from_account = self.db.query(Account).filter(Account.id == from_account_id).first()
                    if from_account:
                        # Check if there's enough balance
                        if from_account.balance >= decimal_amount:
                            from_account.balance -= decimal_amount
                        else:
                            self.db.rollback()
                            raise ValueError("Insufficient funds for withdrawal")
            
            elif transaction_type == "transfer":
                if from_account_id and to_account_id:
                    from_account = self.db.query(Account).filter(Account.id == from_account_id).first()
                    to_account = self.db.query(Account).filter(Account.id == to_account_id).first()
                    
                    if from_account and to_account:
                        # Check if there's enough balance
                        if from_account.balance >= decimal_amount:
                            from_account.balance -= decimal_amount
                            to_account.balance += decimal_amount
                        else:
                            self.db.rollback()
                            raise ValueError("Insufficient funds for transfer")
            
            elif transaction_type == "payment":
                if from_account_id:
                    from_account = self.db.query(Account).filter(Account.id == from_account_id).first()
                    if from_account and from_account.balance >= decimal_amount:
                        from_account.balance -= decimal_amount
                    else:
                        self.db.rollback()
                        raise ValueError("Insufficient funds for payment")
            
            elif transaction_type == "refund":
                if to_account_id:
                    to_account = self.db.query(Account).filter(Account.id == to_account_id).first()
                    if to_account:
                        to_account.balance += decimal_amount
            
            elif transaction_type == "fee":
                if from_account_id:
                    from_account = self.db.query(Account).filter(Account.id == from_account_id).first()
                    if from_account and from_account.balance >= decimal_amount:
                        from_account.balance -= decimal_amount
                    else:
                        self.db.rollback()
                        raise ValueError("Insufficient funds for fee")
            
            elif transaction_type == "interest":
                if to_account_id:
                    to_account = self.db.query(Account).filter(Account.id == to_account_id).first()
                    if to_account:
                        to_account.balance += decimal_amount
            
            elif transaction_type == "reversal":
                # For reversals, you need to handle according to your business logic
                # This is a simplified example - you'd want to reference the original transaction
                if from_account_id:
                    from_account = self.db.query(Account).filter(Account.id == from_account_id).first()
                    if from_account:
                        from_account.balance -= decimal_amount
                
                if to_account_id:
                    to_account = self.db.query(Account).filter(Account.id == to_account_id).first()
                    if to_account:
                        to_account.balance += decimal_amount
            
            # Commit the transaction and balance updates together
            self.db.commit()
            return new_transaction.to_dict()
        
        except Exception as e:
            self.db.rollback()
            print(f"Transaction creation failed: {str(e)}")
            raise e  # Re-raise to handle in the service layer

    def _generate_transaction_number(self, transaction_type: str) -> str:
        """Generate a unique transaction number based on transaction type."""
        # Create prefix based on transaction type
        type_prefixes = {
            "deposit": "DEP",
            "withdrawal": "WDR",
            "transfer": "TRF",
            "payment": "PMT",
            "refund": "REF",
            "fee": "FEE",
            "interest": "INT",
            "reversal": "REV"
        }
        
        # Get the prefix or use "TRX" as default if type not found
        prefix = type_prefixes.get(transaction_type, "TRX")
        
        # Format: PREFIX-YYYYMMDD-XXXXXX
        date_part = datetime.now().strftime("%Y%m%d")
        
        # Get the last transaction number for this type today
        last_transaction = self.db.query(Transaction)\
            .filter(Transaction.transaction_number.like(f"{prefix}-{date_part}-%"))\
            .order_by(Transaction.id.desc())\
            .first()
        
        if last_transaction:
            # Extract sequence number and increment
            last_seq = int(last_transaction.transaction_number.split('-')[-1])
            new_seq = last_seq + 1
        else:
            # First transaction of this type today
            new_seq = 1
        
        # Format with 6-digit sequence number
        return f"{prefix}-{date_part}-{new_seq:06d}"

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
    
    def get_all_transactions(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[Transaction]:
        query = self.db.query(Transaction)
        
        if start_date:
            query = query.filter(Transaction.created_at >= start_date)
        
        if end_date:
            query = query.filter(Transaction.created_at <= end_date)
        
        return query.order_by(Transaction.created_at.desc()).all()