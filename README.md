# Ai-food-nutrition-analyzer
An AI-powered web application that analyzes food images to deliver real-time nutritional insights using YOLOv8 and Flask.
# AI-Based Nutrition Analyzer Using Food Image Recognition

## Project Overview

A **Final Year (TYBSc CS) Web Application** that uses AI-powered image recognition to analyze food nutrition content. Users can capture food images using their webcam or upload photos, and the application automatically detects the food items and provides detailed nutritional information including calories, protein, fat, and carbohydrates.

### Student Details
- **Name**: Sakina Khan
- **College**: Tilak College of Science and Commerce
- **Course**: TYBSc CS (Third Year Bachelor of Science in Computer Science)
- **University**: Mumbai University

---

## Features

✅ **User Authentication**
- Secure registration and login system
- User profiles with personal information
- Session management

✅ **Food Image Recognition**
- AI-powered food detection using YOLOv8
- Real-time webcam capture
- Image upload support
- Confidence scores for detections

✅ **Nutrition Tracking**
- Automatic calculation of nutrients per serving
- Daily nutrition summary (Calories, Protein, Fat, Carbohydrates)
- Meal-type classification (Breakfast, Lunch, Dinner, Snack)
- Weekly nutrition statistics

✅ **Data Management**
- Persistent nutrition history
- Daily and weekly aggregated data
- User nutrition trends
- Food database reference

✅ **User Interface**
- Responsive web design using Bootstrap
- Clean and intuitive dashboard
- Real-time charts and visualizations
- Mobile-friendly layout

---

## Technology Stack

| Component | Technology |
|-----------|-----------|
| **Backend** | Python Flask 2.3.3 |
| **Frontend** | HTML5, CSS3, Bootstrap 5, JavaScript |
| **Database** | SQLite |
| **AI Model** | YOLOv8 (Ultralytics) |
| **Image Processing** | OpenCV, Pillow |
| **Data Processing** | NumPy, Pandas |
| **Charts** | Chart.js |

---

## Project Structure

```
AI-Nutrition-Analyzer/
│
├── app.py                          # Main Flask application entry point
├── config.py                       # Configuration settings
├── requirements.txt                # Python dependencies
├── README.md                       # This file
│
├── backend/
│   ├── __init__.py
│   ├── models.py                   # Database models (SQLAlchemy)
│   ├── auth.py                     # User authentication logic
│   ├── nutrition_tracker.py        # Nutrition calculation & management
│   ├── routes.py                   # Flask routes and API endpoints
│   └── utils.py                    # Helper functions and utilities
│
├── ai_model/
│   ├── __init__.py
│   ├── food_recognizer.py          # YOLOv8 food detection
│   └── nutrition_mapper.py         # Food to nutrition mapping
│
├── frontend/
│   ├── templates/
│   │   ├── base.html               # Base template
│   │   ├── index.html              # Home page
│   │   ├── register.html           # Registration
│   │   ├── login.html              # Login
│   │   ├── dashboard.html          # Main dashboard
│   │   ├── capture.html            # Webcam capture
│   │   ├── upload.html             # Image upload
│   │   ├── history.html            # Nutrition history
│   │   ├── profile.html            # User profile
│   │   ├── 404.html                # 404 error page
│   │   └── 500.html                # 500 error page
│   │
│   └── static/
│       ├── css/
│       │   └── style.css           # Custom styling
│       ├── js/
│       │   ├── main.js             # Main JavaScript
│       │   └── camera.js           # Camera utilities
│       └── images/
│
├── database/
│   ├── schema.sql                  # Database schema
│   ├── db_init.py                  # Database initialization script
│   └── nutrition_data.json         # Reference nutrition data
│
├── instance/
│   └── nutrition.db               # SQLite database (auto-created)
│
└── documentation/
    ├── PROJECT_REPORT.md          # Complete project report
    ├── DATABASE_DESIGN.md         # Database design & ER diagram
    ├── SYSTEM_ARCHITECTURE.md     # Architecture documentation
    ├── VIVA_QA.md                 # Viva questions & answers
    └── API_DOCUMENTATION.md       # API endpoints
```

---

