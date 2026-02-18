"""
Migration: Move Website KB from file-based (website_kb_source.md, website_kb_index.json)
to database (website_kb_source, website_kb_chunks tables).

Run from backend: python migrate_website_kb_to_db.py

After migration, the KB uses the database and local sentence-transformers (no API key).
"""

import os
import sys

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from models import WebsiteKBSource, WebsiteKBChunk


def migrate():
    with app.app_context():
        db.create_all()  # Ensure tables exist

        # Migrate source from file if DB is empty
        source_row = db.session.query(WebsiteKBSource).first()
        if not source_row or not (source_row.content or '').strip():
            kb_source_path = os.path.join(os.path.dirname(__file__), 'website_kb_source.md')
            if os.path.exists(kb_source_path):
                with open(kb_source_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                if not source_row:
                    source_row = WebsiteKBSource()
                    db.session.add(source_row)
                source_row.content = content
                db.session.commit()
                print(f"[OK] Migrated KB source from {kb_source_path} to database")
            else:
                if not source_row:
                    source_row = WebsiteKBSource(content='')
                    db.session.add(source_row)
                    db.session.commit()
                print("[INFO] No existing website_kb_source.md; KB source table initialized empty")
        else:
            print("[INFO] KB source already in database")

        # Chunks: old JSON index is incompatible (different embedding model/dims).
        # Admin should click Reindex in AI Settings to rebuild with sentence-transformers.
        chunk_count = db.session.query(WebsiteKBChunk).count()
        if chunk_count == 0:
            print("[INFO] No KB chunks in database. Click 'Reindex' in Admin > AI Settings to build index (no API key needed).")
        else:
            print(f"[OK] KB has {chunk_count} chunks in database")


if __name__ == '__main__':
    migrate()
