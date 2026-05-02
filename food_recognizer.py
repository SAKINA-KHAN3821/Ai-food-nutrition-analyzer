"""
Food Recognition Module using YOLOv8
"""

from ultralytics import YOLO
import numpy as np
from backend.utils import ImageProcessor
import os

class FoodRecognizer:
    """
    YOLOv8-based food recognition model
    """
    
    def __init__(self, model_path=None, confidence_threshold=0.25):
        """
        Initialize food recognizer with food-specific YOLO model
        
        Args:
            model_path: Path to YOLOv8 model (default: uses food-specific model)
            confidence_threshold: Confidence threshold for detections (default: 0.25)
        """
        self.confidence_threshold = confidence_threshold
        self.model = None
        
        # Default to food-specific model if no path provided
        if model_path is None:
            import os
            model_path = os.path.join('ai_model', 'yolov8s-food.pt')
            
            # If food model doesn't exist, use the base model (will be less accurate)
            if not os.path.exists(model_path):
                print("[WARNING] Food-specific model not found. Using base YOLOv8 model (lower accuracy).")
                model_path = 'yolov8n.pt'
        
        self.load_model(model_path)
    
    def load_model(self, model_path):
        """
        Load YOLOv8 model
        
        Args:
            model_path: Path to model file
        """
        try:
            # YOLOv8 will auto-download if not found
            self.model = YOLO(model_path)
            print(f"Model loaded: {model_path}")
        except Exception as e:
            print(f"Error loading model: {str(e)}")
            self.model = None
    
    def detect_food(self, image_path):
        """
        Detect foods in image with enhanced debug logging
        
        Args:
            image_path: Path to image file
        
        Returns:
            dict: Detection results with food items and confidence scores
        """
        print(f"[DEBUG] Starting food detection for: {image_path}")
        
        if self.model is None:
            error_msg = 'Model not loaded'
            print(f"[ERROR] {error_msg}")
            return {'success': False, 'message': error_msg, 'foods': []}
        
        try:
            # Load image directly - YOLO can handle various formats
            import cv2
            print("[DEBUG] Loading image with OpenCV...")
            img = cv2.imread(image_path)
            
            if img is None:
                error_msg = 'Could not read image file. Please check the file path and format.'
                print(f"[ERROR] {error_msg}")
                return {'success': False, 'message': error_msg, 'foods': []}
            
            original_size = img.shape[:2]
            print(f"[DEBUG] Image loaded successfully. Size: {original_size}")
            
            # Run inference with improved parameters for food detection
            print("[DEBUG] Running YOLO inference with food detection...")
            results = self.model(img, 
                              conf=self.confidence_threshold,
                              iou=0.45,  # Slightly lower IoU for better detection of overlapping foods
                              agnostic_nms=True,  # Better for food classes that might be similar
                              max_det=10,  # Limit to 10 detections per image
                              verbose=False)
            print("[DEBUG] YOLO inference completed")
            
            detected_foods = []
            all_detections = []
            
            if not results:
                print("[WARNING] No detection results returned from YOLO model")
            else:
                print(f"[DEBUG] Processing {len(results)} detection results...")
                
                for i, result in enumerate(results):
                    print(f"[DEBUG] Result {i+1}:")
                    print(f"  - Boxes: {len(result.boxes) if result.boxes else 0} detected")
                    print(f"  - Classes: {len(result.names) if hasattr(result, 'names') else 'N/A'} available")
                    
                    if result.boxes is not None:
                        for j, box in enumerate(result.boxes):
                            confidence = float(box.conf)
                            class_id = int(box.cls)
                            class_name = result.names[class_id] if hasattr(result, 'names') and result.names else str(class_id)
                            all_detections.append({
                                'class_id': class_id,
                                'class_name': class_name,
                                'confidence': confidence,
                                'bbox': box.xyxy[0].tolist() if len(box.xyxy) > 0 else []
                            })
                            
                            # Filter for food-related detections
                            is_food = self._is_food_item(class_name)
                            print(f"  - Detection {j+1}: {class_name} (confidence: {confidence:.2f}) - Food: {is_food}")
                            
                            if is_food:
                                detected_foods.append({
                                    'name': class_name,
                                    'confidence': round(confidence, 3),
                                    'class_id': class_id,
                                    'bbox': box.xyxy[0].tolist() if len(box.xyxy) > 0 else []
                                })
            
            # Debug output
            print("\n[DEBUG] Detection Summary:")
            print(f"- Total detections: {len(all_detections)}")
            print(f"- Food detections: {len(detected_foods)}")
            
            if all_detections:
                print("\n[DEBUG] All detected objects:")
                for i, det in enumerate(all_detections):
                    print(f"  {i+1}. {det['class_name']} (ID: {det['class_id']}, Conf: {det['confidence']:.2f})")
            
            if detected_foods:
                print("\n[DEBUG] Detected foods:")
                for i, food in enumerate(detected_foods):
                    print(f"  {i+1}. {food['name']} (Conf: {food['confidence']:.2f})")
            else:
                print("\n[WARNING] No food items detected in the image")
                if all_detections:
                    print("[DEBUG] All detected objects that were not classified as food:")
                    for i, det in enumerate(all_detections):
                        print(f"  {i+1}. {det['class_name']} (ID: {det['class_id']}, Conf: {det['confidence']:.2f})")
            
            return {
                'success': True,
                'message': 'Detection completed',
                'foods': detected_foods,
                'all_detections': all_detections,
                'image_size': original_size
            }
        
        except Exception as e:
            print(f"[ERROR] Detection error: {str(e)}")
            return {
                'success': False,
                'message': f'Detection error: {str(e)}',
                'foods': []
            }
    
    def _is_food_item(self, class_name):
        """
        Check if detected class is a food item
        Expanded to include more food items and be more lenient with detections
        """
        # Expanded whitelist of food-related items
        food_whitelist = {
            # Fruits
            'apple', 'banana', 'orange', 'grape', 'strawberry', 'pineapple',
            'mango', 'watermelon', 'pear', 'peach', 'plum', 'kiwi', 'cherry',
            'blueberry', 'raspberry', 'blackberry', 'lemon', 'lime', 'coconut',
            'avocado', 'pomegranate', 'fig', 'date', 'apricot', 'nectarine',
            'cantaloupe', 'honeydew', 'papaya', 'guava', 'passion fruit',
            'dragon fruit', 'star fruit', 'persimmon', 'lychee', 'mangosteen',
            'jackfruit', 'durian', 'rambutan', 'longan', 'soursop', 'sapodilla',
            
            # Vegetables
            'broccoli', 'carrot', 'lettuce', 'tomato', 'potato', 'cucumber',
            'onion', 'garlic', 'pepper', 'bell pepper', 'chili', 'eggplant',
            'zucchini', 'squash', 'pumpkin', 'sweet potato', 'yam', 'corn',
            'pea', 'green bean', 'asparagus', 'celery', 'cabbage', 'cauliflower',
            'brussels sprout', 'kale', 'spinach', 'chard', 'arugula', 'endive',
            'radish', 'beet', 'turnip', 'rutabaga', 'parsnip', 'artichoke',
            'fennel', 'leek', 'scallion', 'shallot', 'ginger', 'mushroom',
            
            # Baked goods & grains
            'bread', 'pizza', 'sandwich', 'donut', 'cake', 'cookie', 'biscuit',
            'bagel', 'croissant', 'muffin', 'waffle', 'pancake', 'crepe',
            'pita', 'naan', 'tortilla', 'taco', 'burrito', 'quesadilla',
            'baguette', 'sourdough', 'brioche', 'focaccia', 'ciabatta', 'pumpernickel',
            'rye', 'multigrain', 'whole wheat', 'white bread', 'soda bread',
            'cornbread', 'pancake', 'waffle', 'muffin', 'scone', 'biscotti',
            'brownie', 'cupcake', 'cheesecake', 'pie', 'tart', 'pastry',
            
            # Prepared / common dishes
            'salad', 'soup', 'stew', 'curry', 'stir-fry', 'pasta', 'noodles',
            'spaghetti', 'lasagna', 'ravioli', 'dumpling', 'sushi', 'sashimi',
            'burger', 'hot dog', 'taco', 'burrito', 'quesadilla', 'enchilada',
            'tamale', 'fajita', 'tostada', 'empanada', 'samosa', 'spring roll',
            'egg roll', 'dumpling', 'gyoza', 'potsticker', 'pierogi', 'ravioli',
            'tortellini', 'gnocchi', 'risotto', 'paella', 'jambalaya', 'gumbo',
            'goulash', 'stew', 'chili', 'chowder', 'bisque', 'ramen', 'udon',
            'soba', 'pho', 'pad thai', 'fried rice', 'nasi goreng', 'biryani',
            'kebab', 'shish kebab', 'kabob', 'satay', 'teriyaki', 'tempura',
            
            # Proteins & dairy
            'chicken', 'turkey', 'duck', 'goose', 'quail', 'pheasant',
            'beef', 'steak', 'roast beef', 'brisket', 'ribs', 'short ribs',
            'pork', 'bacon', 'ham', 'sausage', 'salami', 'pepperoni',
            'lamb', 'goat', 'veal', 'venison', 'bison', 'buffalo',
            'fish', 'salmon', 'tuna', 'cod', 'halibut', 'trout', 'bass',
            'tilapia', 'mahi mahi', 'swordfish', 'sardine', 'anchovy',
            'shrimp', 'prawn', 'lobster', 'crab', 'scallop', 'clam',
            'mussel', 'oyster', 'squid', 'octopus', 'crayfish', 'crawfish',
            'egg', 'omelet', 'frittata', 'quiche', 'tofu', 'tempeh', 'seitan',
            'cheese', 'cheddar', 'mozzarella', 'parmesan', 'gouda', 'brie',
            'camembert', 'blue cheese', 'feta', 'goat cheese', 'ricotta',
            'cottage cheese', 'cream cheese', 'yogurt', 'kefir', 'butter',
            'milk', 'cream', 'sour cream', 'buttermilk', 'heavy cream',
            'whipped cream', 'ice cream', 'gelato', 'sorbet', 'sherbet',
            
            # Snacks & sweets
            'chip', 'potato chip', 'tortilla chip', 'corn chip', 'pretzel',
            'popcorn', 'cracker', 'rice cake', 'granola bar', 'energy bar',
            'protein bar', 'trail mix', 'nuts', 'almond', 'cashew', 'walnut',
            'pecan', 'pistachio', 'hazelnut', 'macadamia', 'peanut', 'peanut butter',
            'almond butter', 'sunflower seed', 'pumpkin seed', 'sesame seed',
            'chia seed', 'flaxseed', 'candy', 'chocolate', 'dark chocolate',
            'milk chocolate', 'white chocolate', 'fudge', 'caramel', 'toffee',
            'nougat', 'marshmallow', 'gummy', 'jelly bean', 'licorice',
            'lollipop', 'candy cane', 'gumdrop', 'taffy', 'brittle',
            
            # Beverages
            'coffee', 'espresso', 'cappuccino', 'latte', 'mocha', 'americano',
            'tea', 'green tea', 'black tea', 'oolong tea', 'white tea',
            'herbal tea', 'chai', 'matcha', 'hot chocolate', 'cocoa',
            'smoothie', 'milkshake', 'juice', 'orange juice', 'apple juice',
            'grape juice', 'cranberry juice', 'tomato juice', 'vegetable juice',
            'soda', 'cola', 'lemonade', 'iced tea', 'sports drink', 'energy drink',
            'water', 'sparkling water', 'mineral water', 'coconut water',
            'alcohol', 'beer', 'wine', 'red wine', 'white wine', 'champagne',
            'cider', 'sake', 'soju', 'cocktail', 'martini', 'margarita',
            'mojito', 'daiquiri', 'pina colada', 'whiskey', 'bourbon',
            'scotch', 'vodka', 'gin', 'rum', 'tequila', 'brandy', 'cognac',
            'liqueur', 'amaretto', 'baileys', 'kahlua', 'grand marnier',
            'cointreau', 'triple sec', 'schnapps', 'absinthe', 'ouzo', 'sambuca',
            'jagermeister', 'fireball', 'sour', 'sangria', 'mimosa', 'bellini',
            'spritz', 'aperol spritz', 'negroni', 'aperol', 'campari',
            
            # Common food-related terms that might appear in class names
            'food', 'meal', 'dish', 'cuisine', 'recipe', 'ingredient',
            'breakfast', 'brunch', 'lunch', 'dinner', 'supper', 'snack',
            'appetizer', 'entree', 'main course', 'side dish', 'dessert',
            'beverage', 'drink', 'sauce', 'dressing', 'dip', 'spread',
            'condiment', 'seasoning', 'herb', 'spice', 'garnish'
        }

        class_lower = class_name.lower().strip()
        # Normalize variations in class names
        class_norm = class_lower.replace('-', ' ').replace('_', ' ')

        # Respect user-managed whitelist first.
        custom_whitelist = getattr(self, 'whitelist', set())
        if custom_whitelist:
            return any(
                class_norm == item or item in class_norm
                for item in custom_whitelist
            )

        # Detection mode toggles strict vs lenient behavior.
        if self.get_detection_mode() == 'lenient' and self._lenient_food_check(class_norm):
            print(f"[DEBUG] Lenient mode accepted: {class_name}")
            return True
        
        # Check for exact match or partial match with any food term
        for food_term in food_whitelist:
            if (class_norm == food_term or 
                food_term in class_norm or 
                any(term in class_norm for term in food_term.split())):
                print(f"[DEBUG] Detected food: {class_name} (matched term: {food_term})")
                return True
                
        print(f"[DEBUG] Not a food item: {class_name}")
        return False

    # Detection mode & whitelist management
    def set_detection_mode(self, mode: str):
        """Set detection mode: 'strict' or 'lenient'"""
        mode = (mode or '').lower().strip()
        if mode not in ('strict', 'lenient'):
            raise ValueError('Invalid detection mode')
        self.detection_mode = mode

    def get_detection_mode(self):
        """Get current detection mode"""
        return getattr(self, 'detection_mode', 'strict')

    def add_whitelist_item(self, item: str):
        """Add a new whitelist item (food class)"""
        if not hasattr(self, 'whitelist'):
            self.whitelist = set()
        self.whitelist.add(item.lower().strip())

    def remove_whitelist_item(self, item: str):
        """Remove an item from whitelist"""
        if hasattr(self, 'whitelist'):
            self.whitelist.discard(item.lower().strip())

    def get_whitelist(self):
        """Return current whitelist as list"""
        if hasattr(self, 'whitelist') and self.whitelist:
            return sorted(list(self.whitelist))
        # Fallback to the built-in conservative list
        return sorted(list({
            'apple', 'banana', 'orange', 'grape', 'strawberry', 'pineapple',
            'broccoli', 'carrot', 'lettuce', 'tomato', 'potato',
            'bread', 'pizza', 'sandwich', 'donut', 'cake', 'cookie',
            'bagel', 'croissant', 'muffin', 'waffle', 'pita', 'baguette',
            'salad', 'soup', 'pasta', 'spaghetti', 'noodles', 'burger', 'hot dog', 'taco', 'burrito',
            'chicken', 'egg', 'fish', 'beef', 'pork', 'tofu', 'cheese', 'milk',
            'chip', 'popcorn', 'candy', 'chocolate', 'ice cream', 'popsicle'
        }))

    def _lenient_food_check(self, class_name: str):
        """Lenient fallback: broader keyword matching"""
        keywords = [
            'apple', 'banana', 'orange', 'fruit', 'pizza', 'sandwich', 'cake',
            'donut', 'cookie', 'food', 'broccoli', 'carrot', 'hot dog',
            'bread', 'chicken', 'meat', 'salad', 'pasta', 'bowl', 'plate', 'cup'
        ]
        class_lower = class_name.lower()
        return any(k in class_lower for k in keywords)

    def detect_multiple_foods(self, image_path, return_top_n=5):
        """
        Detect multiple foods and return top N by confidence
        
        Args:
            image_path: Path to image file
            return_top_n: Number of top detections to return
        
        Returns:
            list: Top food detections sorted by confidence
        """
        result = self.detect_food(image_path)
        
        if not result['success']:
            return []
        
        foods = result['foods']
        # Sort by confidence and return top N
        foods_sorted = sorted(foods, key=lambda x: x['confidence'], reverse=True)
        return foods_sorted[:return_top_n]


