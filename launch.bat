@echo off
title InsightGym Launcher
color 0A
echo ========================================
echo   InsightGym Application Launcher
echo ========================================
echo.

REM Change to the script's directory
cd /d "%~dp0"

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH
    echo Please install Python 3.8 or higher
    pause
    exit /b 1
)

REM Check if Node.js is installed
node --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Node.js is not installed or not in PATH
    echo Please install Node.js 14 or higher
    pause
    exit /b 1
)

REM Check if backend virtual environment exists
if not exist "backend\venv" (
    echo [ERROR] Backend virtual environment not found.
    echo Please run setup.bat first or create it manually:
    echo   cd backend
    echo   python -m venv venv
    echo   venv\Scripts\activate
    echo   pip install -r requirements.txt
    echo.
    pause
    exit /b 1
)

REM Check if frontend node_modules exists
if not exist "frontend\node_modules" (
    echo [ERROR] Frontend dependencies not found.
    echo Please run setup.bat first or install manually:
    echo   cd frontend
    echo   npm install
    echo.
    pause
    exit /b 1
)

echo [INFO] All prerequisites found!
echo.

REM Check if backend is already running
netstat -ano | findstr ":5000" >nul 2>&1
if not errorlevel 1 (
    echo [WARNING] Backend server may already be running on port 5000
    echo.
)

REM Check if frontend is already running
netstat -ano | findstr ":3000" >nul 2>&1
if not errorlevel 1 (
    echo [WARNING] Frontend server may already be running on port 3000
    echo.
)

echo [1/2] Starting backend server...
start "InsightGym Backend" cmd /k "cd /d %~dp0backend && call venv\Scripts\activate && echo Backend Server Starting... && python app.py"

REM Wait a moment for backend to initialize
echo [INFO] Waiting for backend to initialize...
timeout /t 4 /nobreak >nul

echo [2/2] Starting frontend server...
start "InsightGym Frontend" cmd /k "cd /d %~dp0frontend && echo Frontend Server Starting... && npm start"

echo.
echo ========================================
echo   Servers are starting in new windows
echo ========================================
echo.
echo Backend API:  http://localhost:5000
echo Frontend UI:  http://localhost:3000
echo.
echo The application will open automatically in your browser.
echo You can close this window - servers will continue running.
echo.
echo To stop servers, close the Backend and Frontend windows.
echo.
pause
