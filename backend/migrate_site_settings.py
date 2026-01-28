"""
Migration script to create the site_settings table (website contact & social info).
Run this once if you get "no such table: site_settings".

Usage (from backend folder):
  python migrate_site_settings.py
"""

from app import app, db
from models import SiteSettings


def migrate():
    with app.app_context():
        try:
            print("Creating site_settings table if not exists...")
            db.create_all()
            print("[OK] site_settings table is ready.")
        except Exception as e:
            print(f"[ERROR] {e}")
            import traceback
            traceback.print_exc()
            raise


if __name__ == "__main__":
    migrate()
