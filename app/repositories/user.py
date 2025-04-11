from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from app.models.user import User

class UserRepository:
    def __init__(self, db: Session = None):
        from app.utils.database_session_manager import get_db_session
        self.db = db if db is not None else get_db_session()

    def find_by_id(self, user_id: int):
        return self.db.query(User).filter(User.id == user_id).first()

    def find_by_username(self, username: str):
        return self.db.query(User).filter(User.username == username).first()

    def find_by_email(self, email: str):
        return self.db.query(User).filter(User.email == email).first()

    def create(self, username: str, email: str, password_hash: str, is_admin: bool = False):
        try:
            new_user = User(
                username=username,
                email=email,
                password=password_hash,
                is_admin=is_admin
            )
            
            self.db.add(new_user)
            self.db.commit()
            self.db.refresh(new_user)
            return new_user
        except SQLAlchemyError as e:
            self.db.rollback()
            raise

    def update(self, user_id: int, updates: dict):
        try:
            print(f"Updating user {user_id} with changes: {updates}")
            
            # Using self.db directly since that's your session object
            user = self.db.query(User).filter(User.id == user_id).first()
            
            if not user:
                print(f"User {user_id} not found")
                return None
                
            print(f"Found user: {user.username}, {user.email}")
            
            # Update fields - include phone in allowed fields
            allowed_fields = ['username', 'email', 'password_hash', 'is_admin', 'phone']
            for field, value in updates.items():
                if field in allowed_fields and hasattr(user, field):
                    print(f"Updating {field} from {getattr(user, field)} to {value}")
                    setattr(user, field, value)
                else:
                    print(f"Field {field} not allowed or doesn't exist on User model")
                    
            self.db.commit()
            print("Changes committed to database")
            self.db.refresh(user)
            print(f"User after update: {user.username}, {user.email}")
            return user
            
        except SQLAlchemyError as e:
            self.db.rollback()
            print(f"SQL error during update: {e}")
            raise

    def delete(self, user_id: int):
        try:
            user = self.db.query(User).filter(User.id == user_id).first()
            if user:
                self.db.delete(user)
                self.db.commit()
                return True
            return False
        except SQLAlchemyError:
            self.db.rollback()
            return False

    def find_all(self):
        return self.db.query(User).all()

    def count(self):
        return self.db.query(User).count()

    def get_admin_users(self):
        return self.db.query(User).filter(User.is_admin == True).all()