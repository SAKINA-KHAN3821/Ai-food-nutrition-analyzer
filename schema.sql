-- AI Nutrition Analyzer Database Schema
-- SQLite Database

-- Users Table
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    full_name TEXT,
    age INTEGER,
    gender TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Food Database Table (Reference Nutrition Data)
CREATE TABLE IF NOT EXISTS food_database (
    food_id INTEGER PRIMARY KEY AUTOINCREMENT,
    food_name TEXT NOT NULL,
    calories REAL DEFAULT 0,
    protein REAL DEFAULT 0,
    fat REAL DEFAULT 0,
    carbohydrates REAL DEFAULT 0,
    serving_size TEXT DEFAULT '100g',
    category TEXT
);

-- Nutrition History Table (Individual Food Entries)
CREATE TABLE IF NOT EXISTS nutrition_history (
    history_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    date DATE DEFAULT CURRENT_DATE,
    food_name TEXT NOT NULL,
    quantity REAL DEFAULT 1.0,
    calories REAL DEFAULT 0,
    protein REAL DEFAULT 0,
    fat REAL DEFAULT 0,
    carbohydrates REAL DEFAULT 0,
    meal_type TEXT DEFAULT 'other',
    image_path TEXT,
    detected_confidence REAL DEFAULT 0,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

-- Daily Nutrition Summary Table
CREATE TABLE IF NOT EXISTS daily_nutrition (
    stats_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    date DATE DEFAULT CURRENT_DATE,
    total_calories REAL DEFAULT 0,
    total_protein REAL DEFAULT 0,
    total_fat REAL DEFAULT 0,
    total_carbohydrates REAL DEFAULT 0,
    meal_count INTEGER DEFAULT 0,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    UNIQUE(user_id, date)
);

-- Create Indexes for Performance
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_nutrition_history_user_id ON nutrition_history(user_id);
CREATE INDEX IF NOT EXISTS idx_nutrition_history_date ON nutrition_history(date);
CREATE INDEX IF NOT EXISTS idx_daily_nutrition_user_id ON daily_nutrition(user_id);
CREATE INDEX IF NOT EXISTS idx_daily_nutrition_date ON daily_nutrition(date);
CREATE INDEX IF NOT EXISTS idx_food_database_name ON food_database(food_name);
