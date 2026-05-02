from flask import Blueprint, request, jsonify, render_template, session, redirect, url_for, send_from_directory, abort, current_app
from backend.models import db

from backend.auth import register_user, login_user, logout_user, get_current_user, login_required, update_user_profile
from backend.models import FoodDatabase, NutritionHistory, DailyNutrition, db

from backend.nutrition_tracker import (
    add_food_entry, get_daily_summary, get_nutrition_history,
    delete_food_entry, search_foods, get_food_by_id, get_weekly_stats
)
from backend.utils import (
    allowed_file, save_upload_file, delete_file, 
    NutritionCalculator, get_meal_type_from_time
)
from config import Config
import os
from datetime import datetime, timedelta

# Create blueprint
api = Blueprint('api', __name__, url_prefix='/api')
pages = Blueprint('pages', __name__)

# Initialize food recognizer
food_recognizer = None

def init_food_recognizer():
    """Initialize the food recognizer model"""
    global food_recognizer
    if food_recognizer is None:
        # Import here to avoid heavy model imports (and network checks) at module import time
        from ai_model.food_recognizer import FoodRecognizer
        food_recognizer = FoodRecognizer(
            model_path=Config.MODEL_PATH,
            confidence_threshold=Config.CONFIDENCE_THRESHOLD
        )

# ==================== PAGE ROUTES ====================

@pages.route('/')
def index():
    """Home page - Modern landing page"""
    # Always show landing page (not redirecting to dashboard)
    return render_template('index_new.html')


@pages.route('/register', methods=['GET', 'POST'])
def register():
    """Register page"""
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        full_name = request.form.get('full_name')
        
        success, message, user_data = register_user(username, email, password, full_name)
        
        if success:
            return redirect(url_for('pages.login'))
        else:
            return render_template('register.html', error=message)
    
    return render_template('register.html')


