"""
User model for the Community Collaboration Platform

This module defines the User class and related functionality for:
1. User authentication
2. Role-based access control
3. User profile management
"""

import os
import hashlib
import uuid
from enum import Enum
from typing import Dict, List, Optional, Any
from datetime import datetime
from flask_login import UserMixin

# Define user roles
class UserRole(Enum):
    ADMIN = "admin"
    SCHOLAR = "scholar"
    REGULATOR = "regulator"
    PRACTITIONER = "practitioner"
    GUEST = "guest"

# Mock database for users (in production, use a real database)
_users_db = {}

class User(UserMixin):
    """User class for authentication and access control"""
    
    def __init__(self, id: str, name: str, email: str, password_hash: str, 
                 role: UserRole, created_at: datetime, profile: Dict[str, Any] = None):
        """
        Initialize a user
        
        Args:
            id: Unique user ID
            name: User's full name
            email: User's email address
            password_hash: Hashed password
            role: User role (admin, scholar, regulator, practitioner, guest)
            created_at: Account creation timestamp
            profile: Additional profile information
        """
        self.id = id
        self.name = name
        self.email = email
        self.password_hash = password_hash
        self.role = role if isinstance(role, UserRole) else UserRole(role)
        self.created_at = created_at
        self.profile = profile or {}
        self.active = True
    
    @staticmethod
    def create(name: str, email: str, password: str, role: str = "practitioner") -> Optional['User']:
        """
        Create a new user
        
        Args:
            name: User's full name
            email: User's email address
            password: Plain text password (will be hashed)
            role: User role
            
        Returns:
            New User instance or None if creation failed
        """
        # Check if email already exists
        if any(u.email == email for u in _users_db.values()):
            return None
        
        # Create user ID
        user_id = str(uuid.uuid4())
        
        # Hash password
        password_hash = User._hash_password(password)
        
        # Create user
        user = User(
            id=user_id,
            name=name,
            email=email,
            password_hash=password_hash,
            role=role,
            created_at=datetime.now()
        )
        
        # Save to mock database
        _users_db[user_id] = user
        
        return user
    
    @staticmethod
    def authenticate(email: str, password: str) -> Optional['User']:
        """
        Authenticate a user
        
        Args:
            email: User's email
            password: Plain text password
            
        Returns:
            User instance if authentication successful, None otherwise
        """
        # Find user by email
        user = next((u for u in _users_db.values() if u.email == email), None)
        
        if not user:
            return None
        
        # Check password
        password_hash = User._hash_password(password)
        if user.password_hash != password_hash:
            return None
        
        return user
    
    @staticmethod
    def get_by_id(user_id: str) -> Optional['User']:
        """Get user by ID"""
        return _users_db.get(user_id)
    
    @staticmethod
    def get_by_email(email: str) -> Optional['User']:
        """Get user by email"""
        return next((u for u in _users_db.values() if u.email == email), None)
    
    @staticmethod
    def get_all() -> List['User']:
        """Get all users"""
        return list(_users_db.values())
    
    def update_profile(self, profile_data: Dict[str, Any]) -> bool:
        """Update user profile"""
        self.profile.update(profile_data)
        return True
    
    def change_password(self, current_password: str, new_password: str) -> bool:
        """Change user password"""
        # Verify current password
        current_hash = User._hash_password(current_password)
        if current_hash != self.password_hash:
            return False
        
        # Update password
        self.password_hash = User._hash_password(new_password)
        return True
    
    def has_permission(self, required_role: UserRole) -> bool:
        """Check if user has the required role or higher"""
        role_hierarchy = {
            UserRole.GUEST: 0,
            UserRole.PRACTITIONER: 1,
            UserRole.REGULATOR: 2,
            UserRole.SCHOLAR: 3,
            UserRole.ADMIN: 4
        }
        
        return role_hierarchy.get(self.role, 0) >= role_hierarchy.get(required_role, 0)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert user to dictionary"""
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "role": self.role.value,
            "created_at": self.created_at.isoformat(),
            "profile": self.profile
        }
    
    @staticmethod
    def _hash_password(password: str) -> str:
        """Hash a password"""
        salt = os.getenv("PASSWORD_SALT", "default_salt")
        return hashlib.sha256(f"{password}{salt}".encode()).hexdigest()

# Create initial admin user
if not _users_db:
    admin = User.create(
        name="Admin User",
        email="admin@example.com",
        password="admin123",  # Change in production!
        role=UserRole.ADMIN.value
    )
    
    # Create a scholar user
    scholar = User.create(
        name="Scholar User",
        email="scholar@example.com",
        password="scholar123",  # Change in production!
        role=UserRole.SCHOLAR.value
    )
    
    # Create a regulator user
    regulator = User.create(
        name="Regulator User",
        email="regulator@example.com",
        password="regulator123",  # Change in production!
        role=UserRole.REGULATOR.value
    )
    
    # Create a practitioner user
    practitioner = User.create(
        name="Practitioner User",
        email="practitioner@example.com",
        password="practitioner123",  # Change in production!
        role=UserRole.PRACTITIONER.value
    )
