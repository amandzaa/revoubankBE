from datetime import datetime
from typing import Optional, Tuple, Dict, Union
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from app.models.user import User 

class AuthRepository:
    def __init__(self, db: Session):
        from app.utils.database_session_manager import get_db_session
        self.db = db if db is not None else get_db_session()

    def find_user_by_email(self, email: str) -> Optional[User]:
        return self.db.query(User).filter(User.email == email).first()

    def create_user(self, user_data: Dict[str, Union[str, None]], hashed_password: str) -> Tuple[bool, Union[str, Exception]]:
        try:
            # Create new user instance
            new_user = User(
                name=user_data.get('name'),
                email=user_data.get('email'),
                password=hashed_password,
                phone=user_data.get('phone', ''),
                is_admin=False
            )
            
            # Add and commit the new user
            self.db.add(new_user)
            self.db.commit()
            
            # Refresh to ensure we have the generated ID
            self.db.refresh(new_user)
            
            return True, new_user.id
        
        except SQLAlchemyError as e:
            # Rollback the session in case of error
            self.db.rollback()
            return False, str(e)

    def user_exists(self, email: str) -> bool:
        user = self.db.query(User).filter(User.email == email).first()
        return user is not None

    def get_user_by_id(self, user_id: str) -> Optional[User]:
        return self.db.query(User).filter(User.id == user_id).first()

    def update_user_password(self, user_id: str, new_hashed_password: str) -> bool:
        try:
            user = self.db.query(User).filter(User.id == user_id).first()
            
            if not user:
                return False
            
            user.password = new_hashed_password
            user.updated_at = datetime.now()
            
            self.db.commit()
            return True
        
        except SQLAlchemyError:
            self.db.rollback()
            return False

    def authenticate_user(self, email: str, hashed_password: str) -> Optional[User]:
        user = self.find_user_by_email(email)
        
        if user and user.password == hashed_password:
            return user
        
        return None