## Installation & Setup

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)
- Git
- Modern web browser with webcam support

### Step 1: Clone/Download Project

```bash
cd "c:\Users\Admin\OneDrive\Desktop\Ai nutrition"
```

### Step 2: Create Virtual Environment (Recommended)

```bash
python -m venv venv
```

**Activate Virtual Environment:**

- **Windows (PowerShell):**
```powershell
.\venv\Scripts\Activate.ps1
```

- **Windows (Command Prompt):**
```cmd
venv\Scripts\activate.bat
```

- **Linux/Mac:**
```bash
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

This will install:
- Flask and extensions
- SQLAlchemy (ORM)
- YOLOv8 (Object Detection)
- OpenCV (Image Processing)
- Torch & TorchVision (Deep Learning)
- And other dependencies

**Note**: First installation may take 5-10 minutes as it downloads the YOLOv8 model.

### Step 4: Initialize Database

```bash
python database/db_init.py
```

This will:
- Create SQLite database
- Create all tables from schema
- Add sample foods to database
- Create demo user account

**Demo Account Credentials:**
- Username: `demo_user`
- Password: `demo123`

### Step 5: Run Application

```bash
python app.py
```

**Output:**
```
 * Serving Flask app
 * Debug mode: on
 * WARNING in use a production server
 * Running on http://127.0.0.1:5000
