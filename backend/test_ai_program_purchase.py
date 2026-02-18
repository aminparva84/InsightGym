"""
Test AI-designed program generation (simulates purchase flow).
Run from backend dir: python test_ai_program_purchase.py
Requires: DATABASE_URL, and AI API key in Admin settings or env (OPENAI_API_KEY etc).
"""

import os
import sys

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.chdir(os.path.dirname(os.path.abspath(__file__)))

def main():
    from app import app, db
    from models import UserProfile, TrainingProgram, SiteSettings

    with app.app_context():
        # 1. Check AI settings
        row = db.session.query(SiteSettings).first()
        raw = getattr(row, 'ai_settings_json', None) or ''
        print("AI settings (ai_settings_json):", raw[:200] + "..." if len(raw) > 200 else raw or "(empty)")
        if not raw or not raw.strip():
            print("WARNING: No AI settings in database. Configure in Admin -> AI settings.")

        # 2. Test chat_completion with db (same as purchase flow)
        from services.ai_provider import chat_completion, _get_settings, _resolve_provider, get_provider_api_key

        settings = _get_settings(db)
        provider = _resolve_provider(settings)
        api_key, _ = get_provider_api_key(provider or 'openai', settings)

        print(f"\nProvider: {provider}, API key set: {bool(api_key)}")

        if not provider or not api_key:
            print("ERROR: No AI provider available. Set API key in Admin or env (OPENAI_API_KEY, etc).")
            return 1

        # 3. Direct chat_completion with db (bypasses current_app for settings)
        print("\nTesting chat_completion with db...")
        out = chat_completion("You are a test. Reply only: OK", "Say OK.", max_tokens=50, db=db)
        if out:
            print(f"SUCCESS: chat_completion returned: {out[:100]}")
        else:
            print("FAILED: chat_completion returned None")
            return 1

        # 4. Test generate_personalized_program_after_purchase (needs real user/program)
        user = db.session.query(UserProfile).first()
        template = db.session.query(TrainingProgram).filter(TrainingProgram.user_id.is_(None)).first()
        if not user or not template:
            print("\nSkipping full program test (no user profile or template). Chat test passed.")
            return 0

        user_id = user.user_id
        program_id = template.id
        print(f"\nTesting generate_personalized_program_after_purchase(user_id={user_id}, program_id={program_id})...")
        from services.session_ai_service import generate_personalized_program_after_purchase

        sessions, err = generate_personalized_program_after_purchase(user_id, program_id, 'fa', db)
        if sessions:
            print(f"SUCCESS: Generated {len(sessions)} sessions")
            return 0
        print(f"FAILED: {err}")
        return 1

if __name__ == "__main__":
    sys.exit(main() or 0)
