from datetime import datetime
import uuid
from utils.db import get_db
from models.user import User

class UserRepository:
    def find_by_id(self, user_id):
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT id, name, email, phone FROM users WHERE id = ?", (user_id,))
        user = cursor.fetchone()
        if user:
            return dict(user)  # Convert SQLite Row to dictionary
        return None
    
    def find_by_email(self, email):
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
        row = cursor.fetchone()
        return User.from_row(row)
    
    def create(self, name, email, password, phone=None):
        db = get_db()
        cursor = db.cursor()
        user_id = str(uuid.uuid4())
        now = datetime.now()
        cursor.execute(
            """
            INSERT INTO users (id, name, email, password, phone, is_admin, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (user_id, name, email, password, phone, False, now, now)
        )
        db.commit()
        return self.find_by_id(user_id)
    
    def update(self, user_id, updates):
        if not updates:
            return False, "No updates provided", {}
        db = get_db()
        cursor = db.cursor()
        # First, get current user data for comparison
        cursor.execute("SELECT name, email, phone FROM users WHERE id = ?", (user_id,))
        current_user = cursor.fetchone()
        if not current_user:
            return False, "User not found", {}
        # Track what changed
        changes = {}
        for field in updates:
            if field in current_user.keys():
                current_value = current_user[field]
                new_value = updates[field]
                print(f"Comparing {field}: current='{current_value}' (type: {type(current_value)}) vs new='{new_value}' (type: {type(new_value)})")
                print(f"Are they equal? {current_value == new_value}")
                if new_value != current_value:
                    changes[field] = {
                        'from': current_value,
                        'to': new_value
                    }
        # Prepare update parameters
        set_clause = ", ".join([f"{field} = ?" for field in updates.keys()])
        set_clause += ", updated_at = ?"
        # Add current timestamp to update values
        update_values = list(updates.values())
        update_values.append(datetime.now())
        update_values.append(user_id)
        try:
            query = f"UPDATE users SET {set_clause} WHERE id = ?"
            cursor.execute(query, tuple(update_values))
            rows_affected = cursor.rowcount
            db.commit()
            if rows_affected == 0:
                return False, "No rows were updated", {}
            return True, "Profile updated successfully", changes
        except Exception as e:
            db.rollback()
            return False, f"Update failed: {str(e)}", {}
    
    def delete(self, user_id):
        db = get_db()
        cursor = db.cursor()
        cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
        db.commit()
        return cursor.rowcount > 0
    
    def find_all(self):
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT id, name, email, phone, is_admin FROM users")
        users = cursor.fetchall()
        if users:
            return [{
                'id': user['id'],
                'name': user['name'],
                'email': user['email'],
                'phone': user['phone'],
                'is_admin': user['is_admin']
            } for user in users]
        return None
    