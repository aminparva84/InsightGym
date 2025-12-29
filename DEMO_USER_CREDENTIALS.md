# Demo User Credentials

## Quick Setup

I've created a script to set up a demo user, but due to model conflicts, here are two options:

### Option 1: Register a New User (Easiest)

1. Start the backend server:
   ```bash
   cd backend
   python app.py
   ```

2. Start the frontend:
   ```bash
   cd frontend
   npm start
   ```

3. Go to the registration page and create an account:
   - Username: `demo` (or any username you prefer)
   - Email: `demo@raha-fitness.com` (or any email)
   - Password: `demo123`

### Option 2: Use Python to Create User Directly

Run this Python code in a Python shell (with the backend running):

```python
from app import app, db, User
from werkzeug.security import generate_password_hash
from datetime import datetime

with app.app_context():
    # Check if exists
    if User.query.filter_by(username='demo').first():
        print("Demo user already exists!")
    else:
        demo_user = User(
            username='demo',
            email='demo@raha-fitness.com',
            password_hash=generate_password_hash('demo123'),
            language='fa',
            created_at=datetime.utcnow()
        )
        db.session.add(demo_user)
        db.session.commit()
        print("Demo user created!")
```

### Option 3: Use Flask Shell

```bash
cd backend
python -c "from app import app, db, User; from werkzeug.security import generate_password_hash; from datetime import datetime; app.app_context().push(); u = User(username='demo', email='demo@raha-fitness.com', password_hash=generate_password_hash('demo123'), language='fa', created_at=datetime.utcnow()); db.session.add(u); db.session.commit(); print('Demo user created!')"
```

## Demo User Credentials

Once created, use these credentials to log in:

- **Username:** `demo`
- **Password:** `demo123`
- **Email:** `demo@raha-fitness.com`
- **Language:** Farsi (Persian)

## What You'll See

After logging in, you'll see the member landing page (Dashboard) with:
- History tab (Exercise and Chat history)
- Nutrition tab (2-week and 4-week meal plans)
- Tips & Suggestions tab
- Injuries tab
- AI Chat panel (click the chat button)

## Note

If you want sample data (exercises, chat history, etc.), you'll need to:
1. Seed the exercise database: `python backend/seed_exercises.py`
2. Seed tips and injuries: `python backend/seed_data.py`
3. Use the app to create additional data through the UI



