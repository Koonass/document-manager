@echo off
echo ================================================================================
echo Testing Python Installation
echo ================================================================================
echo.

REM Test method 1: python
echo Testing: python --version
python --version 2>nul
if %errorlevel% == 0 (
    echo [SUCCESS] 'python' command works!
    echo.
    echo You can use: python src\print_diagnostics.py
    echo.
    pause
    exit /b 0
)
echo [FAILED] 'python' command not found
echo.

REM Test method 2: py
echo Testing: py --version
py --version 2>nul
if %errorlevel% == 0 (
    echo [SUCCESS] 'py' command works!
    echo.
    echo You can use: py src\print_diagnostics.py
    echo.
    pause
    exit /b 0
)
echo [FAILED] 'py' command not found
echo.

REM Test method 3: python3
echo Testing: python3 --version
python3 --version 2>nul
if %errorlevel% == 0 (
    echo [SUCCESS] 'python3' command works!
    echo.
    echo You can use: python3 src\print_diagnostics.py
    echo.
    pause
    exit /b 0
)
echo [FAILED] 'python3' command not found
echo.

REM No Python found
echo ================================================================================
echo Python NOT FOUND
echo ================================================================================
echo.
echo Python doesn't appear to be installed or is not in your PATH.
echo.
echo Next steps:
echo   1. Check if Python is installed:
echo      - Open Settings
echo      - Go to Apps and features
echo      - Search for "Python"
echo.
echo   2. If Python IS installed:
echo      - See PYTHON_SETUP_HELP.md for how to add it to PATH
echo.
echo   3. If Python is NOT installed:
echo      - Download from: https://python.org/downloads
echo      - Or install from Microsoft Store
echo      - Make sure to check "Add Python to PATH" during install
echo.
echo ================================================================================
echo.
pause