@pages.route('/login', methods=['GET', 'POST'])
def login():
    """Login page"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        success, message, user_data = login_user(username, password)
        
        if success:
            return redirect(url_for('pages.dashboard'))
        else:
            return render_template('login.html', error=message)
    
    return render_template('login.html')


@pages.route('/logout', methods=['POST'])
def logout():
    """Logout"""
    logout_user()
    return redirect(url_for('pages.index'))


@pages.route('/dashboard')
def dashboard():
    """Dashboard page"""
    user = get_current_user()
    if not user:
        return redirect(url_for('pages.login'))
    
    daily_summary = get_daily_summary(user.user_id)
    weekly_stats = get_weekly_stats(user.user_id)

    # Build a 7-day calories series for charts (oldest -> newest)
    end_date = datetime.utcnow().date()
    start_date = end_date - timedelta(days=6)
    daily_rows = (
        DailyNutrition.query.filter(
            DailyNutrition.user_id == user.user_id,
            DailyNutrition.date >= start_date,
            DailyNutrition.date <= end_date,
        )
        .order_by(DailyNutrition.date.asc())
        .all()
    )

    by_date = {r.date: r for r in daily_rows}
    weekly_labels = []
    weekly_calories = []
    for i in range(7):
        d = start_date + timedelta(days=i)
        weekly_labels.append(d.strftime('%a'))
        row = by_date.get(d)
        weekly_calories.append(float(row.total_calories) if row else 0.0)

    # Compute progress percentages server-side to avoid relying on Jinja builtins
    try:
        cal_pct = int(min(100, (float(daily_summary.get('total_calories', 0)) / Config.DAILY_CALORIE_TARGET) * 100))
    except Exception:
        cal_pct = 0

    try:
        pro_pct = int(min(100, (float(daily_summary.get('total_protein', 0)) / Config.DAILY_PROTEIN_TARGET) * 100))
    except Exception:
        pro_pct = 0

    try:
        fat_pct = int(min(100, (float(daily_summary.get('total_fat', 0)) / Config.DAILY_FAT_TARGET) * 100))
    except Exception:
        fat_pct = 0

    try:
        carbs_pct = int(min(100, (float(daily_summary.get('total_carbohydrates', 0)) / Config.DAILY_CARBS_TARGET) * 100))
    except Exception:
        carbs_pct = 0

    return render_template('dashboard_modern.html', 
                         user=user, 
                         daily_summary=daily_summary,
                         weekly_stats=weekly_stats,
                         weekly_labels=weekly_labels,
                         weekly_calories=weekly_calories,
                         cal_percent=cal_pct,
                         pro_percent=pro_pct,
                         fat_percent=fat_pct,
                         carbs_percent=carbs_pct,
                         is_premium=session.get('premium', False))


@pages.route('/capture')
def capture():
    """Camera capture page"""
    user = get_current_user()
    if not user:
        return redirect(url_for('pages.login'))
    return render_template('capture_modern.html', user=user)


@pages.route('/upload')
def upload():
    """Image upload page"""
    user = get_current_user()
    if not user:
        return redirect(url_for('pages.login'))
    return render_template('upload_modern.html', user=user)


@pages.route('/uploads/<path:filename>')
def uploaded_file(filename):
    if os.path.basename(filename) != filename:
        abort(404)
    return send_from_directory(Config.UPLOAD_FOLDER, filename)


@pages.route('/food-details/<food_name>')
def food_details(food_name):
    """Food details page after detection"""
    user = get_current_user()
    if not user:
        return redirect(url_for('pages.login'))
    
    # Get nutrition data for the food
    from ai_model.food_recognizer import FoodNutritionMapper
    nutrition = FoodNutritionMapper.get_nutrition_for_food(food_name, quantity=250)
    
    # Prepare the data structure expected by our new template
    food_data = {
        'food_identification': {
            'name': food_name.title(),
            'category': nutrition.get('tags', ['Food'])[0] if nutrition.get('tags') else 'Food',
            'confidence': 95
        },
        'serving_details': {
            'serving_size': f'1 serving (~{nutrition.get("serving_size", "1")}g)',
            'estimated_weight_g': 250
        },
        'energy': {
            'calories_kcal': int(nutrition['calories']),
            'health_score': min(10, max(1, 10 - (nutrition.get('sugar', 0) / 5) - (nutrition.get('fat', 0) / 10)))
        },
        'macronutrients': {
            'protein_g': round(nutrition['protein'], 1),
            'carbohydrates_g': round(nutrition['carbohydrates'], 1),
            'fat_g': round(nutrition['fat'], 1),
            'fiber_g': round(nutrition.get('fiber', 0), 1)
        },
        'additional_metrics': {
            'sugar_g': round(nutrition.get('sugar', 0), 1),
            'sodium_mg': nutrition.get('sodium', 0),
            'glycemic_index': nutrition.get('glycemic_index', 'Medium (56-69)')
        },
        'nutritional_quality': {
            'strengths': [
                f"Good source of {nutrient}" for nutrient in ['protein', 'fiber', 'vitamins'] 
                if nutrition.get(nutrient, 0) > 0
            ][:2],  # Limit to 2 strengths
            'concerns': [
                f"High in {nutrient}" for nutrient in ['sugar', 'fat', 'sodium'] 
                if nutrition.get(nutrient, 0) > 10
            ][:3]  # Limit to 3 concerns
        },
        'health_benefits': nutrition.get('tags', [])[:3],
        'overall_assessment': nutrition.get('description', f"A serving of {food_name} provides a good balance of nutrients."),
        'image_url': None
    }

    uploaded_filename = request.args.get('image')
    if uploaded_filename:
        if os.path.basename(uploaded_filename) == uploaded_filename:
            uploaded_path = os.path.join(Config.UPLOAD_FOLDER, uploaded_filename)
            if os.path.exists(uploaded_path):
                food_data['image_url'] = f"/uploads/{uploaded_filename}"

    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    images_dir = os.path.join(project_root, 'frontend', 'static', 'images')
    food_image_filename = f"{food_name.strip().lower().replace(' ', '-')}.jpg"
    food_image_path = os.path.join(images_dir, food_image_filename)
    placeholder_path = os.path.join(images_dir, 'placeholder-food.jpg')

    if food_data['image_url']:
        pass
    elif os.path.exists(food_image_path):
        food_data['image_url'] = f"/static/images/{food_image_filename}"
    elif os.path.exists(placeholder_path):
        food_data['image_url'] = "/static/images/placeholder-food.jpg"

    # Ensure we have at least 2 strengths and 2 concerns
    if len(food_data['nutritional_quality']['strengths']) < 2:
        food_data['nutritional_quality']['strengths'].extend([
            "Contains essential nutrients",
            "Natural food source"
        ][:2 - len(food_data['nutritional_quality']['strengths'])])
        
    if len(food_data['nutritional_quality']['concerns']) < 2:
        food_data['nutritional_quality']['concerns'].extend([
            "Moderate in calories",
            "Consider portion size"
        ][:2 - len(food_data['nutritional_quality']['concerns'])])
    
    return render_template('food-details.html', food_data=food_data)


@pages.route('/history')
def history():
    """Nutrition history page"""
    user = get_current_user()
    if not user:
        return redirect(url_for('pages.login'))

    end_dt = datetime.utcnow()
    start_dt = end_dt - timedelta(days=30)

    entries = (
        NutritionHistory.query.filter(
            NutritionHistory.user_id == user.user_id,
            NutritionHistory.timestamp >= start_dt,
            NutritionHistory.timestamp <= end_dt,
        )
        .order_by(NutritionHistory.timestamp.desc())
        .all()
    )

    history_data = []
    for e in entries:
        image_filename = os.path.basename(e.image_path) if e.image_path else None
        history_data.append(
            {
                'entry_id': e.history_id,
                'food_name': e.food_name,
                'meal_type': e.meal_type,
                'calories': e.calories,
                'protein': e.protein,
                'fat': e.fat,
                'carbohydrates': e.carbohydrates,
                'created_at': e.timestamp,
                'image_filename': image_filename,
            }
        )

    # Calculate summary stats
    total_calories = sum(e['calories'] for e in history_data)
    total_protein = sum(e['protein'] for e in history_data)
    total_carbs = sum(e['carbohydrates'] for e in history_data)

    return render_template(
        'history_modern.html',
        user=user,
        history=history_data,
        total_calories=total_calories,
        total_protein=total_protein,
        total_carbs=total_carbs,
    )


@pages.route('/profile')
def profile():
    """User profile page"""
    user = get_current_user()
    if not user:
        return redirect(url_for('pages.login'))
    
    history_data = get_nutrition_history(user.user_id, days=30)
    meals_logged = sum((record.get('meal_count') or 0) for record in history_data)
    days_tracked = len(history_data)
    total_calories = sum((record.get('total_calories') or 0) for record in history_data)
    
    return render_template('profile_modern.html', 
                         user=user,
                         meals_logged=meals_logged,
                         days_tracked=days_tracked,
                         total_calories=total_calories)


@pages.route('/pricing')
def pricing():
    """Pricing page"""
    return render_template('pricing.html')

# Add subscribe route to redirect to payment
@pages.route('/subscribe')
def subscribe():
    """Redirect to payment page for subscription"""
    user = get_current_user()
    if not user:
        return redirect(url_for('pages.login'))
    return redirect(url_for('pages.payment'))


# Add dummy payment process route
@pages.route('/payment', methods=['GET', 'POST'])
def payment():
    """Dummy payment process for premium plan"""
    user = get_current_user()
    if not user:
        return redirect(url_for('pages.login'))
    stripe_ready = bool(
        Config.STRIPE_PUBLISHABLE_KEY and
        os.environ.get('STRIPE_SECRET_KEY')
    )
    if request.method == 'POST':
        if not Config.ALLOW_DUMMY_PAYMENTS:
            return render_template(
                'payment.html',
                user=user,
                error='Payments are not configured on this server.'
            ), 403
        # Simulate transaction
        import uuid
        transaction_id = str(uuid.uuid4())[:8].upper()  # Fake transaction ID
        amount = 9.99  # Example premium price
        payment_method = request.form.get('payment_method', 'Google Pay')
        
        # Set premium status
        session['premium'] = True
        
        # Show success with transaction details
        return render_template('payment_success.html', 
                               transaction_id=transaction_id, 
                               amount=amount, 
                               payment_method=payment_method, 
                               user=user)
    
    # Show payment form
    payment_error = None
    if not stripe_ready and not Config.ALLOW_DUMMY_PAYMENTS:
        payment_error = (
            'Stripe is not configured. Set STRIPE_SECRET_KEY and STRIPE_PUBLISHABLE_KEY, '
            'or enable ALLOW_DUMMY_PAYMENTS for demo mode.'
        )
    return render_template('payment.html', user=user, error=payment_error)


@pages.route('/analyzer')
def food_analyzer():
    """Advanced AI Food Analyzer page"""
    user = get_current_user()
    if not user:
        return redirect(url_for('pages.login'))
    return render_template('analyzer.html', user=user)


# ==================== API ROUTES ====================

@api.route('/auth/register', methods=['POST'])
def api_register():
    """API: Register user"""
    data = request.get_json()
    
    success, message, user_data = register_user(
        data.get('username'),
        data.get('email'),
        data.get('password'),
        data.get('full_name')
    )
    
    return jsonify({
        'success': success,
        'message': message,
        'user': user_data
    }), 201 if success else 400


@api.route('/auth/login', methods=['POST'])
def api_login():
    """API: Login user"""
    data = request.get_json()
    
    success, message, user_data = login_user(
        data.get('username'),
        data.get('password')
    )
    
    return jsonify({
        'success': success,
        'message': message,
        'user': user_data
    }), 200 if success else 401


@api.route('/auth/logout', methods=['POST'])
@login_required
def api_logout():
    """API: Logout user"""
    success, message = logout_user()
    return jsonify({'success': success, 'message': message})


@api.route('/auth/me', methods=['GET'])
@login_required
def api_get_user():
    """API: Get current user"""
    user = get_current_user()
    return jsonify({'success': True, 'user': user.to_dict()})


@api.route('/auth/profile', methods=['PUT'])
@login_required
def api_update_profile():
    """API: Update user profile"""
    user = get_current_user()
    data = request.get_json()
    
    success, message, user_data = update_user_profile(
        user.user_id,
        full_name=data.get('full_name'),
        age=data.get('age'),
        gender=data.get('gender')
    )
    
    return jsonify({
        'success': success,
        'message': message,
        'user': user_data
    }), 200 if success else 400


@api.route('/auth/account', methods=['DELETE'])
@login_required
def api_delete_account():
    """API: Delete current user account and all related data."""
    user = get_current_user()
    if not user:
        return jsonify({'success': False, 'message': 'User not found'}), 404
    try:
        db.session.delete(user)
        db.session.commit()
        session.clear()
        return jsonify({'success': True, 'message': 'Account deleted'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'Could not delete account: {str(e)}'}), 500


@api.route('/food/recognize', methods=['POST'])
@login_required
def api_recognize_food():
    """API: Recognize food from image"""
    try:
        init_food_recognizer()
        image_path = None

        if 'file' in request.files:
            image_file = request.files['file']
            if image_file.filename == '':
                return jsonify({'success': False, 'message': 'No file selected'}), 400
            if not allowed_file(image_file.filename, Config.ALLOWED_EXTENSIONS):
                return jsonify({'success': False, 'message': 'Invalid file type'}), 400
            success, result = save_upload_file(image_file, Config.UPLOAD_FOLDER)
            if not success:
                return jsonify({'success': False, 'message': result}), 500
            image_path = result
        elif request.is_json:
            data = request.get_json() or {}
            if not data or 'image' not in data:
                return jsonify({'success': False, 'message': 'No image data provided'}), 400
            image_base64 = data['image']
            try:
                import base64
                import io
                from PIL import Image
                import uuid

                if ',' in image_base64:
                    image_data = image_base64.split(',')[1]
                else:
                    image_data = image_base64
                image_bytes = base64.b64decode(image_data)
                image_buffer = io.BytesIO(image_bytes)
                filename = f"{uuid.uuid4()}.jpg"
                image_path = os.path.join(Config.UPLOAD_FOLDER, filename)
                os.makedirs(os.path.dirname(image_path), exist_ok=True)
                Image.open(image_buffer).save(image_path)
            except Exception as e:
                return jsonify({
                    'success': False, 
                    'message': f'Invalid image format: {str(e)}'
                }), 400
        else:
            return jsonify({
                'success': False, 
                'message': 'No image provided. Please upload an image file or provide a base64-encoded image.'
            }), 400

        if not image_path or not os.path.exists(image_path):
            return jsonify({
                'success': False, 
                'message': 'Failed to process image. Please try again.'
            }), 400

        detection_result = food_recognizer.detect_food(image_path)

        if not detection_result['success'] or len(detection_result.get('foods', [])) == 0:
            if os.path.exists(image_path):
                delete_file(image_path)
            available_foods = [f.food_name for f in FoodDatabase.query.all()]
            return jsonify({
                'success': False,
                'message': 'Could not auto-detect food. Please select from available foods.',
                'foods': [],
                'available_foods': available_foods,
            }), 200

        foods = detection_result['foods']

        # Enrich foods with nutrition data
        from ai_model.food_recognizer import FoodNutritionMapper
        enriched_foods = []
        for food in foods:
            food_name = food['name']
            nutrition = FoodNutritionMapper.get_nutrition_for_food(food_name, quantity=250)
            strengths = []
            concerns = []

            if nutrition.get('protein', 0) > 5:
                strengths.append("High in protein")
            if nutrition.get('fiber', 0) > 3:
                strengths.append("Good source of fiber")
            if nutrition.get('carbohydrates', 0) < 20:
                strengths.append("Low in carbs")
            if nutrition.get('fat', 0) < 5:
                strengths.append("Low in fat")
            if nutrition.get('calories', 0) < 150:
                strengths.append("Low calorie")

            if nutrition.get('sugar', 0) > 15:
                concerns.append("High in sugar")
            if nutrition.get('fat', 0) > 15:
                concerns.append("High in fat")
            if nutrition.get('calories', 0) > 400:
                concerns.append("High in calories")
            if nutrition.get('carbohydrates', 0) > 40:
                concerns.append("High in carbs")

            if not strengths:
                strengths = ["Contains essential nutrients", "Natural food source"]
            if not concerns:
                concerns = ["Moderate in calories", "Consider portion size"]

            enriched_food = {
                'name': food_name,
                'confidence': food['confidence'],
                'calories': int(nutrition['calories']),
                'protein': round(nutrition['protein'], 1),
                'carbs': round(nutrition['carbohydrates'], 1),
                'fat': round(nutrition['fat'], 1),
                'fiber': round(nutrition.get('fiber', 0), 1),
                'sugar': round(nutrition.get('sugar', 0), 1),
                'vitamin_c': round(nutrition.get('vitamin_c', 0), 1),
                'vitamin_a': round(nutrition.get('vitamin_a', 0), 1),
                'potassium': round(nutrition.get('potassium', 0), 1),
                'iron': round(nutrition.get('iron', 0), 1),
                'calcium': round(nutrition.get('calcium', 0), 1),
                'sodium': round(nutrition.get('sodium', 0), 1),
                'glycemic_index': nutrition.get('glycemic_index', 'Medium'),
                'antioxidants': nutrition.get('antioxidants', 'Medium'),
                'serving_size': '250g (1 serving)',
                'strengths': strengths[:2],
                'concerns': concerns[:2],
                'description': nutrition.get('description', f'A serving of {food_name}'),
                'tags': nutrition.get('tags', []),
                'benefits': nutrition.get('benefits', []),
                'allergens': nutrition.get('allergens', []),
                'preparation': nutrition.get('preparation', 'Various methods'),
                'health_score': min(10, max(1, 10 - (nutrition.get('sugar', 0) / 5) - (nutrition.get('fat', 0) / 10)))
            }
            enriched_foods.append(enriched_food)
        
        response_payload = {
            'success': True,
            'message': 'Food detection successful',
            'foods': enriched_foods,
            'image_path': image_path,
            'uploaded_filename': os.path.basename(image_path) if image_path else None,
            'uploaded_url': f"/uploads/{os.path.basename(image_path)}" if image_path else None,
        }

        return jsonify(response_payload)
        
    except Exception:
        current_app.logger.exception("Unhandled exception in /api/food/recognize")
        return jsonify({
            'success': False,
            'message': 'An internal error occurred during food recognition.'
        }), 500


# === Food recognizer control APIs ===
@api.route('/food/detection-mode', methods=['GET', 'POST'])
@login_required
def api_food_detection_mode():
    """GET: return detection mode. POST: set detection mode (json {mode: 'strict'|'lenient'})"""
    init_food_recognizer()
    if request.method == 'GET':
        mode = food_recognizer.get_detection_mode()
        return jsonify({'success': True, 'mode': mode})

    data = request.get_json() or {}
    mode = data.get('mode')
    if mode not in ('strict', 'lenient'):
        return jsonify({'success': False, 'message': 'Invalid mode'}), 400
    try:
        food_recognizer.set_detection_mode(mode)
        return jsonify({'success': True, 'mode': food_recognizer.get_detection_mode()})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@api.route('/food/whitelist', methods=['GET', 'POST', 'DELETE'])
@login_required
def api_food_whitelist():
    """Manage whitelist: GET list, POST add (json {item}), DELETE remove (json {item})"""
    init_food_recognizer()
    if request.method == 'GET':
        return jsonify({'success': True, 'whitelist': food_recognizer.get_whitelist()})

    data = request.get_json() or {}
    item = (data.get('item') or '').strip()
    if not item:
        return jsonify({'success': False, 'message': 'Item required'}), 400

    if request.method == 'POST':
        food_recognizer.add_whitelist_item(item)
        return jsonify({'success': True, 'whitelist': food_recognizer.get_whitelist()})

    # DELETE
    food_recognizer.remove_whitelist_item(item)
    return jsonify({'success': True, 'whitelist': food_recognizer.get_whitelist()})


@api.route('/nutrition/add', methods=['POST'])
@login_required
def api_add_nutrition():
    """API: Add food entry to nutrition history"""
    user = get_current_user()
    data = request.get_json() or {}

    food_name = (data.get('food_name') or '').strip()
    if not food_name:
        return jsonify({'success': False, 'message': 'food_name is required'}), 400

    try:
        quantity = float(data.get('quantity', 1))
        calories = float(data.get('calories', 0))
        protein = float(data.get('protein', 0))
        fat = float(data.get('fat', 0))
        carbs = float(data.get('carbohydrates', 0))
        confidence = float(data.get('confidence', 0))
    except (TypeError, ValueError):
        return jsonify({'success': False, 'message': 'Invalid numeric value in payload'}), 400

    if quantity <= 0:
        return jsonify({'success': False, 'message': 'quantity must be greater than zero'}), 400
    
    success, message, entry = add_food_entry(
        user.user_id,
        food_name=food_name,
        quantity=quantity,
        calories=calories,
        protein=protein,
        fat=fat,
        carbs=carbs,
        meal_type=data.get('meal_type', get_meal_type_from_time()),
        image_path=data.get('image_path'),
        confidence=confidence
    )
    
    return jsonify({
        'success': success,
        'message': message,
        'entry': entry
    }), 201 if success else 400


@api.route('/nutrition/daily', methods=['GET'])
@login_required
def api_get_daily():
    """API: Get daily nutrition summary"""
    user = get_current_user()
    
    daily_summary = get_daily_summary(user.user_id)
    
    # Add targets and percentages
    daily_summary['targets'] = {
        'calories': Config.DAILY_CALORIE_TARGET,
        'protein': Config.DAILY_PROTEIN_TARGET,
        'fat': Config.DAILY_FAT_TARGET,
        'carbs': Config.DAILY_CARBS_TARGET
    }
    
    daily_summary['percentages'] = {
        'calories': NutritionCalculator.calculate_percentage(
            daily_summary['total_calories'], 
            Config.DAILY_CALORIE_TARGET
        ),
        'protein': NutritionCalculator.calculate_percentage(
            daily_summary['total_protein'],
            Config.DAILY_PROTEIN_TARGET
        ),
        'fat': NutritionCalculator.calculate_percentage(
            daily_summary['total_fat'],
            Config.DAILY_FAT_TARGET
        ),
        'carbs': NutritionCalculator.calculate_percentage(
            daily_summary['total_carbohydrates'],
            Config.DAILY_CARBS_TARGET
        )
    }
    
    return jsonify(daily_summary)


@api.route('/nutrition/history', methods=['GET'])
@login_required
def api_get_history():
    """API: Get nutrition history"""
    user = get_current_user()
    days = request.args.get('days', 7, type=int)
    
    history = get_nutrition_history(user.user_id, days)
    
    return jsonify({
        'success': True,
        'history': history
    })


@api.route('/nutrition/weekly', methods=['GET'])
@login_required
def api_get_weekly():
    """API: Get weekly statistics"""
    user = get_current_user()
    
    stats = get_weekly_stats(user.user_id)
    
    return jsonify(stats)


@api.route('/nutrition/delete/<int:entry_id>', methods=['DELETE'])
@login_required
def api_delete_entry(entry_id):
    """API: Delete food entry"""
    user = get_current_user()
    
    success, message = delete_food_entry(entry_id, user.user_id)
    
    return jsonify({
        'success': success,
        'message': message
    }), 200 if success else 400


@api.route('/food/search', methods=['GET'])
def api_search_foods():
    """API: Search food database"""
    query = request.args.get('q', '', type=str)
    
    if not query or len(query) < 2:
        return jsonify({'success': False, 'message': 'Query too short'}), 400
    
    foods = search_foods(query)
    
    return jsonify({
        'success': True,
        'foods': foods
    })


@api.route('/food/nutrition', methods=['GET'])
def api_get_food_nutrition():
    """API: Get nutrition for detected food"""
    food_name = request.args.get('food', '', type=str)
    quantity = request.args.get('quantity', 100, type=float)
    
    if not food_name:
        return jsonify({'success': False, 'message': 'Food name required'}), 400
    
    from ai_model.food_recognizer import FoodNutritionMapper
    nutrition = FoodNutritionMapper.get_nutrition_for_food(food_name, quantity)
    
    return jsonify({
        'success': True,
        'food_name': food_name,
        'quantity': quantity,
        'nutrition': nutrition
    })


@api.route('/payment/gpay', methods=['POST'])
@login_required
def api_dummy_gpay_payment():
    """Dummy Google Pay transaction for premium plan"""
    if not Config.ALLOW_DUMMY_PAYMENTS:
        return jsonify({
            'success': False,
            'message': 'Dummy payments are disabled on this server.'
        }), 403

    data = request.get_json()
    # Simulate payment processing (no real transaction)
    # In a real system, integrate with Google Pay API
    payment_method = data.get('payment_method', 'dummy')
    amount = data.get('amount', 9.99)  # Example premium price
    
    # Simulate success
    session['premium'] = True
    
    return jsonify({
        'success': True,
        'message': f'Dummy payment of ${amount} via {payment_method} successful. Premium activated.',
        'premium_activated': True
    }), 200
