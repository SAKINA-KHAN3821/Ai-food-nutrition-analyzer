from flask import request, jsonify, session
from functools import wraps
from backend.models import db, User
from datetime import datetime

def register_user(username, email, password, full_name=None, age=None, gender=None):
    """
    Register a new user
    
    Args:
        username: Unique username
        email: Unique email address
        password: Password (will be hashed)
        full_name: User's full name
        age: User's age
        gender: User's gender
    
    Returns:
        tuple: (success, message, user_data)
    """
    try:
        # Validate inputs
        if not username or len(username) < 3:
            return False, "Username must be at least 3 characters", None
        
        if not email or '@' not in email:
            return False, "Invalid email format", None
        
        if not password or len(password) < 6:
            return False, "Password must be at least 6 characters", None
        
        # Check if user already exists
        if User.query.filter_by(username=username).first():
            return False, "Username already exists", None
        
        if User.query.filter_by(email=email).first():
            return False, "Email already registered", None
        
        # Create new user
        user = User(
            username=username,
            email=email,
            full_name=full_name,
            age=age,
            gender=gender
        )
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        return True, "Registration successful", user.to_dict()
    
    except Exception as e:
        db.session.rollback()
        return False, f"Registration error: {str(e)}", None


def login_user(username, password):
    """
    Authenticate user login
    
    Args:
        username: Username
        password: Password
    
    Returns:
        tuple: (success, message, user_data)
    """
    try:
        user = User.query.filter_by(username=username).first()
        
        if not user:
            return False, "Invalid username or password", None
        
        if not user.check_password(password):
            return False, "Invalid username or password", None
        
        # Set session
        session['user_id'] = user.user_id
        session['username'] = user.username
        session.permanent = True
        
        return True, "Login successful", user.to_dict()
    
    except Exception as e:
        return False, f"Login error: {str(e)}", None


def logout_user():
    """Logout current user"""
    session.clear()
    return True, "Logout successful"


def get_current_user():
    """Get currently logged-in user"""
    if 'user_id' not in session:
        return None
    
    return db.session.get(User, session['user_id'])


def login_required(f):
    """Decorator to require login for route"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'success': False, 'message': 'Login required'}), 401
        return f(*args, **kwargs)
    return decorated_function


def update_user_profile(user_id, **kwargs):
    """
    Update user profile information
    
    Args:
        user_id: User ID
        **kwargs: Fields to update (full_name, age, gender)
    
    Returns:
        tuple: (success, message, user_data)
    """
    try:
        user = db.session.get(User, user_id)
        if not user:
            return False, "User not found", None
        
        allowed_fields = ['full_name', 'age', 'gender']
        for field, value in kwargs.items():
            if field in allowed_fields and value is not None:
                setattr(user, field, value)
        
        db.session.commit()
        return True, "Profile updated successfully", user.to_dict()
    
    except Exception as e:
        db.session.rollback()
        return False, f"Update error: {str(e)}", None
