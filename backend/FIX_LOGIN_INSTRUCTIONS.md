# Fix Login Issues - Instructions

## Problem
You cannot login with old/existing users.

## Solution

### Option 1: Reset Password for Existing Users

To reset the password for any existing user, use the reset script:

```bash
cd backend
python reset_user_password.py <username> [new_password]
```

**Examples:**
```bash
# Reset password for "ramin test" user to "demo123"
python reset_user_password.py "ramin test" demo123

# Reset password for "رامین تکمیل" user to "password123"
python reset_user_password.py "رامین تکمیل" password123

# Reset password for demo user (default password: demo123)
python reset_user_password.py demo
```

### Option 2: Use Demo User

A demo user has been created with these credentials:
- **Username:** `demo`
- **Password:** `demo123`
- **Email:** `demo@raha-fitness.com`

### Option 3: Create New User

Register a new user through the web interface at `http://localhost:3000`

## Current Users in Database

1. **Username:** رامین تکمیل
   - Email: ramintakmil@gmail.com
   - Language: fa

2. **Username:** ramin test
   - Email: test@gmail.com
   - Language: fa

3. **Username:** demo
   - Email: demo@raha-fitness.com
   - Password: demo123
   - Language: fa

## Useful Scripts

- `list_users.py` - List all users in the database
- `fix_login.py` - Create/reset demo user
- `reset_user_password.py <username> [password]` - Reset password for any user

## Troubleshooting

If you still can't login:

1. Make sure the backend server is running on port 5000
2. Check browser console for errors
3. Verify the database exists: `backend/instance/raha_fitness.db`
4. Try resetting the password using the script above
5. Clear browser localStorage and try again



