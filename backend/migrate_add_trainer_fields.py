"""
Migration script to add trainer professional details fields to user_profiles table:
- certifications
- qualifications
- years_of_experience
- specialization
- education
- bio

Run this once to update the database schema.
"""

from app import app, db
from sqlalchemy import text

def migrate_trainer_fields():
    """Add trainer professional detail columns to user_profiles table"""
    with app.app_context():
        try:
            print("Starting migration...")
            
            # Get table info to check existing columns
            result = db.session.execute(text("PRAGMA table_info(user_profiles)"))
            existing_columns = [row[1] for row in result.fetchall()]
            
            print(f"Existing columns: {existing_columns}")
            
            # Trainer professional detail fields
            trainer_fields = [
                ('certifications', 'TEXT', 'Certifications'),
                ('qualifications', 'TEXT', 'Qualifications'),
                ('years_of_experience', 'INTEGER', 'Years of Experience'),
                ('specialization', 'VARCHAR(200)', 'Specialization'),
                ('education', 'VARCHAR(200)', 'Education'),
                ('bio', 'TEXT', 'Bio')
            ]
            
            for field_name, field_type, field_label in trainer_fields:
                if field_name not in existing_columns:
                    print(f"Adding {field_name} column...")
                    db.session.execute(text(f"""
                        ALTER TABLE user_profiles 
                        ADD COLUMN {field_name} {field_type}
                    """))
                    print(f"[OK] Added {field_name} column")
                else:
                    print(f"[OK] {field_name} column already exists")
            
            # Commit all changes
            db.session.commit()
            print("\n[SUCCESS] Migration completed successfully!")
            print("All trainer professional detail fields have been added to the database.")
            
        except Exception as e:
            db.session.rollback()
            print(f"\n[ERROR] Migration error: {e}")
            import traceback
            traceback.print_exc()
            raise

if __name__ == '__main__':
    print("=" * 70)
    print("Migration: Add Trainer Professional Detail Fields")
    print("=" * 70)
    migrate_trainer_fields()


