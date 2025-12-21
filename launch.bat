@echo off
echo Starting InsightGym Application...
echo.

REM Check if backend virtual environment exists
if not exist "backend\venv" (
    echo Backend virtual environment not found. Please run setup.bat first.
    pause
    exit /b 1
)

REM Check if frontend node_modules exists
if not exist "frontend\node_modules" (
    echo Frontend dependencies not found. Please run setup.bat first.
    pause
    exit /b 1
)

echo Starting backend server...
start "InsightGym Backend" cmd /k "cd backend && call venv\Scripts\activate && python app.py"

REM Wait a moment for backend to start
timeout /t 3 /nobreak >nul

echo Starting frontend server...
start "InsightGym Frontend" cmd /k "cd frontend && npm start"

echo.
echo Both servers are starting...
echo Backend: http://localhost:5000
echo Frontend: http://localhost:3000
echo.
echo Press any key to close this window (servers will continue running)...
pause >nul

