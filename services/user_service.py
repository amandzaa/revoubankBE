from utils import helpers
from utils.auth import hash_password
from repositories.user_repository import UserRepository
from utils.validators import validate_email, validate_password

class UserService:
    def __init__(self):
        self.user_repository = UserRepository()
    
    def get_all_users(self):
        users = self.user_repository.find_all()
        return users if users is not None else []
    
    def get_info_user(self, user_id):
        is_owner, error_response, status_code = helpers.check_user_owner(user_id)
        if not is_owner:
            return False, error_response, status_code
        user_info = self.user_repository.find_by_id(user_id)
        if not user_info:
            return False, {'message': 'User not found!'}, 404
        else:
            user_info = dict(user_info)
        return True, user_info, 200
    
    def update_user(self, user_id, data):
        current_user = self.user_repository.find_by_id(user_id)
        if not current_user:
            return False, "User not found", {}
        updates = {}
        changes = {}
        allowed_fields = ['name', 'email', 'phone','is_admin']
        is_current_user_admin = current_user.get('is_admin', False)
        for field in allowed_fields:
            if field in data and data[field] is not None and data[field] != current_user.get(field, None):
                # Special handling for email
                if field == 'email':
                    if not validate_email(data['email']):
                        return False, "Invalid email format", {}
                    # Check if email is already in use by another user
                    existing_user = self.user_repository.find_by_email(data['email'])
                    if existing_user and existing_user['id'] != user_id:
                        return False, "Email already in use", {}
                if field == 'is_admin' and not is_current_user_admin:
                    return False, "Admin access required to update 'is_admin' field", {}
                updates[field] = data[field]
                changes[field] = {
                    'from': current_user[field],
                    'to': data[field]
                }
        # Handle password separately to hash it
        if 'password' in data and data['password']:
            valid_password, pwd_message = validate_password(data['password'])
            if not valid_password:
                return False, pwd_message, {}
            updates['password'] = hash_password(data['password'])
            changes['password'] = {
                'from': '********',
                'to': '********'
            }
        # If no updates, return early
        if not updates:
            return True, "No changes to update", {}
        success, message, _ = self.user_repository.update(user_id, updates)
        return success, message, changes
    
    def delete_user(self, user_id):
        success = self.user_repository.delete(user_id)
        if not success:
            return False, "Failed to delete user"
        return True, "User deleted successfully"
    
    def register_user(self, data):
        # Validate data
        if not all(field in data for field in ['name', 'email', 'phone', 'password']):
            return False, "Missing required fields: name, email, phone, password"
        # Check if email is already taken
        existing_user = self.user_repository.find_by_email(data['email'])
        if existing_user:
            return False, "Email address is already taken"
        # Hash password
        data['password'] = hash_password(data['password'])
        # Insert user into the database
        success = self.user_repository.create(
        email=data['email'],
        name=data['name'],
        phone=data['phone'],
        password=data['password']
        )
        if not success:
            return False, "Failed to register user"
        return True, "User registered successfully"
    