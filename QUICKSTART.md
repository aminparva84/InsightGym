# Quick Start Guide - Raha Fitness

## Prerequisites

- Python 3.8 or higher
- Node.js 14 or higher
- npm or yarn

## Step-by-Step Setup

### 1. Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file (copy from project root .env.example if available)
# Or create manually with:
# DATABASE_URL=postgresql://user:password@localhost:5432/raha_fitness
# JWT_SECRET_KEY=your-secret-key-here
# Create the PostgreSQL database first: createdb raha_fitness

# Run the Flask server
python app.py
```

The backend should now be running on `http://localhost:5000`

### 2. Seed Sample Data (Optional)

In a new terminal, while the backend is running:

```bash
cd backend
python seed_data.py
```

This will add sample tips and injury information in both Farsi and English.

### 3. Frontend Setup

Open a new terminal:

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start the development server
npm start
```

The frontend should now be running on `http://localhost:3000`

### 4. Access the Application

1. Open your browser and go to `http://localhost:3000`
2. You'll see the landing page with login/register options
3. Create a new account or login
4. Once logged in, you'll see the dashboard with tabs for:
   - History (Exercise and Chat history)
   - Nutrition (2-week and 4-week plans)
   - Tips & Suggestions
   - Injuries

### 5. Test the AI Assistant

1. Click the chat button in the top navigation
2. Try sending messages like:
   - "سلام" (Hello in Farsi)
   - "I want a workout plan"
   - "برنامه تغذیه" (Nutrition plan in Farsi)
   - "What exercises should I do?"

## Language Support

- Default language: Farsi (Persian)
- Switch languages using the language buttons in the navigation bar
- The entire UI and AI responses will switch between Farsi and English

## Troubleshooting

### Backend Issues

- **Port 5000 already in use**: Change the port in `app.py` (last line) or stop the process using port 5000
- **Database errors**: Ensure PostgreSQL is running and `DATABASE_URL` in `.env` is correct. Create the database (e.g. `createdb raha_fitness`). Run `python init_database.py` to create tables and a demo user. If migrating from SQLite, see [MIGRATION.md](MIGRATION.md).
- **Module not found**: Make sure you've activated the virtual environment and installed requirements

### Frontend Issues

- **Port 3000 already in use**: React will automatically suggest using port 3001
- **API connection errors**: Make sure the backend is running on port 5000
- **CORS errors**: Check that Flask-CORS is properly installed and configured

### MCP Server (Optional)

If you want to run the MCP server for advanced AI agent integration:

```bash
# Install MCP server dependencies
npm install --prefix . express axios cors

# Run MCP server
node mcp-server.js
```

The MCP server will run on `http://localhost:3001`

## Next Steps

1. **Add Exercises**: Use the AI chat to add exercises or integrate with the API directly
2. **Create Nutrition Plans**: Add nutrition plans through the API or let the AI assistant help
3. **Customize**: Modify the AI responses in `backend/app.py` or integrate with OpenAI API for more advanced responses
4. **Add Data**: Use the seed script as a template to add more tips and injury information

## API Testing

You can test the API endpoints using tools like Postman or curl:

```bash
# Register a new user
curl -X POST http://localhost:5000/api/register \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","email":"test@example.com","password":"test123","language":"fa"}'

# Login
curl -X POST http://localhost:5000/api/login \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","password":"test123"}'

# Get exercises (replace TOKEN with actual token)
curl -X GET http://localhost:5000/api/exercises \
  -H "Authorization: Bearer TOKEN"
```

## Support

For issues or questions, check the main README.md file for more detailed documentation.



