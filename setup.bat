@echo off
setlocal
title ObsidianPipe One-Click Setup

echo ====================================================
echo          ObsidianPipe Automated Setup
echo ====================================================

:: Check for Python 3.12 (falls back to default python if py launcher isn't used)
py -3.12 --version >nul 2>&1
if %errorlevel% equ 0 (
    set PYTHON_CMD=py -3.12
) else (
    python --version >nul 2>&1
    if %errorlevel% neq 0 (
        echo [ERROR] Python is not installed or not in PATH! Please install Python 3.12.
        pause
        exit /b 1
    )
    set PYTHON_CMD=python
)

echo [INFO] Using Python command: %PYTHON_CMD%

if not exist "venv_mineru" (
    echo [INFO] Creating virtual environment (venv_mineru)...
    %PYTHON_CMD% -m venv venv_mineru
)

call venv_mineru\Scripts\activate.bat
python install.py

echo.
echo Launching ObsidianPipe GUI...
python src/gui.py
pause