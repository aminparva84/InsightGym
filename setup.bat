@echo off
echo Setting up Raha Fitness Application...
echo.

REM Backend setup
echo Setting up backend...
cd backend
python -m venv venv
call venv\Scripts\activate
pip install -r requirements.txt

REM Create .env if it doesn't exist (copy from .env.example or use PostgreSQL URL)
if not exist .env (
    echo Creating .env file...
    if exist ..\\.env.example (
        copy ..\\.env.example .env
    ) else (
        echo DATABASE_URL=postgresql://user:password@localhost:5432/raha_fitness
        echo JWT_SECRET_KEY=your-secret-key-change-in-production
    ) > .env
    echo .env file created! Edit .env and set DATABASE_URL to your PostgreSQL connection.
)

cd ..

REM Frontend setup
echo.
echo Setting up frontend...
cd frontend
call npm install
cd ..

echo.
echo Setup complete!
echo.
echo To start the backend:
echo   cd backend
echo   venv\Scripts\activate
echo   python app.py
echo.
echo To start the frontend (in a new terminal):
echo   cd frontend
echo   npm start
echo.
echo Don't forget to seed sample data:
echo   cd backend
echo   python seed_data.py
pause



