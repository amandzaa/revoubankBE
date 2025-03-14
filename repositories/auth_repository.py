from datetime import datetime
import uuid
from utils.db import get_db

class AuthRepository:
    @staticmethod
    def find_user_by_email(email):
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT id, email, password FROM users WHERE email = ?", (email,))
        return cursor.fetchone()
    
    @staticmethod
    def create_user(user_data, hashed_password):
        db = get_db()
        cursor = db.cursor()
        user_id = str(uuid.uuid4())
        current_time = datetime.now()
        try:
            cursor.execute(
                "INSERT INTO users (id, name, email, password, phone, is_admin, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (user_id, user_data.get('name'), user_data.get('email'), hashed_password,
                 user_data.get('phone', ''), False,  current_time, current_time)
            )
            db.commit()
            return True, user_id
        except Exception as e:
            db.rollback()
            return False, str(e)
    
    @staticmethod
    def user_exists(email):
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
        return cursor.fetchone() is not None
    