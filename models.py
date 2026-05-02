from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(db.Model):
    """User model for authentication"""
    __tablename__ = 'users'
    
    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    full_name = db.Column(db.String(120))
    age = db.Column(db.Integer)
    gender = db.Column(db.String(10))  # Male, Female, Other
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    nutrition_history = db.relationship('NutritionHistory', backref='user', lazy=True, cascade='all, delete-orphan')
    daily_nutrition = db.relationship('DailyNutrition', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def set_password(self, password):
        """Hash and set password"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Verify password"""
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'user_id': self.user_id,
            'username': self.username,
            'email': self.email,
            'full_name': self.full_name,
            'age': self.age,
            'gender': self.gender,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class FoodDatabase(db.Model):
    """Food nutrition reference database"""
    __tablename__ = 'food_database'
    
    food_id = db.Column(db.Integer, primary_key=True)
    food_name = db.Column(db.String(120), nullable=False, index=True)
    calories = db.Column(db.Float, default=0)
    protein = db.Column(db.Float, default=0)  # grams
    fat = db.Column(db.Float, default=0)      # grams
    carbohydrates = db.Column(db.Float, default=0)  # grams
    serving_size = db.Column(db.String(50), default='100g')
    category = db.Column(db.String(50))  # e.g., Fruits, Vegetables, Protein, Grains
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'food_id': self.food_id,
            'food_name': self.food_name,
            'calories': self.calories,
            'protein': self.protein,
            'fat': self.fat,
            'carbohydrates': self.carbohydrates,
            'serving_size': self.serving_size,
            'category': self.category
        }


class NutritionHistory(db.Model):
    """User's food consumption history"""
    __tablename__ = 'nutrition_history'
    
    history_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False, index=True)
    date = db.Column(db.Date, default=datetime.utcnow, index=True)
    food_name = db.Column(db.String(120), nullable=False)
    quantity = db.Column(db.Float, default=1.0)
    calories = db.Column(db.Float, default=0)
    protein = db.Column(db.Float, default=0)
    fat = db.Column(db.Float, default=0)
    carbohydrates = db.Column(db.Float, default=0)
    meal_type = db.Column(db.String(20), default='other')  # breakfast, lunch, dinner, snack
    image_path = db.Column(db.String(255))
    detected_confidence = db.Column(db.Float, default=0)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'history_id': self.history_id,
            'user_id': self.user_id,
            'date': self.date.isoformat() if self.date else None,
            'food_name': self.food_name,
            'quantity': self.quantity,
            'calories': self.calories,
            'protein': self.protein,
            'fat': self.fat,
            'carbohydrates': self.carbohydrates,
            'meal_type': self.meal_type,
            'detected_confidence': self.detected_confidence,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None
        }


class DailyNutrition(db.Model):
    """Daily aggregated nutrition data"""
    __tablename__ = 'daily_nutrition'
    
    stats_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False, index=True)
    date = db.Column(db.Date, default=datetime.utcnow, index=True)
    total_calories = db.Column(db.Float, default=0)
    total_protein = db.Column(db.Float, default=0)
    total_fat = db.Column(db.Float, default=0)
    total_carbohydrates = db.Column(db.Float, default=0)
    meal_count = db.Column(db.Integer, default=0)
    
    __table_args__ = (
        db.UniqueConstraint('user_id', 'date', name='unique_user_date'),
    )
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'stats_id': self.stats_id,
            'user_id': self.user_id,
            'date': self.date.isoformat() if self.date else None,
            'total_calories': self.total_calories,
            'total_protein': self.total_protein,
            'total_fat': self.total_fat,
            'total_carbohydrates': self.total_carbohydrates,
            'meal_count': self.meal_count
        }
