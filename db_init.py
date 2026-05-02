"""
Database Initialization and Seeding Script
Initializes SQLite database and populates with sample data
"""

import sqlite3
import os
import sys
from datetime import datetime, timedelta

# Add parent directory to path to allow imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.models import User, FoodDatabase, NutritionHistory, DailyNutrition, db
from app import create_app

def init_database():
    """Initialize database with schema and sample data"""
    
    app = create_app('development')
    
    with app.app_context():
        # Create all tables
        db.create_all()
        print("✓ Database tables created")
        
        # Check if sample data already exists
        if User.query.filter_by(username='demo_user').first():
            print("✓ Sample data already exists")
            return
        
        # Add sample foods to database
        sample_foods = [
            ('Apple', 52, 0.3, 0.2, 14, '100g', 'Fruits'),
            ('Banana', 89, 1.1, 0.3, 23, '100g', 'Fruits'),
            ('Orange', 47, 0.9, 0.1, 12, '100g', 'Fruits'),
            ('Broccoli', 34, 2.8, 0.4, 7, '100g', 'Vegetables'),
            ('Carrot', 41, 0.9, 0.2, 10, '100g', 'Vegetables'),
            ('Milk', 61, 3.2, 3.3, 4.8, '100ml', 'Dairy'),
            ('Egg', 155, 13, 11, 1.1, '1 egg', 'Protein'),
            ('Chicken', 165, 31, 3.6, 0, '100g', 'Protein'),
            ('Rice', 130, 2.7, 0.3, 28, '100g', 'Grains'),
            ('Bread', 265, 9, 3, 49, '100g', 'Grains'),
            ('Pizza', 285, 12, 10, 36, '100g', 'Fast Food'),
            ('Sandwich', 350, 15, 12, 45, '100g', 'Fast Food'),
            ('Salad', 50, 2, 0.5, 10, '100g', 'Vegetables'),
            ('Pasta', 131, 5, 1.1, 25, '100g', 'Grains'),
            ('Cake', 280, 3, 10, 45, '100g', 'Sweets'),
            ('Cookie', 502, 6, 27, 63, '100g', 'Sweets'),
            ('Donut', 452, 4, 25, 51, '100g', 'Sweets'),
        ]
        
        for food_name, cal, pro, fat, carbs, serving, category in sample_foods:
            food = FoodDatabase(
                food_name=food_name,
                calories=cal,
                protein=pro,
                fat=fat,
                carbohydrates=carbs,
                serving_size=serving,
                category=category
            )
            db.session.add(food)
        
        db.session.commit()
        print(f"✓ Added {len(sample_foods)} sample foods")
        
        # Add demo user
        demo_user = User(
            username='demo_user',
            email='demo@nutrition.local',
            full_name='Demo User',
            age=25,
            gender='Other'
        )
        demo_user.set_password('demo123')
        db.session.add(demo_user)
        db.session.commit()
        print("✓ Created demo user (username: demo_user, password: demo123)")
        
        # Add sample nutrition history for demo user (last 7 days)
        for day_offset in range(7):
            target_date = datetime.utcnow().date() - timedelta(days=day_offset)
            
            # Sample meals for each day
            sample_meals = [
                ('Apple', 1, 52, 0.3, 0.2, 14, 'breakfast'),
                ('Bread', 1, 265, 9, 3, 49, 'breakfast'),
                ('Chicken', 1, 165, 31, 3.6, 0, 'lunch'),
                ('Rice', 1, 130, 2.7, 0.3, 28, 'lunch'),
                ('Salad', 1, 50, 2, 0.5, 10, 'dinner'),
            ]
            
            for food_name, qty, cal, pro, fat, carbs, meal_type in sample_meals:
                entry = NutritionHistory(
                    user_id=demo_user.user_id,
                    date=target_date,
                    food_name=food_name,
                    quantity=qty,
                    calories=cal,
                    protein=pro,
                    fat=fat,
                    carbohydrates=carbs,
                    meal_type=meal_type
                )
                db.session.add(entry)
            
            db.session.commit()
            
            # Create daily summary
            daily_total = sum([cal for _, _, cal, _, _, _, _ in sample_meals])
            daily_protein = sum([pro for _, _, _, pro, _, _, _ in sample_meals])
            daily_fat = sum([fat for _, _, _, _, fat, _, _ in sample_meals])
            daily_carbs = sum([carbs for _, _, _, _, _, carbs, _ in sample_meals])
            
            daily = DailyNutrition(
                user_id=demo_user.user_id,
                date=target_date,
                total_calories=daily_total,
                total_protein=daily_protein,
                total_fat=daily_fat,
                total_carbohydrates=daily_carbs,
                meal_count=len(sample_meals)
            )
            db.session.add(daily)
        
        db.session.commit()
        print("✓ Added sample nutrition history (7 days)")
        
        print("\n" + "="*50)
        print("Database initialization completed!")
        print("="*50)


if __name__ == '__main__':
    init_database()
