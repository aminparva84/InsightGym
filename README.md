# AlphaFit - Fitness Application

A comprehensive fitness application with Flask backend and React frontend, featuring AI assistant, multi-language support (Farsi/English), and comprehensive fitness tracking.

## Features

- 🏋️ **Exercise Tracking**: Record and view exercise history
- 🥗 **Nutrition Plans**: 2-week and 4-week meal plans
- 🤖 **AI Assistant**: Chat with AI agent for fitness guidance
- 📊 **History Tracking**: View exercise and chat history
- 💡 **Tips & Suggestions**: Get fitness tips and recommendations
- 🏥 **Injury Information**: Access injury prevention and treatment info
- 🌐 **Multi-language**: Support for Farsi (default) and English
- 🌙 **Dark Theme**: Modern dark theme UI

## Tech Stack

### Backend
- Flask
- SQLAlchemy
- Flask-JWT-Extended
- Flask-CORS

### Frontend
- React
- React Router
- React i18next
- Axios

## Setup Instructions

### Backend Setup

1. Navigate to the backend directory:
```bash
cd backend
```

2. Create a virtual environment:
```bash
python -m venv venv
```

3. Activate the virtual environment:
- Windows:
```bash
venv\Scripts\activate
```
- Linux/Mac:
```bash
source venv/bin/activate
```

4. Install dependencies:
```bash
pip install -r requirements.txt
```

5. Create a `.env` file in the backend directory:
```
DATABASE_URL=sqlite:///raha_fitness.db
JWT_SECRET_KEY=your-secret-key-change-in-production
```

6. Run the Flask server:
```bash
python app.py
```

The backend will run on `http://localhost:5000`

### Frontend Setup

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Start the development server:
```bash
npm start
```

The frontend will run on `http://localhost:3000`

## Project Structure

```
InsightGym/
├── backend/
│   ├── app.py                 # Flask application
│   ├── requirements.txt       # Python dependencies
│   └── .env                   # Environment variables
├── frontend/
│   ├── public/
│   ├── src/
│   │   ├── components/        # React components
│   │   ├── context/           # React context (Auth)
│   │   ├── i18n/              # i18n configuration
│   │   └── App.js
│   └── package.json
└── README.md
```

## API Endpoints

### Authentication
- `POST /api/register` - Register new user
- `POST /api/login` - Login user
- `GET /api/user` - Get current user (requires auth)

### Exercises
- `GET /api/exercises` - Get user exercises
- `POST /api/exercises` - Add new exercise

### Chat
- `POST /api/chat` - Send message to AI assistant
- `GET /api/chat/history` - Get chat history

### Nutrition
- `GET /api/nutrition/plans?type=2week|4week` - Get nutrition plans
- `POST /api/nutrition/plans` - Add nutrition plan

### Tips & Injuries
- `GET /api/tips?language=fa|en` - Get fitness tips
- `GET /api/injuries?language=fa|en` - Get injury information

## Default Language

The application defaults to Farsi (Persian) but supports English. Users can switch languages using the language toggle in the navigation bar.

## Database

The application uses SQLite by default. The database file (`raha_fitness.db`) will be created automatically when you first run the backend.

## AI Assistant

The AI assistant can help users with:
- Creating personalized fitness plans
- Nutrition suggestions
- Exercise recommendations
- General fitness guidance

The assistant is aware of the user's exercise history and nutrition plans to provide contextual help.

## License

This project is for educational purposes.

