@echo off
REM ==============================================================================
REM AegisGov AI: 1-Click Windows Local Runner
REM Automatically verifies virtualenv and starts the full-stack server
REM ==============================================================================

setlocal enabledelayedexpansion

echo ======================================================
echo  🚀 Starting AegisGov AI Sovereign Governance Platform
echo ======================================================
echo.

cd /d "%~dp0\.."

REM 1. Check Python installation
where python >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Python is not installed or not in PATH!
    echo Please install Python 3.9+ from https://www.python.org/downloads/
    pause
    exit /b 1
)

REM 2. Create virtual environment if it does not exist
if not exist "backend\venv\Scripts\activate.bat" (
    echo [INFO] Creating Python virtual environment in backend\venv...
    python -m venv backend\venv
    if %ERRORLEVEL% NEQ 0 (
        echo [ERROR] Failed to create virtual environment.
        pause
        exit /b 1
    )
    echo [INFO] Installing required dependencies...
    call backend\venv\Scripts\activate.bat
    python -m pip install --upgrade pip
    python -m pip install -r backend\requirements.txt
    if %ERRORLEVEL% NEQ 0 (
        echo [ERROR] Failed to install dependencies.
        pause
        exit /b 1
    )
) else (
    call backend\venv\Scripts\activate.bat
)

REM 3. Ensure .env exists
if not exist ".env" (
    if exist ".env.example" (
        echo [INFO] Initializing .env from .env.example...
        copy .env.example .env >nul
    )
)

echo.
echo ======================================================
echo  ✅ Environment ready! Starting local server...
echo  🌐 Access UI at: http://localhost:8080
echo  🏥 Health check: http://localhost:8080/api/health
echo  (Press Ctrl+C to stop)
echo ======================================================
echo.

python -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8080 --reload
pause
