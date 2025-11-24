@echo off
echo ============================================================
echo   Document Manager - Python Dependencies Setup
echo ============================================================
echo.
echo This script will install the required Python packages
echo for Document Manager to run properly.
echo.
echo Requirements:
echo   - Python 3.8 or higher must be installed
echo   - Internet connection for downloading packages
echo.
echo ============================================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo.
    echo Please install Python from https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation
    echo.
    pause
    exit /b 1
)

echo [OK] Python found:
python --version
echo.

REM Get the directory where this batch file is located
cd /d "%~dp0"
echo Installing packages from: %CD%
echo.

REM Check if requirements.txt exists
if not exist "requirements.txt" (
    echo ERROR: requirements.txt not found in current directory
    echo Please make sure you're running this from the Document Manager folder
    echo.
    pause
    exit /b 1
)

echo Installing Python dependencies...
echo This may take a few minutes...
echo.

REM Install requirements
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

if errorlevel 1 (
    echo.
    echo ERROR: Failed to install dependencies
    echo.
    echo Common solutions:
    echo   1. Check your internet connection
    echo   2. Try running as Administrator
    echo   3. Update pip: python -m pip install --upgrade pip
    echo.
    pause
    exit /b 1
)

echo.
echo ============================================================
echo SUCCESS! All dependencies installed successfully
echo ============================================================
echo.
echo You can now run Document Manager using:
echo   - START_APP.bat (double-click from File Explorer)
echo   - Or create a desktop shortcut to START_APP.bat
echo.
echo ============================================================
pause
