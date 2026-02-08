# Database migration

## SQLite to PostgreSQL (one-time data migration)

If you have an existing SQLite database (e.g. `raha_fitness.db`) and want to move to PostgreSQL while keeping your data:

1. **Create the PostgreSQL database** (e.g. `createdb raha_fitness`).

2. **Set environment variables** (e.g. in `.env` in project root or `backend/`):
   - `DATABASE_URL=postgresql://user:password@localhost:5432/raha_fitness` (target)
   - Optionally `SOURCE_SQLITE_URL=sqlite:///instance/raha_fitness.db` (default: SQLite file under `backend/instance/`)

3. **Run the migration script** from the backend directory:
   ```bash
   cd backend
   python migrate_sqlite_to_postgres.py
   ```

4. **Use PostgreSQL from then on**: keep `DATABASE_URL` set to PostgreSQL. The app and all utility scripts (e.g. `check_users.py`, `list_users.py`) use `DATABASE_URL` and will work with PostgreSQL.

If you have no existing SQLite data, skip this and set `DATABASE_URL` to PostgreSQL, then run `python init_database.py` to create tables and an optional demo user.

## Schema creation (PostgreSQL)

- **Recommended:** Use the Flask app: set `DATABASE_URL` and run `python init_database.py` (or start the app so `db.create_all()` runs). This keeps the schema in sync with SQLAlchemy models.
- **Optional manual/backup:** Use `database_schema_postgresql.sql` for a standalone PostgreSQL DDL (e.g. `psql -d raha_fitness -f database_schema_postgresql.sql`).
