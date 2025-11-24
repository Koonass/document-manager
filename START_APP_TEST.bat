@echo off
REM ================================================================================
REM Document Manager V2.3 - Testing/Development Launcher
REM ================================================================================
REM
REM ⚠️ WARNING: THIS IS THE TESTING VERSION ⚠️
REM
REM This launcher is for testing new features and bug fixes.
REM Use START_APP.bat for the stable production version.
REM
REM Changes made in this version will not affect production users until
REM the code is copied to the production folder.
REM ================================================================================

echo.
echo ================================================================================
echo Document Manager V2.3 - ⚠️ TESTING VERSION ⚠️
echo ================================================================================
echo.
echo WARNING: You are running the TESTING version!
echo          This version may contain untested features or bugs.
echo.
echo For stable production version, use START_APP.bat instead.
echo.
echo ================================================================================
echo.

REM Set working directory to this script's location
cd /d "%~dp0"

REM Display current location for troubleshooting
echo Running from: %CD%
echo.

REM ================================================================================
REM Find Python Installation
REM ================================================================================

set PYTHON_CMD=

REM Method 1: Check if python is in PATH
python --version >nul 2>&1
if %errorlevel% == 0 (
    set PYTHON_CMD=python
    goto :found_python
)

REM Method 2: Try py launcher (Windows Python Launcher)
py --version >nul 2>&1
if %errorlevel% == 0 (
    set PYTHON_CMD=py
    goto :found_python
)

REM Method 3: Try python3
python3 --version >nul 2>&1
if %errorlevel% == 0 (
    set PYTHON_CMD=python3
    goto :found_python
)

REM Method 4: Check common Python installation paths
if exist "C:\Python312\python.exe" (
    set PYTHON_CMD="C:\Python312\python.exe"
    goto :found_python
)

if exist "C:\Python311\python.exe" (
    set PYTHON_CMD="C:\Python311\python.exe"
    goto :found_python
)

if exist "C:\Python310\python.exe" (
    set PYTHON_CMD="C:\Python310\python.exe"
    goto :found_python
)

if exist "C:\Python39\python.exe" (
    set PYTHON_CMD="C:\Python39\python.exe"
    goto :found_python
)

REM Method 5: Check AppData local installations
if exist "%LOCALAPPDATA%\Programs\Python\Python312\python.exe" (
    set PYTHON_CMD="%LOCALAPPDATA%\Programs\Python\Python312\python.exe"
    goto :found_python
)

if exist "%LOCALAPPDATA%\Programs\Python\Python311\python.exe" (
    set PYTHON_CMD="%LOCALAPPDATA%\Programs\Python\Python311\python.exe"
    goto :found_python
)

if exist "%LOCALAPPDATA%\Programs\Python\Python310\python.exe" (
    set PYTHON_CMD="%LOCALAPPDATA%\Programs\Python\Python310\python.exe"
    goto :found_python
)

if exist "%LOCALAPPDATA%\Programs\Python\Python39\python.exe" (
    set PYTHON_CMD="%LOCALAPPDATA%\Programs\Python\Python39\python.exe"
    goto :found_python
)

REM Method 6: Check Program Files
if exist "C:\Program Files\Python312\python.exe" (
    set PYTHON_CMD="C:\Program Files\Python312\python.exe"
    goto :found_python
)

if exist "C:\Program Files\Python311\python.exe" (
    set PYTHON_CMD="C:\Program Files\Python311\python.exe"
    goto :found_python
)

if exist "C:\Program Files\Python310\python.exe" (
    set PYTHON_CMD="C:\Program Files\Python310\python.exe"
    goto :found_python
)

REM Python not found
echo ===============================================================================
echo ERROR: Python not found!
echo ===============================================================================
echo.
echo This application requires Python to run.
echo.
echo Please install Python from: https://www.python.org/downloads/
echo   - Make sure to check "Add Python to PATH" during installation
echo.
echo If Python is already installed:
echo   1. Open Command Prompt
echo   2. Type: where python
echo   3. Edit this START_APP_TEST.bat file
echo   4. Add the path to the Python search section
echo.
echo ===============================================================================
pause
exit /b 1

:found_python
echo Found Python: %PYTHON_CMD%
echo.

REM ================================================================================
REM Verify Python Version
REM ================================================================================

echo Checking Python version...
%PYTHON_CMD% --version
echo.

REM ================================================================================
REM Check Dependencies
REM ================================================================================

echo Checking required dependencies...
echo.

REM Check if requirements.txt exists
if not exist "requirements.txt" (
    echo WARNING: requirements.txt not found
    echo Application may fail if dependencies are missing.
    echo.
) else (
    echo Dependencies file found: requirements.txt
    echo If this is first run, you may need to install dependencies:
    echo   %PYTHON_CMD% -m pip install -r requirements.txt
    echo.
)

REM ================================================================================
REM Launch Application (Testing Mode)
REM ================================================================================

echo Starting Document Manager V2.3 in TESTING mode...
echo.
echo ⚠️  Testing Mode Active - Use with caution ⚠️
echo.
echo --------------------------------------------------------------------------------
echo.

%PYTHON_CMD% run_v2_3.py

REM ================================================================================
REM Handle Errors
REM ================================================================================

if %errorlevel% neq 0 (
    echo.
    echo ===============================================================================
    echo ERROR: Application failed to start (Exit code: %errorlevel%)
    echo ===============================================================================
    echo.
    echo Common issues:
    echo.
    echo 1. MISSING DEPENDENCIES
    echo    Solution: Run this command:
    echo      %PYTHON_CMD% -m pip install -r requirements.txt
    echo.
    echo 2. MISSING FILES
    echo    Solution: Ensure all application files are present:
    echo      - run_v2_3.py
    echo      - src\ folder with all Python modules
    echo      - settings_v2_3.json
    echo.
    echo 3. FILE PERMISSIONS
    echo    Solution: Ensure you have read/write access to:
    echo      - Application directory
    echo      - Network paths configured in settings
    echo      - Database file location
    echo.
    echo 4. PYTHON VERSION
    echo    Solution: This app requires Python 3.8 or higher
    echo.
    echo 5. CODE SYNTAX ERRORS (Testing Version)
    echo    Solution: Check recent code changes for syntax errors
    echo              Revert to last working version if needed
    echo.
    echo For more help, check the documentation or contact IT support.
    echo.
    echo ===============================================================================
    pause
    exit /b 1
)

REM Application closed normally
echo.
echo Testing session complete.
echo.
pause
