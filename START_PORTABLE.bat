@echo off
REM ============================================================
REM   Document Manager v2.4 - Portable Launcher
REM   Complete self-contained deployment - no installation needed!
REM   Works from USB, OneDrive, network share, or local drive
REM ============================================================

REM Get the directory where this batch file is located
set "APP_DIR=%~dp0"
cd /d "%APP_DIR%"

REM Clear screen and show startup message
cls
echo ====================================================================
echo   Document Manager v2.4 - Portable Edition
echo ====================================================================
echo.
echo Starting from: %APP_DIR%
echo.

REM ============================================================
REM Find portable Python
REM ============================================================

REM Try common portable Python locations
set "PYTHON_EXE="

if exist "%APP_DIR%python\python.exe" (
    set "PYTHON_EXE=%APP_DIR%python\python.exe"
    set "PYTHON_LOCATION=python\"
)

if exist "%APP_DIR%python-embedded\python.exe" (
    set "PYTHON_EXE=%APP_DIR%python-embedded\python.exe"
    set "PYTHON_LOCATION=python-embedded\"
)

if exist "%APP_DIR%python-portable\python.exe" (
    set "PYTHON_EXE=%APP_DIR%python-portable\python.exe"
    set "PYTHON_LOCATION=python-portable\"
)

REM Check if we found portable Python
if "%PYTHON_EXE%"=="" (
    echo [ERROR] Portable Python not found!
    echo.
    echo This portable version requires bundled Python.
    echo Expected location: python\python.exe
    echo.
    echo Please ensure:
    echo   1. The python\ folder exists in this directory
    echo   2. All files synced from OneDrive/network share
    echo   3. Sync is complete (check OneDrive icon for green checkmark)
    echo.
    echo To build portable package, run: BUILD_PORTABLE_PACKAGE.ps1
    echo Or use standard installation with system Python: START_V2_4.bat
    echo.
    goto :error
)

echo [OK] Found portable Python: %PYTHON_LOCATION%

REM Verify Python works
"%PYTHON_EXE%" --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Portable Python exists but won't run!
    echo.
    echo This could be caused by:
    echo   1. Incomplete file sync
    echo   2. Corrupted Python files
    echo   3. Antivirus blocking execution
    echo.
    echo Try:
    echo   - Wait for sync to complete
    echo   - Rebuild portable package
    echo   - Check antivirus logs
    echo.
    goto :error
)

REM Show Python version
for /f "tokens=*" %%i in ('"%PYTHON_EXE%" --version 2^>^&1') do set PYTHON_VERSION=%%i
echo [OK] %PYTHON_VERSION%

REM ============================================================
REM Check for settings and setup
REM ============================================================
echo.
echo Checking configuration...

if not exist "settings_v2_4.json" (
    echo [NOTICE] First time setup needed
    echo.
    echo Would you like to run setup now? This will:
    echo   - Create settings file from template
    echo   - Create DATA folder structure
    echo   - Validate everything is ready
    echo.
    choice /C YN /M "Run setup now"
    if errorlevel 2 goto :skip_setup
    if errorlevel 1 (
        echo.
        echo Running setup...
        call SETUP_FOR_NEW_USER.bat
        exit /b 0
    )
)

:skip_setup
echo [OK] Configuration ready

REM ============================================================
REM Launch application
REM ============================================================
echo.
echo ====================================================================
echo Starting Document Manager...
echo ====================================================================
echo.

"%PYTHON_EXE%" run_v2_4.py

REM Check exit code
if errorlevel 1 (
    echo.
    echo ====================================================================
    echo Application exited with error
    echo ====================================================================
    echo.
    echo Check error message above for details.
    echo.
    goto :error
)

REM Normal exit
echo.
echo Application closed normally.
goto :end

:error
echo.
echo ====================================================================
echo Startup Failed
echo ====================================================================
echo.
echo For help, see:
echo   - PORTABLE_DEPLOYMENT_GUIDE.md
echo   - TROUBLESHOOTING.md
echo   - README.md
echo.
pause
exit /b 1

:end
echo.
echo Press any key to exit...
pause >nul
exit /b 0
