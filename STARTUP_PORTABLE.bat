@echo off
REM ============================================================
REM   Document Manager - Portable Python Launcher
REM   No Python installation required!
REM ============================================================

REM Get the directory where this batch file is located
set "APP_DIR=%~dp0"

REM Use portable Python (bundled with application)
set "PYTHON_EXE=%APP_DIR%python-embedded\python.exe"

REM Check if portable Python exists
if not exist "%PYTHON_EXE%" (
    echo.
    echo ============================================================
    echo   ERROR: Portable Python not found!
    echo ============================================================
    echo.
    echo Expected location: %PYTHON_EXE%
    echo.
    echo Please ensure:
    echo   1. Files synced from OneDrive/Teams
    echo   2. python-embedded folder is present
    echo   3. OneDrive sync is complete
    echo.
    echo Check OneDrive icon in system tray - should show green checkmark
    echo.
    pause
    exit /b 1
)

REM Change to application directory
cd /d "%APP_DIR%"

REM Clear screen and show startup message
cls
echo ============================================================
echo   Document Manager V2.3
echo   Starting with Portable Python...
echo ============================================================
echo.

REM Launch application with portable Python
"%PYTHON_EXE%" run_v2_3.py

REM If application exits with error, pause to show error
if errorlevel 1 (
    echo.
    echo ============================================================
    echo   Application exited with error
    echo ============================================================
    echo.
    pause
)
