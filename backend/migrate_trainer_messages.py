"""Create trainer_messages table for member-to-trainer messaging."""
import os
import sys

# Add parent directory to path so we can import app
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from sqlalchemy import text


def migrate():
    with app.app_context():
        # Check if table exists (SQLite and PostgreSQL compatible)
        inspector = db.inspect(db.engine)
        if 'trainer_messages' in inspector.get_table_names():
            print("[OK] Table trainer_messages already exists")
            return
        print("Creating table trainer_messages...")
        db.create_all()
        print("[OK] Table trainer_messages created")


if __name__ == '__main__':
    migrate()
