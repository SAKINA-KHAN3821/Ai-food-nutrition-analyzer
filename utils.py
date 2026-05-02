import os
import json
from datetime import datetime
from PIL import Image
import cv2
import numpy as np
import uuid
from werkzeug.utils import secure_filename

def allowed_file(filename, allowed_extensions):
    """Check if file has allowed extension"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions


def save_upload_file(file, upload_folder):
    """
    Save uploaded file and return path
    
    Args:
        file: File object from request
        upload_folder: Folder to save file
    
    Returns:
        tuple: (success, file_path or error_message)
    """
    try:
        if not os.path.exists(upload_folder):
            os.makedirs(upload_folder)
        
        # Create unique, sanitized filename
        timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S_')
        original_name = secure_filename(file.filename or '')
        if not original_name:
            original_name = 'upload.jpg'
        filename = f"{timestamp}{uuid.uuid4().hex[:8]}_{original_name}"
        filepath = os.path.join(upload_folder, filename)
        
        # Save file
        file.save(filepath)
        return True, filepath
    
    except Exception as e:
        return False, str(e)


def resize_image(image_path, size=(640, 640)):
    """Resize image to standard size"""
    try:
        img = Image.open(image_path)
        img = img.resize(size, Image.Resampling.LANCZOS)
        img.save(image_path)
        return True
    except Exception as e:
        print(f"Image resize error: {str(e)}")
        return False


def convert_image_to_rgb(image_path):
    """Convert image to RGB if needed"""
    try:
        img = Image.open(image_path)
        if img.mode != 'RGB':
            img = img.convert('RGB')
            img.save(image_path)
        return True
    except Exception as e:
        print(f"Image conversion error: {str(e)}")
        return False


def get_image_dimensions(image_path):
    """Get image dimensions"""
    try:
        img = Image.open(image_path)
        return img.size
    except:
        return None


def delete_file(file_path):
    """Safely delete a file"""
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
        return True
    except:
        return False


def load_food_database_json(json_path):
    """
    Load food database from JSON file
    
    Args:
        json_path: Path to JSON file
    
    Returns:
        list: Food items
    """
    try:
        with open(json_path, 'r') as f:
            return json.load(f)
    except:
        return []


def round_nutrition(value, decimals=1):
    """Round nutrition values"""
    return round(float(value), decimals)


def format_nutrition_data(nutrition_dict):
    """Format nutrition data for display"""
    return {
        'calories': round_nutrition(nutrition_dict.get('calories', 0)),
        'protein': round_nutrition(nutrition_dict.get('protein', 0)),
        'fat': round_nutrition(nutrition_dict.get('fat', 0)),
        'carbohydrates': round_nutrition(nutrition_dict.get('carbohydrates', 0))
    }


def validate_email(email):
    """Simple email validation"""
    return '@' in email and '.' in email.split('@')[1]


def validate_username(username):
    """Validate username"""
    return len(username) >= 3 and len(username) <= 30


def get_meal_type_from_time():
    """Determine meal type from current time"""
    hour = datetime.now().hour
    
    if 5 <= hour < 11:
        return 'breakfast'
    elif 11 <= hour < 16:
        return 'lunch'
    elif 16 <= hour < 20:
        return 'snack'
    elif 20 <= hour < 23:
        return 'dinner'
    else:
        return 'other'


class NutritionCalculator:
    """Helper class for nutrition calculations"""
    
    @staticmethod
    def calculate_percentage(value, daily_target):
        """Calculate percentage of daily target"""
        if daily_target == 0:
            return 0
        return (value / daily_target) * 100
    
    @staticmethod
    def get_macronutrient_ratio(protein, fat, carbs):
        """Calculate macronutrient ratio"""
        total = protein + fat + carbs
        if total == 0:
            return {'protein': 0, 'fat': 0, 'carbs': 0}
        
        return {
            'protein': round((protein / total) * 100, 1),
            'fat': round((fat / total) * 100, 1),
            'carbs': round((carbs / total) * 100, 1)
        }
    
    @staticmethod
    def get_calorie_breakdown(protein, fat, carbs):
        """Calculate calorie breakdown from macros"""
        # 1g protein = 4 calories, 1g fat = 9 calories, 1g carbs = 4 calories
        return {
            'protein_calories': protein * 4,
            'fat_calories': fat * 9,
            'carbs_calories': carbs * 4,
            'total_calories': (protein * 4) + (fat * 9) + (carbs * 4)
        }


class ImageProcessor:
    """Image processing utility class"""
    
    @staticmethod
    def read_image(image_path):
        """Read image using OpenCV"""
        img = cv2.imread(image_path)
        if img is None:
            return None
        return cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    
    @staticmethod
    def resize_image_cv2(image, size=(640, 640)):
        """Resize image using OpenCV"""
        return cv2.resize(image, size, interpolation=cv2.INTER_LINEAR)
    
    @staticmethod
    def normalize_image(image):
        """Normalize image for model input"""
        return image.astype(np.float32) / 255.0
    
    @staticmethod
    def preprocess_image(image_path, target_size=(640, 640)):
        """
        Preprocess image for AI model
        
        Args:
            image_path: Path to image file
            target_size: Target image size
        
        Returns:
            tuple: (image_array, original_dimensions) or (None, None) if error
        """
        try:
            img = ImageProcessor.read_image(image_path)
            if img is None:
                return None, None
            
            original_size = img.shape[:2]
            img_resized = ImageProcessor.resize_image_cv2(img, target_size)
            img_normalized = ImageProcessor.normalize_image(img_resized)
            
            return img_normalized, original_size
        except Exception as e:
            print(f"Image preprocessing error: {str(e)}")
            return None, None
