-- SQL script to create demo user
-- Run this in your SQLite database

-- Note: This uses SQLite syntax. For other databases, adjust accordingly.

-- Insert demo user
-- Password hash for 'demo123' using werkzeug's generate_password_hash
-- You may need to generate this using Python first

INSERT OR IGNORE INTO user (username, email, password_hash, language, created_at)
VALUES (
    'demo',
    'demo@raha-fitness.com',
    'pbkdf2:sha256:600000$YourHashHere$...',  -- Replace with actual hash
    'fa',
    datetime('now')
);

-- To generate the password hash, run this Python code:
-- from werkzeug.security import generate_password_hash
-- print(generate_password_hash('demo123'))