```

### Step 6: Access Application

Open your web browser and navigate to:
```
http://localhost:5000
```

---

## Usage Guide

### 1. **Creating an Account**
- Navigate to the registration page
- Enter username (minimum 3 characters)
- Enter valid email address
- Set password (minimum 6 characters)
- Click "Register"

### 2. **Logging In**
- Enter your username and password
- Or use demo account: `demo_user` / `demo123`

### 3. **Capturing Food Image**
- Go to "Capture" page
- Click "Start Camera" to enable webcam
- Click "Capture Image" to take a photo
- Review the image
- Click "Analyze Image"

### 4. **Uploading Food Image**
- Go to "Upload" page
- Select an image file from your computer
- Click "Analyze Image"
- System will detect food items

### 5. **Adding to Daily Nutrition**
- After food detection, select quantity for each food
- Click "Add to Daily Nutrition"
- Food entry will be saved to your history

### 6. **Viewing Dashboard**
- Dashboard shows today's nutrition summary
- View charts for calories, protein, fat, carbs
- See meals logged today
- Track weekly averages

### 7. **Checking History**
- Go to "History" page
- View past 7, 14, or 30 days
- See daily summaries
- Track nutrition trends

### 8. **Managing Profile**
- Go to "Profile" page
- Update full name, age, gender
- View account details
- Logout when done

---

## Database Schema

### Users Table
```sql
CREATE TABLE users (
    user_id INTEGER PRIMARY KEY,
    username TEXT UNIQUE NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    full_name TEXT,
    age INTEGER,
    gender TEXT,
    created_at TIMESTAMP
);
```

### Food Database Table
```sql
CREATE TABLE food_database (
    food_id INTEGER PRIMARY KEY,
    food_name TEXT NOT NULL,
    calories REAL,
    protein REAL,
    fat REAL,
    carbohydrates REAL,
    serving_size TEXT,
    category TEXT
);
```

### Nutrition History Table
```sql
CREATE TABLE nutrition_history (
    history_id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL,
    date DATE,
    food_name TEXT NOT NULL,
    quantity REAL,
    calories REAL,
    protein REAL,
    fat REAL,
    carbohydrates REAL,
    meal_type TEXT,
    image_path TEXT,
    detected_confidence REAL,
    timestamp TIMESTAMP
);
```

### Daily Nutrition Table
```sql
CREATE TABLE daily_nutrition (
    stats_id INTEGER PRIMARY KEY,
    user_id INTEGER,
    date DATE,
    total_calories REAL,
    total_protein REAL,
    total_fat REAL,
    total_carbohydrates REAL,
    meal_count INTEGER
);
```

---

## API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login user
- `POST /api/auth/logout` - Logout user
- `GET /api/auth/me` - Get current user
- `PUT /api/auth/profile` - Update user profile

### Food Recognition
- `POST /api/food/recognize` - Recognize food from image
- `GET /api/food/search` - Search food database
- `GET /api/food/nutrition` - Get food nutrition info

### Nutrition Tracking
- `POST /api/nutrition/add` - Add food entry
- `GET /api/nutrition/daily` - Get daily summary
- `GET /api/nutrition/history` - Get nutrition history
- `GET /api/nutrition/weekly` - Get weekly stats
- `DELETE /api/nutrition/delete/<id>` - Delete entry

---

## AI Model Details

### YOLOv8
- **Model Type**: Object Detection (Nano version)
- **Framework**: Ultralytics
- **Input Size**: 640x640 pixels
- **Confidence Threshold**: 0.5 (adjustable)
- **Pre-trained on**: COCO Dataset
- **Detects**: Various food items (apple, pizza, bread, etc.)

### Food Detection Process
1. Receive image from user
2. Preprocess image (resize, normalize)
3. Run YOLOv8 inference
4. Filter detections for food items
5. Return detected foods with confidence scores
6. Map food names to nutrition database
7. Calculate total nutrition for meal

---

## Sample Test Data

The application comes with sample data:
- **Vegetables**: Apple, Banana, Orange, Broccoli, Carrot
- **Proteins**: Milk, Egg, Chicken
- **Grains**: Rice, Bread, Pasta
- **Fast Food**: Pizza, Sandwich
- **Sweets**: Cake, Cookie, Donut

---

## Troubleshooting

### "Camera not working"
- Check browser permissions
- Allow camera access in browser settings
- Try using HTTPS (required for some browsers)

### "Port 5000 already in use"
```bash
python app.py --port 5001
```

### "Database locked"
- Close other instances of the application
- Delete `instance/nutrition.db` and reinitialize

### "YOLOv8 model download fails"
```bash
pip install --upgrade ultralytics
```

### "ImportError" for packages
```bash
pip install -r requirements.txt --upgrade
```

---

## Performance Optimization

- Database indexing on frequently queried columns
- Image resizing to 640x640 before AI processing
- Caching of food database queries
- Lazy loading of nutritional data

---

## Security Features

✅ Password hashing (Werkzeug)
✅ Session management with timeouts
✅ CSRF protection ready
✅ Input validation on all forms
✅ SQL injection prevention (SQLAlchemy ORM)
✅ File upload validation

---

## Limitations & Future Improvements

### Current Limitations
- Food quantities estimated at 100g servings
- Limited food database (expandable)
- Single user per session
- No mobile app (web-based only)

### Future Enhancements
- Barcode scanning integration
- Multiple food detection in single image
- Machine learning model training on custom foods
- Export nutrition data to PDF/Excel
- Mobile app (React Native)
- Integration with fitness apps
- AI-powered meal recommendations
- Multi-language support

---

## Testing

### Manual Testing Checklist
- [ ] User registration with valid data
- [ ] User registration with invalid data (error handling)
- [ ] Login with correct credentials
- [ ] Login with wrong credentials
- [ ] Webcam capture functionality
- [ ] Image upload functionality
- [ ] Food detection accuracy
- [ ] Daily nutrition summary calculation
- [ ] History filtering and display
- [ ] Profile update functionality
- [ ] Logout functionality

### Test Images
Test with images of:
- Single food item
- Multiple food items
- Non-food objects
- Unclear/blurry images

---

## Support & Contact

For issues or queries:
- Check the troubleshooting section above
- Review the code documentation
- Check Viva Q&A document for common questions

---

## Project Submission Checklist

✅ Complete working application
✅ All code files with comments
✅ Database schema with sample data
✅ System architecture documentation
✅ API documentation
✅ README with installation steps
✅ Project report (6 chapters)
✅ ER diagram with explanation
✅ Viva questions and answers
✅ Sample test data included

---

## License & Academic Use

This project is submitted for academic evaluation as part of the TYBSc Computer Science curriculum at Tilak College of Science and Commerce, Mumbai University.

---

**Last Updated**: January 7, 2026
**Status**: FINAL - READY FOR SUBMISSION

For evaluation and feedback, please refer to the comprehensive documentation provided in the `documentation/` folder.
