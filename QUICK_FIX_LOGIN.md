# Quick Fix for Login Issue

## Solution 1: Register via UI (Easiest)

1. Make sure backend is running:
   ```bash
   cd backend
   python app.py
   ```

2. Make sure frontend is running:
   ```bash
   cd frontend
   npm start
   ```

3. Go to `http://localhost:3000`
4. Click "ثبت نام" (Register)
5. Create account with:
   - Username: `demo`
   - Email: `demo@raha-fitness.com`
   - Password: `demo123`

## Solution 2: Use API Registration

If backend is running, you can use this Python script:

```python
import requests

response = requests.post('http://localhost:5000/api/register', json={
    'username': 'demo',
    'email': 'demo@raha-fitness.com',
    'password': 'demo123',
    'language': 'fa'
})

print(response.json())
```

Or use curl:
```bash
curl -X POST http://localhost:5000/api/register \
  -H "Content-Type: application/json" \
  -d '{"username":"demo","email":"demo@raha-fitness.com","password":"demo123","language":"fa"}'
```

## Solution 3: Check Backend Logs

Check the backend terminal for error messages. Common issues:
- Backend not running
- Database not initialized
- CORS issues
- Port conflicts

## Solution 4: Delete and Recreate Database

If there are database issues:

```bash
cd backend
# Delete database
rm raha_fitness.db  # or del raha_fitness.db on Windows

# Restart backend (it will create new database)
python app.py
```

Then register via UI.



