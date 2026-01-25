"""
Migration script to add role and assigned_to fields to user table
Run this once to update the database schema.
"""

from app import app, db
from sqlalchemy import text

def migrate_user_role():
    """Add role and assigned_to columns to user table"""
    with app.app_context():
        try:
            print("Starting migration...")
            
            # Get table info to check existing columns
            result = db.session.execute(text("PRAGMA table_info(user)"))
            existing_columns = [row[1] for row in result.fetchall()]
            
            print(f"Existing columns: {existing_columns}")
            
            # Add role column if it doesn't exist
            if 'role' not in existing_columns:
                print("Adding role column...")
                db.session.execute(text("""
                    ALTER TABLE user 
                    ADD COLUMN role VARCHAR(20) DEFAULT 'member'
                """))
                print("[OK] Added role column")
            else:
                print("[OK] role column already exists")
            
            # Add assigned_to column if it doesn't exist
            if 'assigned_to' not in existing_columns:
                print("Adding assigned_to column...")
                db.session.execute(text("""
                    ALTER TABLE user 
                    ADD COLUMN assigned_to INTEGER
                """))
                print("[OK] Added assigned_to column")
            else:
                print("[OK] assigned_to column already exists")
            
            # Commit all changes
            db.session.commit()
            print("\n[SUCCESS] Migration completed successfully!")
            print("User role and assignment fields have been added to the database.")
            
        except Exception as e:
            db.session.rollback()
            print(f"\n[ERROR] Migration error: {e}")
            import traceback
            traceback.print_exc()
            raise

if __name__ == '__main__':
    print("=" * 70)
    print("User Role Migration Script")
    print("=" * 70)
    print("\nThis script will add the following fields to user table:")
    print("  - role (VARCHAR, default: 'member')")
    print("  - assigned_to (INTEGER, nullable)")
    print("\n" + "=" * 70 + "\n")
    
    migrate_user_role()




