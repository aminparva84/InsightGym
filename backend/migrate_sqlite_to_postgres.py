"""
One-time data migration: SQLite -> PostgreSQL.

Use this script when you have an existing SQLite database (e.g. raha_fitness.db)
and want to move its data to PostgreSQL before switching the app to DATABASE_URL.

Usage:
  1. Set DATABASE_URL to your PostgreSQL connection in .env.
  2. Set SOURCE_SQLITE_URL to the SQLite file (default: sqlite:///instance/raha_fitness.db
     relative to backend, or pass as env var).
  3. From backend: python migrate_sqlite_to_postgres.py

The script will:
  - Connect to SQLite (read-only) and PostgreSQL
  - Create tables on PostgreSQL via db.create_all() (so schema matches the app)
  - Copy data table-by-table in FK-safe order, preserving IDs

If there is no existing SQLite data, skip this and run init_database.py with
DATABASE_URL set to PostgreSQL instead.
"""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# We need two engines: source (SQLite) and target (PostgreSQL).
# Load env before importing app so DATABASE_URL is for PostgreSQL.
from dotenv import load_dotenv
load_dotenv()

# Source SQLite URL (default: instance/raha_fitness.db under backend)
SOURCE_SQLITE_URL = os.getenv('SOURCE_SQLITE_URL', 'sqlite:///instance/raha_fitness.db')
# Resolve relative path for sqlite so it's under backend
if SOURCE_SQLITE_URL.startswith('sqlite:///') and 'instance' in SOURCE_SQLITE_URL:
    _rel = SOURCE_SQLITE_URL.replace('sqlite:///', '')
    if not os.path.isabs(_rel):
        _base = os.path.dirname(os.path.abspath(__file__))
        _path = os.path.join(_base, _rel)
        SOURCE_SQLITE_URL = 'sqlite:///' + _path

TARGET_DATABASE_URL = os.getenv('DATABASE_URL')
if not TARGET_DATABASE_URL or not TARGET_DATABASE_URL.startswith('postgresql'):
    if TARGET_DATABASE_URL and TARGET_DATABASE_URL.startswith('postgres://'):
        TARGET_DATABASE_URL = TARGET_DATABASE_URL.replace('postgres://', 'postgresql://', 1)
    else:
        print("[ERROR] DATABASE_URL must be set to a PostgreSQL URL (e.g. postgresql://user:password@localhost:5432/raha_fitness)")
        sys.exit(1)

from sqlalchemy import create_engine, text, inspect
from sqlalchemy.engine import Engine

# Table copy order: respect foreign keys (user first, then tables that reference user)
TABLE_ORDER = [
    'user',           # app uses __tablename__ = 'user'; SQLite from app has 'user'
    'user_profiles',
    'user_exercises',
    'chat_history',
    'exercises',
    'exercise_history',
    'nutrition_plans',
    'tips',
    'injuries',
    'training_programs',
    'workout_logs',
    'progress_entries',
    'weekly_goals',
    'workout_reminders',
    'member_weekly_goals',
    'daily_steps',
    'break_requests',
    'configuration',
    'site_settings',
]

# SQLite may have been created from old schema with 'users' (plural)
SOURCE_TABLE_ALIAS = {'users': 'user'}


def get_source_table_name(inspector, desired_name):
    """Return actual table name on source (e.g. 'users' -> 'user' for target)."""
    tables = inspector.get_table_names()
    if desired_name in tables:
        return desired_name
    # Reverse alias: we want target 'user', source might have 'users'
    for src, tgt in SOURCE_TABLE_ALIAS.items():
        if tgt == desired_name and src in tables:
            return src
    return None


def copy_table(src_engine: Engine, tgt_engine: Engine, table_name: str) -> int:
    """Copy one table from source to target. Returns row count."""
    insp_src = inspect(src_engine)
    src_actual = get_source_table_name(insp_src, table_name)
    if not src_actual:
        return 0
    cols = [c['name'] for c in insp_src.get_columns(src_actual)]
    if not cols:
        return 0
    cols_list = ', '.join(f'"{c}"' for c in cols)
    placeholders = ', '.join(':' + c for c in cols)
    # Target table name: use 'user' quoted for PostgreSQL
    tgt_table = f'"{table_name}"' if table_name == 'user' else table_name
    insert_sql = f'INSERT INTO {tgt_table} ({cols_list}) VALUES ({placeholders})'
    # SQLite: quote only if reserved; table name as-is
    select_sql = f'SELECT {cols_list} FROM "{src_actual}"' if src_actual == 'user' else f'SELECT {cols_list} FROM {src_actual}'
    with src_engine.connect() as sconn:
        result = sconn.execute(text(select_sql))
        rows = result.fetchall()
    if not rows:
        return 0
    with tgt_engine.connect() as tconn:
        for row in rows:
            params = dict(zip(cols, row))
            try:
                tconn.execute(text(insert_sql), params)
            except Exception as e:
                if 'unique' in str(e).lower() or 'duplicate' in str(e).lower():
                    pass
                else:
                    raise
        tconn.commit()
    return len(rows)


def main():
    print("=" * 60)
    print("SQLite -> PostgreSQL data migration")
    print("=" * 60)
    print(f"Source: {SOURCE_SQLITE_URL}")
    print(f"Target: {TARGET_DATABASE_URL.split('@')[-1] if '@' in TARGET_DATABASE_URL else 'PostgreSQL'}")
    print()

    src_engine = create_engine(SOURCE_SQLITE_URL)
    # Create tables on target using the Flask app (DATABASE_URL must be PostgreSQL)
    from app import app, db
    with app.app_context():
        db.create_all()
    tgt_engine = db.engine
    print("[OK] Target tables created/verified")

    total = 0
    for table_name in TABLE_ORDER:
        n = copy_table(src_engine, tgt_engine, table_name)
        if n > 0:
            print(f"  {table_name}: {n} rows")
            total += n

    print()
    print(f"[SUCCESS] Migrated {total} rows. Set DATABASE_URL to PostgreSQL and run the app.")
    print("=" * 60)


if __name__ == '__main__':
    main()
