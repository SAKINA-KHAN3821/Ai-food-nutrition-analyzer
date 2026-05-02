import sys, os
# Ensure project root is on path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app
from backend.nutrition_tracker import add_food_entry
from backend.auth import register_user
from backend.models import db, NutritionHistory, User

app = create_app('development')
with app.app_context():
    user = User.query.filter_by(username='testuser').first()
    if not user:
        print('Creating testuser')
        success, msg, udata = register_user('testuser','test@example.com','password123','Test User')
        user = User.query.filter_by(username='testuser').first()
    print('Using user_id', user.user_id)
    success,message,entry = add_food_entry(user.user_id,'TestFood',quantity=150,calories=200,protein=10,fat=5,carbs=30,meal_type='lunch',image_path=None,confidence=0.9)
    print('add_food_entry result', success, message, entry)
    latest = NutritionHistory.query.filter_by(user_id=user.user_id).order_by(NutritionHistory.history_id.desc()).first()
    print('Latest entry row', latest.food_name, latest.calories, latest.protein, latest.carbohydrates, latest.quantity)