class FoodNutritionMapper:
    """
    Map detected foods to nutrition data
    """
    
    # Common food nutrition data (in per 100g) with extended info
    FOOD_NUTRITION_DB = {
        'apple': {
            'calories': 52, 'protein': 0.3, 'fat': 0.2, 'carbs': 14, 'fiber': 2.4, 'sugar': 10.4,
            'vitamin_c': 4.6, 'potassium': 107, 'vitamin_a': 3, 'iron': 0.1,
            'glycemic_index': 39, 'antioxidants': 'High',
            'description': 'A crisp and refreshing fruit rich in fiber and natural antioxidants. Perfect for a healthy snack.',
            'tags': ['Fruit', 'Healthy', 'Low-Calorie', 'Snack'],
            'benefits': ['Heart health', 'Digestive health', 'Weight management'],
            'allergens': [],
            'preparation': 'Raw, baked, or in smoothies'
        },
        'banana': {
            'calories': 89, 'protein': 1.1, 'fat': 0.3, 'carbs': 23, 'fiber': 2.6, 'sugar': 12,
            'vitamin_c': 8.7, 'potassium': 358, 'vitamin_b6': 0.4, 'magnesium': 27,
            'glycemic_index': 51, 'antioxidants': 'Medium',
            'description': 'A nutrient-dense fruit packed with potassium, perfect for post-workout recovery.',
            'tags': ['Fruit', 'Potassium-Rich', 'Energy', 'Healthy'],
            'benefits': ['Muscle recovery', 'Heart health', 'Digestive health', 'Energy boost'],
            'allergens': [],
            'preparation': 'Raw, smoothies, baking'
        },
        'orange': {
            'calories': 47, 'protein': 0.9, 'fat': 0.1, 'carbs': 12, 'fiber': 2.4, 'sugar': 9.3,
            'vitamin_c': 53.2, 'potassium': 181, 'vitamin_a': 11, 'folate': 30,
            'glycemic_index': 43, 'antioxidants': 'High',
            'description': 'A citrus fruit loaded with vitamin C, supporting immunity and overall health.',
            'tags': ['Fruit', 'Citrus', 'Vitamin C', 'Fresh'],
            'benefits': ['Immune support', 'Skin health', 'Heart health', 'Antioxidant protection'],
            'allergens': [],
            'preparation': 'Raw, juice, salads'
        },
        'broccoli': {
            'calories': 34, 'protein': 2.8, 'fat': 0.4, 'carbs': 7, 'fiber': 2.4, 'sugar': 1.7,
            'vitamin_c': 89.2, 'vitamin_k': 101.6, 'folate': 63, 'potassium': 316,
            'glycemic_index': 15, 'antioxidants': 'Very High',
            'description': 'A cruciferous vegetable rich in nutrients and antioxidants, excellent for weight management.',
            'tags': ['Vegetable', 'Healthy', 'Low-Calorie', 'Green'],
            'benefits': ['Cancer prevention', 'Heart health', 'Bone health', 'Detoxification'],
            'allergens': [],
            'preparation': 'Steamed, roasted, raw in salads'
        },
        'carrot': {
            'calories': 41, 'protein': 0.9, 'fat': 0.2, 'carbs': 10, 'fiber': 2.8, 'sugar': 4.7,
            'vitamin_a': 835, 'vitamin_k': 13.2, 'potassium': 320, 'vitamin_c': 5.9,
            'glycemic_index': 39, 'antioxidants': 'High',
            'description': 'A root vegetable rich in beta-carotene, supporting eye health and immunity.',
            'tags': ['Vegetable', 'Beta-Carotene', 'Healthy', 'Orange'],
            'benefits': ['Eye health', 'Immune support', 'Skin health', 'Digestive health'],
            'allergens': [],
            'preparation': 'Raw, cooked, juice'
        },
        'pizza': {
            'calories': 285, 'protein': 12, 'fat': 10, 'carbs': 36, 'fiber': 1.8, 'sugar': 3.4,
            'calcium': 188, 'iron': 2.5, 'sodium': 598, 'vitamin_a': 102,
            'glycemic_index': 60, 'antioxidants': 'Low',
            'description': 'A classic Italian pizza featuring a thin crust topped with tomato sauce, fresh mozzarella, and basil. Simple, flavorful, and satisfying.',
            'tags': ['Pizza', 'Italian', 'Comfort Food', 'Savory'],
            'benefits': ['Calcium source', 'Protein source'],
            'allergens': ['Gluten', 'Dairy'],
            'preparation': 'Baked, traditionally at high temperature'
        },
        'sandwich': {
            'calories': 350, 'protein': 15, 'fat': 12, 'carbs': 45, 'fiber': 3.2, 'sugar': 5,
            'iron': 2.8, 'calcium': 120, 'sodium': 780, 'vitamin_b12': 0.5,
            'glycemic_index': 69, 'antioxidants': 'Medium',
            'description': 'A classic sandwich with protein-rich fillings between slices of bread. Perfect for lunch or quick meals.',
            'tags': ['Sandwich', 'Lunch', 'Protein', 'Convenient'],
            'benefits': ['Balanced meal', 'Protein source', 'Convenient nutrition'],
            'allergens': ['Gluten', 'Dairy'],
            'preparation': 'Assembled, can be toasted'
        },
        'cake': {
            'calories': 280, 'protein': 3, 'fat': 10, 'carbs': 45, 'fiber': 0.8, 'sugar': 32,
            'calcium': 32, 'iron': 1.2, 'sodium': 240, 'vitamin_a': 15,
            'glycemic_index': 68, 'antioxidants': 'Low',
            'description': 'A delicious baked dessert perfect for celebrations and special occasions.',
            'tags': ['Dessert', 'Bakery', 'Sweet', 'Cake'],
            'benefits': ['Mood enhancement', 'Social bonding'],
            'allergens': ['Gluten', 'Dairy', 'Eggs'],
            'preparation': 'Baked, various frostings available'
        },
        'bread': {
            'calories': 265, 'protein': 9, 'fat': 3, 'carbs': 49, 'fiber': 2.7, 'sugar': 3.8,
            'iron': 3.6, 'calcium': 142, 'sodium': 490, 'vitamin_b1': 0.4,
            'glycemic_index': 71, 'antioxidants': 'Low',
            'description': 'A staple carbohydrate source, great for sandwiches or as a side with meals.',
            'tags': ['Grain', 'Carbs', 'Bakery', 'Bread'],
            'benefits': ['Energy source', 'B-vitamins', 'Fiber source'],
            'allergens': ['Gluten'],
            'preparation': 'Baked, toasted, various types'
        },
        'chicken': {
            'calories': 165, 'protein': 31, 'fat': 3.6, 'carbs': 0, 'fiber': 0, 'sugar': 0,
            'vitamin_b3': 7.5, 'vitamin_b6': 0.5, 'phosphorus': 203, 'selenium': 22,
            'glycemic_index': 0, 'antioxidants': 'Low',
            'description': 'Lean protein source, versatile and widely consumed poultry meat.',
            'tags': ['Protein', 'Lean Meat', 'Poultry', 'Versatile'],
            'benefits': ['High-quality protein', 'Muscle building', 'Low fat'],
            'allergens': [],
            'preparation': 'Grilled, baked, roasted, fried'
        },
        'egg': {
            'calories': 155, 'protein': 13, 'fat': 11, 'carbs': 1.1, 'fiber': 0, 'sugar': 0.6,
            'vitamin_a': 540, 'vitamin_d': 2.0, 'vitamin_e': 1.0, 'vitamin_b12': 0.6,
            'glycemic_index': 0, 'antioxidants': 'Medium',
            'description': 'Complete protein source with all essential amino acids, nature\'s perfect food.',
            'tags': ['Protein', 'Complete Protein', 'Versatile', 'Nutrient-Dense'],
            'benefits': ['Complete protein', 'Brain health', 'Eye health', 'Muscle building'],
            'allergens': ['Eggs'],
            'preparation': 'Boiled, fried, scrambled, baked'
        },
        'rice': {
            'calories': 130, 'protein': 2.7, 'fat': 0.3, 'carbs': 28, 'fiber': 0.4, 'sugar': 0.1,
            'manganese': 0.8, 'vitamin_b1': 0.1, 'iron': 0.8, 'vitamin_b3': 1.6,
            'glycemic_index': 73, 'antioxidants': 'Low',
            'description': 'Staple grain providing carbohydrates and energy, base for many cuisines.',
            'tags': ['Grain', 'Carbs', 'Staple', 'Versatile'],
            'benefits': ['Energy source', 'Digestive health', 'Mineral source'],
            'allergens': [],
            'preparation': 'Boiled, steamed, fried'
        },
        'pasta': {
            'calories': 157, 'protein': 5.8, 'fat': 0.9, 'carbs': 31, 'fiber': 1.8, 'sugar': 0.6,
            'iron': 1.3, 'vitamin_b1': 0.1, 'vitamin_b9': 7, 'manganese': 0.3,
            'glycemic_index': 49, 'antioxidants': 'Low',
            'description': 'Wheat-based carbohydrate source, foundation of Italian cuisine.',
            'tags': ['Carbs', 'Italian', 'Comfort Food', 'Versatile'],
            'benefits': ['Energy source', 'B-vitamins', 'Iron source'],
            'allergens': ['Gluten'],
            'preparation': 'Boiled, various sauces'
        },
        'salad': {
            'calories': 25, 'protein': 1.5, 'fat': 0.5, 'carbs': 5, 'fiber': 1.8, 'sugar': 2.5,
            'vitamin_a': 370, 'vitamin_c': 15, 'vitamin_k': 62, 'folate': 38,
            'glycemic_index': 15, 'antioxidants': 'High',
            'description': 'Fresh vegetable-based dish, light and nutritious meal option.',
            'tags': ['Vegetable', 'Light', 'Healthy', 'Fresh'],
            'benefits': ['Vitamins & minerals', 'Hydration', 'Low calorie', 'Fiber source'],
            'allergens': [],
            'preparation': 'Raw vegetables with dressing'
        },
        'yogurt': {
            'calories': 61, 'protein': 3.5, 'fat': 3.3, 'carbs': 4.7, 'fiber': 0, 'sugar': 4.7,
            'calcium': 121, 'vitamin_b2': 0.2, 'vitamin_b12': 0.4, 'phosphorus': 95,
            'glycemic_index': 27, 'antioxidants': 'Low',
            'description': 'Fermented dairy product rich in probiotics and calcium.',
            'tags': ['Dairy', 'Probiotics', 'Calcium', 'Healthy'],
            'benefits': ['Gut health', 'Bone health', 'Immune support', 'Protein source'],
            'allergens': ['Dairy'],
            'preparation': 'Plain or flavored, various consistencies'
        },
        'cheese': {
            'calories': 402, 'protein': 7, 'fat': 33, 'carbs': 3.4, 'fiber': 0, 'sugar': 0.5,
            'calcium': 721, 'phosphorus': 512, 'vitamin_a': 330, 'vitamin_b12': 1.1,
            'glycemic_index': 0, 'antioxidants': 'Low',
            'description': 'Concentrated dairy product, rich in calcium and protein.',
            'tags': ['Dairy', 'Calcium', 'Protein', 'Concentrated'],
            'benefits': ['Calcium source', 'Protein source', 'Bone health'],
            'allergens': ['Dairy'],
            'preparation': 'Various types, melting, grating'
        },
        'fish': {
            'calories': 206, 'protein': 22, 'fat': 12, 'carbs': 0, 'fiber': 0, 'sugar': 0,
            'vitamin_d': 4.0, 'omega_3': 1.8, 'vitamin_b12': 2.4, 'selenium': 36,
            'glycemic_index': 0, 'antioxidants': 'Medium',
            'description': 'Seafood rich in omega-3 fatty acids and high-quality protein.',
            'tags': ['Protein', 'Omega-3', 'Seafood', 'Healthy Fats'],
            'benefits': ['Heart health', 'Brain health', 'Anti-inflammatory', 'High-quality protein'],
            'allergens': ['Fish'],
            'preparation': 'Grilled, baked, fried, raw'
        },
        'potato': {
            'calories': 77, 'protein': 2, 'fat': 0.1, 'carbs': 17, 'fiber': 2.2, 'sugar': 0.8,
            'vitamin_c': 19.7, 'potassium': 421, 'vitamin_b6': 0.3, 'manganese': 0.2,
            'glycemic_index': 78, 'antioxidants': 'Medium',
            'description': 'Versatile starchy vegetable, staple in many cuisines worldwide.',
            'tags': ['Vegetable', 'Starchy', 'Versatile', 'Staple'],
            'benefits': ['Potassium source', 'Vitamin C', 'Energy source'],
            'allergens': [],
            'preparation': 'Baked, boiled, fried, mashed'
        },
        'tomato': {
            'calories': 18, 'protein': 0.9, 'fat': 0.2, 'carbs': 3.9, 'fiber': 1.2, 'sugar': 2.6,
            'vitamin_c': 14, 'vitamin_a': 42, 'potassium': 237, 'vitamin_k': 7.9,
            'glycemic_index': 15, 'antioxidants': 'Very High',
            'description': 'Nutrient-rich fruit often used as vegetable, rich in lycopene.',
            'tags': ['Vegetable', 'Fruit', 'Antioxidant', 'Versatile'],
            'benefits': ['Heart health', 'Prostate health', 'Skin health', 'Antioxidant protection'],
            'allergens': [],
            'preparation': 'Raw, cooked, sauces, salads'
        },
        'spinach': {
            'calories': 23, 'protein': 2.9, 'fat': 0.4, 'carbs': 3.6, 'fiber': 2.2, 'sugar': 0.4,
            'vitamin_a': 469, 'vitamin_c': 28.1, 'vitamin_k': 482.9, 'folate': 194,
            'glycemic_index': 15, 'antioxidants': 'Very High',
            'description': 'Leafy green vegetable packed with vitamins and minerals.',
            'tags': ['Leafy Green', 'Nutrient-Dense', 'Low-Calorie', 'Superfood'],
            'benefits': ['Bone health', 'Eye health', 'Immune support', 'Blood health'],
            'allergens': [],
            'preparation': 'Raw in salads, cooked, smoothies'
        },
        'avocado': {
            'calories': 160, 'protein': 2, 'fat': 14.7, 'carbs': 8.5, 'fiber': 6.7, 'sugar': 0.7,
            'vitamin_c': 10, 'vitamin_e': 2.1, 'vitamin_k': 21, 'potassium': 485,
            'glycemic_index': 15, 'antioxidants': 'High',
            'description': 'Creamy fruit rich in healthy monounsaturated fats.',
            'tags': ['Fruit', 'Healthy Fats', 'Nutrient-Dense', 'Creamy'],
            'benefits': ['Heart health', 'Skin health', 'Eye health', 'Healthy fats'],
            'allergens': [],
            'preparation': 'Raw, guacamole, smoothies, baking'
        },
        'nuts': {
            'calories': 607, 'protein': 21, 'fat': 54, 'carbs': 21, 'fiber': 8.8, 'sugar': 4.3,
            'vitamin_e': 10.6, 'magnesium': 292, 'vitamin_b6': 0.3, 'iron': 3.7,
            'glycemic_index': 15, 'antioxidants': 'High',
            'description': 'Nutrient-dense seeds providing healthy fats, protein, and minerals.',
            'tags': ['Nuts', 'Healthy Fats', 'Protein', 'Energy'],
            'benefits': ['Heart health', 'Brain health', 'Weight management', 'Antioxidants'],
            'allergens': ['Nuts'],
            'preparation': 'Raw, roasted, in recipes'
        },
        'chocolate': {
            'calories': 546, 'protein': 7.6, 'fat': 31, 'carbs': 61, 'fiber': 7, 'sugar': 48,
            'iron': 11.9, 'magnesium': 228, 'copper': 1.8, 'manganese': 1.9,
            'glycemic_index': 40, 'antioxidants': 'Very High',
            'description': 'Cocoa-based treat rich in antioxidants and mood-enhancing compounds.',
            'tags': ['Dessert', 'Antioxidant', 'Mood', 'Indulgence'],
            'benefits': ['Antioxidant protection', 'Mood enhancement', 'Heart health'],
            'allergens': ['Dairy'],
            'preparation': 'Dark, milk, various forms'
        },
        'milk': {
            'calories': 61, 'protein': 3.2, 'fat': 3.3, 'carbs': 4.8, 'fiber': 0, 'sugar': 5,
            'description': 'A dairy product rich in calcium and vitamin D, supporting bone health.',
            'tags': ['Dairy', 'Calcium', 'Drink', 'Beverage']
        },
        'donut': {
            'calories': 452, 'protein': 4, 'fat': 25, 'carbs': 51, 'fiber': 0.7, 'sugar': 25,
            'description': 'A sweet fried pastry, perfect as an occasional indulgence or breakfast treat.',
            'tags': ['Dessert', 'Pastry', 'Sweet', 'Snack']
        },
        'cookie': {
            'calories': 502, 'protein': 6, 'fat': 27, 'carbs': 63, 'fiber': 0.8, 'sugar': 38,
            'description': 'A delightful baked treat, ideal for satisfying sweet cravings with friends and family.',
            'tags': ['Dessert', 'Bakery', 'Sweet', 'Snack']
        },
    }
    
    @staticmethod
    def get_nutrition_for_food(food_name, quantity=100):
        """
        Get nutrition data for detected food
        
        Args:
            food_name: Name of food
            quantity: Quantity in grams (default 100g)
        
        Returns:
            dict: Nutrition data adjusted for quantity
        """
        food_lower = food_name.lower().strip()
        
        # Try exact match first
        if food_lower in FoodNutritionMapper.FOOD_NUTRITION_DB:
            nutrition = FoodNutritionMapper.FOOD_NUTRITION_DB[food_lower].copy()
        else:
            # Try partial match
            nutrition = None
            for key in FoodNutritionMapper.FOOD_NUTRITION_DB:
                if key in food_lower or food_lower in key:
                    nutrition = FoodNutritionMapper.FOOD_NUTRITION_DB[key].copy()
                    break
            
            # Default nutrition if not found
            if nutrition is None:
                nutrition = {
                    'calories': 100,
                    'protein': 5,
                    'fat': 3,
                    'carbs': 15,
                    'fiber': 2,
                    'sugar': 5,
                    'description': f'{food_name} - A nutritious food item.',
                    'tags': ['Food', 'Meal']
                }
        
        # Adjust for quantity (quantity is in grams, nutrition is per 100g)
        factor = quantity / 100.0
        adjusted_nutrition = {
            'calories': round(nutrition['calories'] * factor, 1),
            'protein': round(nutrition['protein'] * factor, 1),
            'carbohydrates': round(nutrition['carbs'] * factor, 1),
            'fat': round(nutrition['fat'] * factor, 1),
            'fiber': round(nutrition.get('fiber', 0) * factor, 1),
            'sugar': round(nutrition.get('sugar', 0) * factor, 1),
            'vitamin_c': round(nutrition.get('vitamin_c', 0) * factor, 1),
            'vitamin_a': round(nutrition.get('vitamin_a', 0) * factor, 1),
            'potassium': round(nutrition.get('potassium', 0) * factor, 1),
            'iron': round(nutrition.get('iron', 0) * factor, 1),
            'calcium': round(nutrition.get('calcium', 0) * factor, 1),
            'sodium': round(nutrition.get('sodium', 0) * factor, 1),
            'glycemic_index': nutrition.get('glycemic_index', 'Medium'),
            'antioxidants': nutrition.get('antioxidants', 'Medium'),
            'description': nutrition.get('description', f'{food_name} - A nutritious food item.'),
            'tags': nutrition.get('tags', ['Food', 'Meal']),
            'benefits': nutrition.get('benefits', []),
            'allergens': nutrition.get('allergens', []),
            'preparation': nutrition.get('preparation', 'Various methods')
        }
        return adjusted_nutrition
    
    @staticmethod
    def get_nutrition_for_multiple_foods(foods, quantities=None):
        """
        Get combined nutrition for multiple foods
        
        Args:
            foods: List of food names
            quantities: List of quantities (default 100g each)
        
        Returns:
            dict: Combined nutrition data
        """
        if quantities is None:
            quantities = [100] * len(foods)
        
        combined = {
            'calories': 0,
            'protein': 0,
            'fat': 0,
            'carbohydrates': 0
        }
        
        for food, qty in zip(foods, quantities):
            nutrition = FoodNutritionMapper.get_nutrition_for_food(food, qty)
            for key in combined:
                combined[key] += nutrition[key]
        
        return combined
