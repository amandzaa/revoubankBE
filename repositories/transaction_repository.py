import sqlite3
import uuid
from datetime import datetime
from utils.db import get_db
from models.transaction import Transaction

class TransactionRepository:
    def find_by_id(self, transaction_id):
        db = get_db()
        db.row_factory = sqlite3.Row  # Assuming sqlite3 is imported
        cursor = db.cursor()
        cursor.execute("SELECT * FROM transactions WHERE id = ?", (transaction_id,))
        row = cursor.fetchone()
        if row is None:
            return None
        return dict(row)
    
    def find_by_account_id(self, account_id, start_date=None, end_date=None):
        db = get_db()
        cursor = db.cursor()
        query = "SELECT * FROM transactions WHERE account_id = ?"
        params = [account_id]
        if start_date:
            query += " AND transaction_date >= ?"
            params.append(start_date)
        if end_date:
            query += " AND transaction_date <= ?"
            params.append(end_date)
        query += " ORDER BY transaction_date DESC"
        cursor.execute(query, params)
        rows = cursor.fetchall()
        return [Transaction.from_row(row) for row in rows]
    
    def find_by_user_id(self, user_id, account_id=None, start_date=None, end_date=None):
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
        query += " ORDER BY t.transaction_date DESC"
        cursor.execute(query, params)
        rows = cursor.fetchall()
        return [Transaction.from_row(row) for row in rows]
    
    def create(self, account_id, transaction_type, amount, description=None, linked_transaction_id=None):
        db = get_db()
        cursor = db.cursor()
        transaction_id = str(uuid.uuid4())
        now = datetime.now()
        cursor.execute(
            """
            INSERT INTO transactions (id, account_id, transaction_type, amount, 
                                     description, transaction_date, linked_transaction_id)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (transaction_id, account_id, transaction_type, amount, 
             description, now, linked_transaction_id)
        )
        db.commit()
        return self.find_by_id(transaction_id)
    
    def update_linked_transaction(self, transaction_id, linked_transaction_id):
        """Update the linked transaction ID for a transaction."""
        db = get_db()
        cursor = db.cursor()
        cursor.execute(
            """
            UPDATE transactions 
            SET linked_transaction_id = ?
            WHERE id = ?
            """,
            (linked_transaction_id, transaction_id)
        )
        db.commit()
        return cursor.rowcount > 0
    