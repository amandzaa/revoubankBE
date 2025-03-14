from datetime import datetime
import sqlite3
import uuid
from flask import jsonify
from models.account import Account
from utils.db import get_db

class AccountRepository:
    def find_by_id(self, account_id):
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT * FROM accounts WHERE id = ?", (account_id,))
        return cursor.fetchone()
    
    def find_by_user_id(self, user_id):
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT * FROM accounts WHERE user_id = ?", (user_id,))
        return cursor.fetchall()
    
    def find_all_accounts(self):
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT * FROM accounts")
        return cursor.fetchall()
    
    def find_account_info(self, account_id):
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT * FROM accounts WHERE id = ?", (account_id,))
        account = cursor.fetchone()
        print(f"fetching account from repo: {account}")
        if account:
            return dict(account)  # Convert SQLite Row to dictionary
        return None
    
    def create(self, user_id, account_type, account_name, currency, initial_balance=0, status='active'):
        if initial_balance < 0:
            return False, "Initial balance cannot be negative", None
        account_id = str(uuid.uuid4())
        db = get_db()
        cursor = db.cursor()
        try:
            cursor.execute(
                """INSERT INTO accounts 
                (id, user_id, account_name, account_type, currency, balance, status, created_at, updated_at) 
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (account_id, user_id, account_name,
                account_type, currency,
                initial_balance, status, datetime.now(), datetime.now())
            )
            db.commit()
            return True, "Account created successfully", account_id
        except Exception as e:
            db.rollback()
            return False, f"Failed to create account: {str(e)}", None
    
    def update_balance(self, account_id, new_balance):
        db = get_db()
        cursor = db.cursor()
        try:
            cursor.execute(
                "UPDATE accounts SET balance = ? WHERE id = ?",
                (new_balance, account_id)
            )
            db.commit()
            return True, "Balance updated successfully"
        except Exception as e:
            db.rollback()
            return False, f"Failed to update balance: {str(e)}"
    
    def update_status(self, account_id, new_status):
        valid_statuses = ['active', 'suspended', 'closed']
        if new_status not in valid_statuses:
            return False, f"Invalid status. Must be one of: {', '.join(valid_statuses)}"
        db = get_db()
        cursor = db.cursor()
        try:
            cursor.execute(
                "UPDATE accounts SET status = ? WHERE id = ?",
                (new_status, account_id)
            )
            db.commit()
            return True, f"Account status updated to {new_status}"
        except Exception as e:
            db.rollback()
            return False, f"Failed to update status: {str(e)}"
    
    def delete(self, account_id):
        db = get_db()
        cursor = db.cursor()
        try:
            cursor.execute("DELETE FROM accounts WHERE id = ?", (account_id,))
            db.commit()
            return True, "Account successfully deleted"
        except Exception as e:
            db.rollback()
            return False, f"Failed to delete account: {str(e)}"
        
    def update_account(self, account_id, updates):
        db = get_db()
        cursor = db.cursor()
        # Construct update query
        update_fields = ', '.join([f"{field} = ?" for field in updates.keys()])
        query = f"UPDATE accounts SET {update_fields} WHERE id = ?"
        # Execute update
        cursor.execute(query, list(updates.values()) + [account_id])
        db.commit()
        return jsonify({'message': 'Account updated successfully!'})
    