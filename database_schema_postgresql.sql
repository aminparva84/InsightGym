-- PostgreSQL DDL for Raha Fitness / InsightGYM
-- Use for manual setup or backup. Prefer SQLAlchemy db.create_all() or Prisma in normal use.
-- Table "user" is quoted because user is a reserved word in PostgreSQL.

-- User table (app uses __tablename__ = 'user')
CREATE TABLE IF NOT EXISTS "user" (
    id SERIAL PRIMARY KEY,
    username VARCHAR(80) UNIQUE NOT NULL,
    email VARCHAR(120) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    language VARCHAR(10) DEFAULT 'fa',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    role VARCHAR(20) DEFAULT 'member',
    assigned_to INTEGER REFERENCES "user"(id)
);

-- User profiles
CREATE TABLE IF NOT EXISTS user_profiles (
    id SERIAL PRIMARY KEY,
    user_id INTEGER UNIQUE NOT NULL REFERENCES "user"(id) ON DELETE CASCADE,
    age INTEGER,
    weight REAL,
    height REAL,
    gender VARCHAR(20),
    account_type VARCHAR(20),
    chest_circumference REAL,
    waist_circumference REAL,
    abdomen_circumference REAL,
    arm_circumference REAL,
    hip_circumference REAL,
    thigh_circumference REAL,
    training_level VARCHAR(20),
    fitness_goals TEXT,
    injuries TEXT,
    injury_details TEXT,
    medical_conditions TEXT,
    medical_condition_details TEXT,
    exercise_history_years INTEGER,
    exercise_history_description TEXT,
    equipment_access TEXT,
    gym_access BOOLEAN DEFAULT FALSE,
    home_equipment TEXT,
    preferred_workout_time VARCHAR(20),
    workout_days_per_week INTEGER,
    preferred_intensity VARCHAR(20),
    certifications TEXT,
    qualifications TEXT,
    years_of_experience INTEGER,
    specialization VARCHAR(200),
    education VARCHAR(200),
    bio TEXT,
    profile_image VARCHAR(255),
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- User exercises (legacy user_exercises from app.py)
CREATE TABLE IF NOT EXISTS user_exercises (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES "user"(id) ON DELETE CASCADE,
    exercise_name VARCHAR(200) NOT NULL,
    exercise_type VARCHAR(100),
    duration INTEGER,
    calories_burned INTEGER,
    date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    notes TEXT
);

-- Chat history
CREATE TABLE IF NOT EXISTS chat_history (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES "user"(id) ON DELETE CASCADE,
    message TEXT NOT NULL,
    response TEXT NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Exercise library
CREATE TABLE IF NOT EXISTS exercises (
    id SERIAL PRIMARY KEY,
    category VARCHAR(50) NOT NULL,
    name_fa VARCHAR(200) NOT NULL,
    name_en VARCHAR(200) NOT NULL,
    target_muscle_fa VARCHAR(200) NOT NULL,
    target_muscle_en VARCHAR(200) NOT NULL,
    level VARCHAR(20) NOT NULL,
    intensity VARCHAR(20) NOT NULL,
    execution_tips_fa TEXT,
    execution_tips_en TEXT,
    breathing_guide_fa TEXT,
    breathing_guide_en TEXT,
    gender_suitability VARCHAR(20) NOT NULL,
    injury_contraindications TEXT,
    equipment_needed_fa VARCHAR(200),
    equipment_needed_en VARCHAR(200),
    video_url VARCHAR(500),
    image_url VARCHAR(500),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Exercise history
CREATE TABLE IF NOT EXISTS exercise_history (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES "user"(id) ON DELETE CASCADE,
    exercise_id INTEGER REFERENCES exercises(id) ON DELETE SET NULL,
    exercise_name_fa VARCHAR(200),
    exercise_name_en VARCHAR(200),
    category VARCHAR(50),
    sets INTEGER,
    reps INTEGER,
    weight REAL,
    duration INTEGER,
    distance REAL,
    calories_burned INTEGER,
    notes_fa TEXT,
    notes_en TEXT,
    workout_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_user_workout_date ON exercise_history(user_id, workout_date);

-- Nutrition plans
CREATE TABLE IF NOT EXISTS nutrition_plans (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES "user"(id) ON DELETE CASCADE,
    plan_type VARCHAR(20) NOT NULL,
    day INTEGER NOT NULL,
    meal_type VARCHAR(50),
    food_item VARCHAR(200) NOT NULL,
    calories INTEGER,
    protein REAL,
    carbs REAL,
    fats REAL,
    notes TEXT
);

-- Tips
CREATE TABLE IF NOT EXISTS tips (
    id SERIAL PRIMARY KEY,
    title_fa VARCHAR(200) NOT NULL,
    title_en VARCHAR(200) NOT NULL,
    content_fa TEXT NOT NULL,
    content_en TEXT NOT NULL,
    category VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Injuries
CREATE TABLE IF NOT EXISTS injuries (
    id SERIAL PRIMARY KEY,
    title_fa VARCHAR(200) NOT NULL,
    title_en VARCHAR(200) NOT NULL,
    description_fa TEXT NOT NULL,
    description_en TEXT NOT NULL,
    prevention_fa TEXT,
    prevention_en TEXT,
    treatment_fa TEXT,
    treatment_en TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
