@echo off
cd /d "%~dp0"
if not exist "venv_mineru\Scripts\activate.bat" (
    echo Virtual environment not found! Running first-time setup...
    call setup.bat
    exit /b
)
call venv_mineru\Scripts\activate.bat
start "" pythonw src/gui.py