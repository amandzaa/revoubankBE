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
                password_hash=password_hash,
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
            user = self.db.query(User).filter(User.id == user_id).first()
            
            if not user:
                return None

            # Update only allowed fields
            allowed_fields = ['username', 'email', 'password_hash', 'is_admin']
            for field, value in updates.items():
                if field in allowed_fields and hasattr(user, field):
                    setattr(user, field, value)
            
            self.db.commit()
            self.db.refresh(user)
            return user
        
        except SQLAlchemyError as e:
            self.db.rollback()
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