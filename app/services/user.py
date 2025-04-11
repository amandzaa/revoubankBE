from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from app.utils import helpers
from app.utils.auth import hash_password
from app.repositories.user import UserRepository
from app.utils.validator_schemas import validate_email, validate_password

class UserService:
    def __init__(self, db: Session):
        self.user_repository = UserRepository(db)
    
    def get_all_users(self):
        try:
            users = self.user_repository.find_all()
            return users if users is not None else []
        except SQLAlchemyError:
            return []
    
    def get_info_user(self, user_id: int):
        is_owner, error_response, status_code = helpers.check_user_owner(user_id)
        if not is_owner:
            return False, error_response, status_code
        
        user_info = self.user_repository.find_by_id(user_id)
        if not user_info:
            return False, {'message': 'User not found!'}, 404
        
        return True, {
            'id': user_info.id,
            'username': user_info.username,
            'email': user_info.email,
            # Add other fields as needed
        }, 200
    
    def update_user(self, user_id: int, data: dict):
        print(f"Update request for user {user_id}: {data}")
        
        is_owner, error_response, status_code = helpers.check_user_owner(user_id)
        if not is_owner:
            return False, error_response, status_code
        
        current_user = self.user_repository.find_by_id(user_id)
        if not current_user:
            return False, "User not found", {}
        
        updates = {}
        changes = {}
        allowed_fields = ['username', 'email', 'is_admin', 'phone']
        is_current_user_admin = getattr(current_user, 'is_admin', False)
        print(f"User is admin: {is_current_user_admin}")
        
        # Handle regular fields
        for field in allowed_fields:
            if field in data and data[field] is not None:
                current_value = getattr(current_user, field, None)
                
                # Only update if there's an actual change
                if data[field] != current_value:
                    # Special handling for email
                    if field == 'email':
                        if not validate_email(data['email']):
                            return False, "Invalid email format", {}
                        
                        existing_user = self.user_repository.find_by_email(data['email'])
                        if existing_user and existing_user.id != user_id:
                            return False, "Email already in use", {}
                    
                    # Check admin permissions
                    if field == 'is_admin' and not is_current_user_admin:
                        return False, "Admin access required to update 'is_admin' field", {}
                    
                    updates[field] = data[field]
                    changes[field] = {
                        'from': current_value,
                        'to': data[field]
                    }
        
        # Handle password separately
        if 'password' in data and data['password']:
            valid_password, pwd_message = validate_password(data['password'])
            if not valid_password:
                return False, pwd_message, {}
            
            # IMPORTANT: Use password_hash here, not password
            updates['password_hash'] = hash_password(data['password'])
            changes['password'] = {
                'from': '********',
                'to': '********'
            }
        
        print(f"Final updates to apply: {updates}")
        
        # Return early if nothing to update
        if not updates:
            return True, "No changes to update", {}
        
        try:
            updated_user = self.user_repository.update(user_id, updates)
            if not updated_user:
                return False, "Failed to update user", {}
            
            print(f"User updated successfully: {updated_user.username}")
            return True, "User updated successfully", changes
        except SQLAlchemyError as e:
            print(f"SQL error during update: {e}")
            return False, "An error occurred while updating the user", {}
    
    def delete_user(self, user_id: int):
        is_owner, error_response, status_code = helpers.check_user_owner(user_id)
        if not is_owner:
            return False, error_response, status_code
        
        success = self.user_repository.delete(user_id)
        if not success:
            return False, "Failed to delete user"
        
        return True, "User deleted successfully"