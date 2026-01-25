"""
Migration script to add new profile fields:
- account_type
- chest_circumference
- waist_circumference
- abdomen_circumference
- arm_circumference
- hip_circumference
- thigh_circumference

Run this once to update the database schema.
"""

from app import app, db
from sqlalchemy import text

def migrate_profile_fields():
    """Add new columns to user_profiles table"""
    with app.app_context():
        try:
            print("Starting migration...")
            
            # Check if columns already exist and add them if they don't
            # SQLite doesn't support IF NOT EXISTS for ALTER TABLE ADD COLUMN,
            # so we need to check first
            
            # Get table info to check existing columns
            result = db.session.execute(text("PRAGMA table_info(user_profiles)"))
            existing_columns = [row[1] for row in result.fetchall()]
            
            print(f"Existing columns: {existing_columns}")
            
            # Add account_type if it doesn't exist
            if 'account_type' not in existing_columns:
                print("Adding account_type column...")
                db.session.execute(text("""
                    ALTER TABLE user_profiles 
                    ADD COLUMN account_type VARCHAR(20)
                """))
                print("[OK] Added account_type column")
            else:
                print("[OK] account_type column already exists")
            
            # Add body measurement columns if they don't exist
            measurement_fields = [
                ('chest_circumference', 'Chest circumference'),
                ('waist_circumference', 'Waist circumference'),
                ('abdomen_circumference', 'Abdomen circumference'),
                ('arm_circumference', 'Arm circumference'),
                ('hip_circumference', 'Hip circumference'),
                ('thigh_circumference', 'Thigh circumference')
            ]
            
            for field_name, field_label in measurement_fields:
                if field_name not in existing_columns:
                    print(f"Adding {field_name} column...")
                    db.session.execute(text(f"""
                        ALTER TABLE user_profiles 
                        ADD COLUMN {field_name} REAL
                    """))
                    print(f"[OK] Added {field_name} column")
                else:
                    print(f"[OK] {field_name} column already exists")
            
            # Commit all changes
            db.session.commit()
            print("\n[SUCCESS] Migration completed successfully!")
            print("All new profile fields have been added to the database.")
            
        except Exception as e:
            db.session.rollback()
            print(f"\n[ERROR] Migration error: {e}")
            import traceback
            traceback.print_exc()
            raise

if __name__ == '__main__':
    print("=" * 70)
    print("Profile Fields Migration Script")
    print("=" * 70)
    print("\nThis script will add the following fields to user_profiles table:")
    print("  - account_type (VARCHAR)")
    print("  - chest_circumference (REAL)")
    print("  - waist_circumference (REAL)")
    print("  - abdomen_circumference (REAL)")
    print("  - arm_circumference (REAL)")
    print("  - hip_circumference (REAL)")
    print("  - thigh_circumference (REAL)")
    print("\n" + "=" * 70 + "\n")
    
    migrate_profile_fields()

