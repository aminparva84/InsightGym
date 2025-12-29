-- SQL Schema for Raha Fitness Platform
-- Supports Persian (Farsi) and English text with UTF-8 encoding
-- Compatible with SQLite, PostgreSQL, and MySQL

-- Users Table
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username VARCHAR(80) UNIQUE NOT NULL,
    email VARCHAR(120) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    language VARCHAR(10) DEFAULT 'fa',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- User Profiles Table
CREATE TABLE IF NOT EXISTS user_profiles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER UNIQUE NOT NULL,
    age INTEGER,
    weight REAL,  -- in kg
    height REAL,  -- in cm
    gender VARCHAR(20),  -- 'male', 'female', 'other'
    training_level VARCHAR(20),  -- 'beginner', 'intermediate', 'advanced'
    fitness_goals TEXT,  -- JSON array
    injuries TEXT,  -- JSON array
    injury_details TEXT,
    equipment_access TEXT,  -- JSON array
    gym_access BOOLEAN DEFAULT 0,
    home_equipment TEXT,  -- JSON array
    preferred_workout_time VARCHAR(20),  -- 'morning', 'afternoon', 'evening'
    workout_days_per_week INTEGER,  -- 1-7
    preferred_intensity VARCHAR(20),  -- 'light', 'medium', 'heavy'
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Exercise Library Table
CREATE TABLE IF NOT EXISTS exercises (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    category VARCHAR(50) NOT NULL,  -- 'bodybuilding_machine', 'functional_home', 'hybrid_hiit_machine'
    name_fa VARCHAR(200) NOT NULL,  -- نام فارسی
    name_en VARCHAR(200) NOT NULL,  -- English name
    target_muscle_fa VARCHAR(200) NOT NULL,  -- عضله درگیر (Persian)
    target_muscle_en VARCHAR(200) NOT NULL,  -- Target Muscle (English)
    level VARCHAR(20) NOT NULL,  -- 'beginner', 'intermediate', 'advanced'
    intensity VARCHAR(20) NOT NULL,  -- 'light', 'medium', 'heavy'
    execution_tips_fa TEXT,  -- نکات اجرا (Persian)
    execution_tips_en TEXT,  -- Execution Tips (English)
    breathing_guide_fa TEXT,  -- دم و بازدم (Persian)
    breathing_guide_en TEXT,  -- Breathing Guide (English)
    gender_suitability VARCHAR(20) NOT NULL,  -- 'male', 'female', 'both'
    injury_contraindications TEXT,  -- JSON array
    equipment_needed_fa VARCHAR(200),  -- تجهیزات مورد نیاز (Persian)
    equipment_needed_en VARCHAR(200),  -- Equipment Needed (English)
    video_url VARCHAR(500),
    image_url VARCHAR(500),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Exercise History Table
CREATE TABLE IF NOT EXISTS exercise_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    exercise_id INTEGER,  -- Can be NULL for custom exercises
    exercise_name_fa VARCHAR(200),
    exercise_name_en VARCHAR(200),
    category VARCHAR(50),
    sets INTEGER,
    reps INTEGER,
    weight REAL,  -- in kg
    duration INTEGER,  -- in minutes
    distance REAL,  -- in km
    calories_burned INTEGER,
    notes_fa TEXT,
    notes_en TEXT,
    workout_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (exercise_id) REFERENCES exercises(id) ON DELETE SET NULL
);

-- Index for efficient querying
CREATE INDEX IF NOT EXISTS idx_user_workout_date ON exercise_history(user_id, workout_date);

-- Chat History Table
CREATE TABLE IF NOT EXISTS chat_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    message TEXT NOT NULL,
    response TEXT NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Nutrition Plans Table
CREATE TABLE IF NOT EXISTS nutrition_plans (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    plan_type VARCHAR(20) NOT NULL,  -- '2week' or '4week'
    day INTEGER NOT NULL,
    meal_type VARCHAR(50),  -- 'breakfast', 'lunch', 'dinner', 'snack'
    food_item VARCHAR(200) NOT NULL,
    calories INTEGER,
    protein REAL,
    carbs REAL,
    fats REAL,
    notes TEXT,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Tips Table
CREATE TABLE IF NOT EXISTS tips (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title_fa VARCHAR(200) NOT NULL,
    title_en VARCHAR(200) NOT NULL,
    content_fa TEXT NOT NULL,
    content_en TEXT NOT NULL,
    category VARCHAR(100),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Injuries Table
CREATE TABLE IF NOT EXISTS injuries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title_fa VARCHAR(200) NOT NULL,
    title_en VARCHAR(200) NOT NULL,
    description_fa TEXT NOT NULL,
    description_en TEXT NOT NULL,
    prevention_fa TEXT,
    prevention_en TEXT,
    treatment_fa TEXT,
    treatment_en TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Example: Insert a sample exercise
-- INSERT INTO exercises (
--     category, name_fa, name_en, target_muscle_fa, target_muscle_en,
--     level, intensity, execution_tips_fa, execution_tips_en,
--     breathing_guide_fa, breathing_guide_en, gender_suitability,
--     injury_contraindications, equipment_needed_fa, equipment_needed_en
-- ) VALUES (
--     'bodybuilding_machine',
--     'پرس سینه با دستگاه',
--     'Chest Press Machine',
--     'سینه، شانه، سه‌سر بازو',
--     'Chest, Shoulders, Triceps',
--     'intermediate',
--     'medium',
--     'کمر را صاف نگه دارید و به آرامی وزنه را پایین بیاورید.',
--     'Keep your back straight and slowly lower the weight.',
--     'دم هنگام پایین آوردن، بازدم هنگام بالا بردن',
--     'Inhale when lowering, exhale when pushing up',
--     'both',
--     '["shoulder", "lower_back"]',
--     'دستگاه پرس سینه',
--     'Chest Press Machine'
-- );



