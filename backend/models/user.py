from datetime import datetime
from bson import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash

class User:
    """
    User class for managing user data such as authentication, preferences, and activity.
    """
    def __init__(self, email, password=None, name=None, user_id=None, created_at=None, 
                 last_login=None, is_admin=False, preferences=None, password_hash=None):
        self.user_id = user_id if user_id else ObjectId()
        self.email = email
        self.password_hash = password_hash if password_hash else (generate_password_hash(password) if password else None)
        self.name = name
        self.created_at = created_at if created_at else datetime.now()
        self.last_login = last_login
        self.is_admin = is_admin
        self.preferences = preferences if preferences else {}
    
    def check_password(self, password):
        """Verify the password against the stored hash"""
        if not self.password_hash:
            return False
        return check_password_hash(self.password_hash, password)
    
    def update_last_login(self):
        """Update the last login timestamp"""
        self.last_login = datetime.now()
    
    def to_dict(self):
        """Convert user object to dictionary for database storage"""
        return {
            "_id": self.user_id,
            "email": self.email,
            "password_hash": self.password_hash,
            "name": self.name,
            "created_at": self.created_at,
            "last_login": self.last_login,
            "is_admin": self.is_admin,
            "preferences": self.preferences
        }
    
    @classmethod
    def from_dict(cls, user_dict):
        """Create a User object from a dictionary"""
        if not user_dict:
            return None
        
        return cls(
            email=user_dict.get("email"),
            user_id=user_dict.get("_id"),
            name=user_dict.get("name"),
            created_at=user_dict.get("created_at"),
            last_login=user_dict.get("last_login"),
            is_admin=user_dict.get("is_admin", False),
            preferences=user_dict.get("preferences", {}),
            password_hash=user_dict.get("password_hash")
        )
