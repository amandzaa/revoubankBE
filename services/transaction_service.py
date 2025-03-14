# transaction_service.py
import uuid
from datetime import datetime
from flask import g
from repositories.transaction_repository import TransactionRepository
from utils import helpers
from utils.db import get_db
from utils.validators import validate_required_fields, validate_transaction_type

class TransactionService:
    @staticmethod
    def check_transaction_auth(transaction_id):
        """Check if the current user is authorized to access a transaction."""
        db = get_db()
        cursor = db.cursor()
        cursor.execute("""
            SELECT t.*, a.user_id 
            FROM transactions t
            JOIN accounts a ON t.account_id = a.id
            WHERE t.id = ?
        """, (transaction_id,))
        transaction = cursor.fetchone()
        if not transaction:
            return False, "Transaction not found!", 404
        if transaction['user_id'] != g.current_user['id']:
            return False, "Unauthorized access to transaction!", 403
        return True, dict(transaction), None

    @staticmethod
    def get_all_transactions(account_id=None, start_date=None, end_date=None):
        db = get_db()
        cursor = db.cursor()
        query = "SELECT * FROM transactions WHERE 1=1"
        params = []
        if account_id:
            query += " AND account_id = ?"
            params.append(account_id)
        if start_date:
            query += " AND transaction_date >= ?"
            params.append(start_date)
        if end_date:
            query += " AND transaction_date <= ?"
            params.append(end_date)
        cursor.execute(query, params)
        transactions = cursor.fetchall()
        return [dict(txn) for txn in transactions]

    @staticmethod
    def get_user_transactions(user_id, account_id=None, start_date=None, end_date=None):
        """Get transactions for a specific user with optional filtering."""
        db = get_db()
        cursor = db.cursor()
        query = """
            SELECT t.* FROM transactions t
            JOIN accounts a ON t.account_id = a.id
            WHERE a.user_id = ?
        """
        params = [user_id]
        if account_id:
            query += " AND t.account_id = ?"
            params.append(account_id)
        if start_date:
            query += " AND t.transaction_date >= ?"
            params.append(start_date)
        if end_date:
            query += " AND t.transaction_date <= ?"
            params.append(end_date)
        print(f"lalalaparam{params}, {query}")
        cursor.execute(query, params)
        transactions = cursor.fetchall()
        print(f"transactions{transactions}")
        return [dict(txn) for txn in transactions]

    @staticmethod
    def get_transaction_by_id(transaction_id):
        """Get a specific transaction by ID."""
        authorized, transaction, error_message = TransactionService.check_transaction_auth(transaction_id)
        if not authorized:
            return None, error_message
        transaction_repository = TransactionRepository()
        transaction = transaction_repository.find_by_id(transaction_id)
        
        return transaction, None

    @staticmethod
    def create_transaction(data):
        """Create a new transaction."""
        # Validate required fields
        print(data)
        valid, message = validate_required_fields(data, ['transaction_type', 'amount', 'account_id'])
        if not valid:
            return False, message, 400
        # Validate transaction type
        if not validate_transaction_type(data.get('transaction_type')):
            return False, 'Invalid transaction type! Must be deposit, withdrawal, or transfer', 400
        # Check account authorization
        account_id = data.get('account_id')
        authorized, error_message, status_code = helpers.check_account_owner(account_id)
        print(authorized, error_message, status_code)
        if not authorized:
            return False, error_message, status_code
        # For transfers, check destination account exists
        destination_account_id = data.get('destination_account_id')
        if data.get('transaction_type') == 'transfer' and not destination_account_id:
            return False, 'Destination account ID is required for transfers!', 400
        db = get_db()
        cursor = db.cursor()
        # Check account balance for withdrawals and transfers
        if data.get('transaction_type') in ['withdrawal', 'transfer']:
            cursor.execute("SELECT balance FROM accounts WHERE id = ?", (account_id,))
            account = cursor.fetchone()
            if account['balance'] < float(data.get('amount')):
                return False, 'Insufficient funds!', 400
        # Process transaction based on type
        transaction_id = str(uuid.uuid4())
        try:
            db.execute("BEGIN TRANSACTION")
            # Record the transaction
            cursor.execute(
                """INSERT INTO transactions 
                   (id, account_id, transaction_type, amount, description, transaction_date) 
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (transaction_id, account_id, data.get('transaction_type'), data.get('amount'),
                 data.get('description', ''), datetime.now())
            )
            # Update account balance
            if data.get('transaction_type') == 'deposit':
                cursor.execute(
                    "UPDATE accounts SET balance = balance + ? WHERE id = ?",
                    (float(data.get('amount')), account_id)
                )
            elif data.get('transaction_type') == 'withdrawal':
                cursor.execute(
                    "UPDATE accounts SET balance = balance - ? WHERE id = ?",
                    (float(data.get('amount')), account_id)
                )
            elif data.get('transaction_type') == 'transfer':
                # Deduct from source account
                cursor.execute(
                    "UPDATE accounts SET balance = balance - ? WHERE id = ?",
                    (float(data.get('amount')), account_id)
                )
                # Add to destination account
                cursor.execute(
                    "UPDATE accounts SET balance = balance + ? WHERE id = ?",
                    (float(data.get('amount')), destination_account_id)
                )
                # Record a linked transaction for the destination account
                dest_transaction_id = str(uuid.uuid4())
                cursor.execute(
                    """INSERT INTO transactions 
                       (id, account_id, transaction_type, amount, description, transaction_date, linked_transaction_id) 
                       VALUES (?, ?, ?, ?, ?, ?, ?)""",
                    (dest_transaction_id, destination_account_id, 'deposit', data.get('amount'),
                     f"Transfer from account {account_id}", datetime.now(), transaction_id)
                )
                # Update original transaction with link
                cursor.execute(
                    "UPDATE transactions SET linked_transaction_id = ? WHERE id = ?",
                    (dest_transaction_id, transaction_id)
                )
            db.execute("COMMIT")
            print("successfully committed")
        except Exception as e:
            print("not successfully committed")
            db.execute("ROLLBACK")
            return False, f'Transaction failed: {str(e)}', 500
        return True, {
            'message': 'Transaction completed successfully!',
            'transaction_id': transaction_id
        }, 201
        