from backend.models import db, NutritionHistory, DailyNutrition, FoodDatabase
from datetime import datetime, date
from sqlalchemy import func

def add_food_entry(user_id, food_name, quantity=1.0, calories=0, protein=0, fat=0, 
                   carbs=0, meal_type='other', image_path=None, confidence=0):
    """
    Add a food entry to user's nutrition history
    
    Args:
        user_id: User ID
        food_name: Name of food
        quantity: Quantity consumed (for record/display)
        calories: Total calories for this entry
        protein: Total protein in grams for this entry
        fat: Total fat in grams for this entry
        carbs: Total carbohydrates in grams for this entry
        meal_type: Type of meal (breakfast, lunch, dinner, snack)
        image_path: Path to food image
        confidence: AI detection confidence
    
    Returns:
        tuple: (success, message, entry_data)
    """
    try:
        quantity = float(quantity) if quantity is not None else 1.0
        if quantity <= 0:
            return False, "Quantity must be greater than zero", None

        entry = NutritionHistory(
            user_id=user_id,
            date=datetime.utcnow().date(),
            food_name=food_name,
            quantity=quantity,
            calories=calories,
            protein=protein,
            fat=fat,
            carbohydrates=carbs,
            meal_type=meal_type,
            image_path=image_path,
            detected_confidence=confidence
        )
        
        db.session.add(entry)
        db.session.commit()
        
        # Update daily nutrition
        _update_daily_nutrition(user_id, datetime.utcnow().date())
        
        return True, "Food entry added successfully", entry.to_dict()
    
    except Exception as e:
        db.session.rollback()
        return False, f"Error adding entry: {str(e)}", None


def _update_daily_nutrition(user_id, target_date):
    """Update daily nutrition totals"""
    try:
        # Get all entries for the day
        daily_entries = NutritionHistory.query.filter_by(
            user_id=user_id, 
            date=target_date
        ).all()
        
        totals = {
            'calories': sum(e.calories for e in daily_entries),
            'protein': sum(e.protein for e in daily_entries),
            'fat': sum(e.fat for e in daily_entries),
            'carbs': sum(e.carbohydrates for e in daily_entries),
            'count': len(daily_entries)
        }
        
        # Get or create daily nutrition record
        daily = DailyNutrition.query.filter_by(
            user_id=user_id,
            date=target_date
        ).first()
        
        if daily:
            daily.total_calories = totals['calories']
            daily.total_protein = totals['protein']
            daily.total_fat = totals['fat']
            daily.total_carbohydrates = totals['carbs']
            daily.meal_count = totals['count']
        else:
            daily = DailyNutrition(
                user_id=user_id,
                date=target_date,
                total_calories=totals['calories'],
                total_protein=totals['protein'],
                total_fat=totals['fat'],
                total_carbohydrates=totals['carbs'],
                meal_count=totals['count']
            )
            db.session.add(daily)
        
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(f"Error updating daily nutrition: {str(e)}")


def get_daily_summary(user_id, target_date=None):
    """
    Get daily nutrition summary for user
    
    Args:
        user_id: User ID
        target_date: Date to retrieve (default: today)
    
    Returns:
        dict: Daily nutrition summary with breakdown by meal type
    """
    if target_date is None:
        target_date = datetime.utcnow().date()
    
    daily = DailyNutrition.query.filter_by(
        user_id=user_id,
        date=target_date
    ).first()
    
    if not daily:
        return {
            'date': target_date.isoformat(),
            'total_calories': 0,
            'total_protein': 0,
            'total_fat': 0,
            'total_carbohydrates': 0,
            'meal_count': 0,
            'meals': {}
        }
    
    # Get breakdown by meal type
    entries = NutritionHistory.query.filter_by(
        user_id=user_id,
        date=target_date
    ).all()
    
    meals = {}
    for meal_type in ['breakfast', 'lunch', 'dinner', 'snack', 'other']:
        meal_entries = [e for e in entries if e.meal_type == meal_type]
        if meal_entries:
            meals[meal_type] = {
                'count': len(meal_entries),
                'calories': sum(e.calories for e in meal_entries),
                'protein': sum(e.protein for e in meal_entries),
                'fat': sum(e.fat for e in meal_entries),
                'carbs': sum(e.carbohydrates for e in meal_entries),
                'foods': [e.food_name for e in meal_entries]
            }
    
    return {
        'date': target_date.isoformat(),
        'total_calories': daily.total_calories,
        'total_protein': daily.total_protein,
        'total_fat': daily.total_fat,
        'total_carbohydrates': daily.total_carbohydrates,
        'meal_count': daily.meal_count,
        'meals': meals
    }


def get_nutrition_history(user_id, days=7):
    """
    Get nutrition history for past N days
    
    Args:
        user_id: User ID
        days: Number of past days
    
    Returns:
        list: Daily nutrition summaries
    """
    from datetime import timedelta
    
    end_date = datetime.utcnow().date()
    start_date = end_date - timedelta(days=days-1)
    
    daily_records = DailyNutrition.query.filter(
        DailyNutrition.user_id == user_id,
        DailyNutrition.date >= start_date,
        DailyNutrition.date <= end_date
    ).order_by(DailyNutrition.date.desc()).all()
    
    return [record.to_dict() for record in daily_records]


def delete_food_entry(entry_id, user_id):
    """
    Delete a food entry
    
    Args:
        entry_id: History entry ID
        user_id: User ID (for verification)
    
    Returns:
        tuple: (success, message)
    """
    try:
        entry = db.session.get(NutritionHistory, entry_id)
        
        if not entry or entry.user_id != user_id:
            return False, "Entry not found"
        
        target_date = entry.date
        db.session.delete(entry)
        db.session.commit()
        
        # Update daily nutrition
        _update_daily_nutrition(user_id, target_date)
        
        return True, "Entry deleted successfully"
    
    except Exception as e:
        db.session.rollback()
        return False, f"Error deleting entry: {str(e)}"


def search_foods(query, limit=10):
    """
    Search food database
    
    Args:
        query: Search query
        limit: Maximum results
    
    Returns:
        list: Matching foods
    """
    foods = FoodDatabase.query.filter(
        FoodDatabase.food_name.ilike(f'%{query}%')
    ).limit(limit).all()
    
    return [food.to_dict() for food in foods]


def get_food_by_id(food_id):
    """Get food details by ID"""
    food = db.session.get(FoodDatabase, food_id)
    return food.to_dict() if food else None


def get_weekly_stats(user_id):
    """Get weekly nutrition statistics"""
    from datetime import timedelta
    
    end_date = datetime.utcnow().date()
    start_date = end_date - timedelta(days=6)
    
    daily_records = DailyNutrition.query.filter(
        DailyNutrition.user_id == user_id,
        DailyNutrition.date >= start_date,
        DailyNutrition.date <= end_date
    ).all()
    
    if not daily_records:
        return {
            'week_start': start_date.isoformat(),
            'week_end': end_date.isoformat(),
            'avg_calories': 0,
            'avg_protein': 0,
            'avg_fat': 0,
            'avg_carbs': 0,
            'total_days_logged': 0
        }
    
    return {
        'week_start': start_date.isoformat(),
        'week_end': end_date.isoformat(),
        'avg_calories': sum(r.total_calories for r in daily_records) / len(daily_records),
        'avg_protein': sum(r.total_protein for r in daily_records) / len(daily_records),
        'avg_fat': sum(r.total_fat for r in daily_records) / len(daily_records),
        'avg_carbs': sum(r.total_carbohydrates for r in daily_records) / len(daily_records),
        'total_days_logged': len(daily_records)
    }
