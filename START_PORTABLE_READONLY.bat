@echo off
REM ============================================================
REM   Document Manager v2.4 - Portable Launcher (Read-Only Safe)
REM   Handles read-only USB drives by storing data locally
REM   Application runs from USB, data saves to user's AppData
REM ============================================================

REM Get the directory where this batch file is located
set "APP_DIR=%~dp0"
cd /d "%APP_DIR%"

REM Clear screen and show startup message
cls
echo ====================================================================
echo   Document Manager v2.4 - Portable Edition (Read-Only Safe)
echo ====================================================================
echo.
echo Application location: %APP_DIR%
echo.

REM ============================================================
REM Detect if running from read-only location (USB, CD, etc.)
REM ============================================================

echo Checking write permissions...

REM Try to create a test file
echo test > "%APP_DIR%write_test.tmp" 2>nul

if exist "%APP_DIR%write_test.tmp" (
    REM Location is writable
    del "%APP_DIR%write_test.tmp" >nul 2>&1
    set "DATA_LOCATION=%APP_DIR%DATA"
    set "SETTINGS_LOCATION=%APP_DIR%"
    set "READ_ONLY=NO"
    echo [OK] Location is writable - data will be stored here
) else (
    REM Location is read-only
    set "READ_ONLY=YES"

    REM Use user's AppData folder for data storage
    set "DATA_ROOT=%APPDATA%\DocumentManager"
    set "DATA_LOCATION=%DATA_ROOT%\DATA"
    set "SETTINGS_LOCATION=%DATA_ROOT%"

    echo [NOTICE] Location is READ-ONLY (USB drive?)
    echo [INFO] Data will be stored in: %DATA_ROOT%
    echo.
    echo This allows you to:
    echo   - Run app from read-only USB drive
    echo   - Store your data on this computer
    echo   - Keep app portable on USB
    echo.
)

REM ============================================================
REM Create data directory structure if needed
REM ============================================================

if "%READ_ONLY%"=="YES" (
    echo.
    echo Creating data folder structure...

    if not exist "%DATA_ROOT%" (
        mkdir "%DATA_ROOT%"
        echo [OK] Created: %DATA_ROOT%
    )

    if not exist "%DATA_LOCATION%" (
        mkdir "%DATA_LOCATION%"
        echo [OK] Created: %DATA_LOCATION%
    )

    if not exist "%DATA_LOCATION%\BisTrack Exports" (
        mkdir "%DATA_LOCATION%\BisTrack Exports"
        echo [OK] Created: BisTrack Exports folder
    )

    if not exist "%DATA_LOCATION%\PDFs" (
        mkdir "%DATA_LOCATION%\PDFs"
        echo [OK] Created: PDFs folder
    )

    if not exist "%DATA_LOCATION%\Archive" (
        mkdir "%DATA_LOCATION%\Archive"
        echo [OK] Created: Archive folder
    )

    REM Copy settings template if needed
    if not exist "%SETTINGS_LOCATION%\settings_v2_4.json" (
        if exist "%APP_DIR%settings_v2_4_template.json" (
            echo [OK] Creating settings file...
            copy "%APP_DIR%settings_v2_4_template.json" "%SETTINGS_LOCATION%\settings_v2_4.json" >nul

            REM Update paths in settings to point to local DATA folder
            echo [OK] Configuring data paths for local storage...
        )
    )
)

REM ============================================================
REM Find portable Python
REM ============================================================
echo.
echo Looking for portable Python...

set "PYTHON_EXE="

if exist "%APP_DIR%python\python.exe" (
    set "PYTHON_EXE=%APP_DIR%python\python.exe"
    echo [OK] Found: python\python.exe
)

if exist "%APP_DIR%python-embedded\python.exe" (
    set "PYTHON_EXE=%APP_DIR%python-embedded\python.exe"
    echo [OK] Found: python-embedded\python.exe
)

if exist "%APP_DIR%python-portable\python.exe" (
    set "PYTHON_EXE=%APP_DIR%python-portable\python.exe"
    echo [OK] Found: python-portable\python.exe
)

if "%PYTHON_EXE%"=="" (
    echo [ERROR] Portable Python not found!
    echo.
    echo Expected location: python\python.exe
    echo.
    echo Please ensure all files copied from USB correctly.
    echo.
    goto :error
)

REM Verify Python works
"%PYTHON_EXE%" --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python won't run!
    goto :error
)

for /f "tokens=*" %%i in ('"%PYTHON_EXE%" --version 2^>^&1') do set PYTHON_VERSION=%%i
echo [OK] %PYTHON_VERSION%

REM ============================================================
REM Set environment variables for the application
REM ============================================================

if "%READ_ONLY%"=="YES" (
    REM Pass data location to Python via environment variable
    set "DM_DATA_PATH=%DATA_LOCATION%"
    set "DM_SETTINGS_PATH=%SETTINGS_LOCATION%\settings_v2_4.json"
    set "DM_READONLY_MODE=1"

    echo.
    echo ====================================================================
    echo Configuration:
    echo ====================================================================
    echo   App Location:      %APP_DIR% (read-only)
    echo   Data Location:     %DATA_LOCATION% (writable)
    echo   Settings Location: %SETTINGS_LOCATION% (writable)
    echo ====================================================================
)

REM ============================================================
REM Launch application
REM ============================================================
echo.
echo ====================================================================
echo Starting Document Manager...
echo ====================================================================
echo.

if "%READ_ONLY%"=="YES" (
    echo DATA FOLDER: %DATA_LOCATION%
    echo.
    echo IMPORTANT: Place your HTML files in:
    echo %DATA_LOCATION%\BisTrack Exports\
    echo.
    echo Generated PDFs will be saved to:
    echo %DATA_LOCATION%\PDFs\
    echo.
    pause
)

"%PYTHON_EXE%" run_v2_4_readonly.py

REM Check exit code
if errorlevel 1 (
    echo.
    echo ====================================================================
    echo Application exited with error
    echo ====================================================================
    echo.
    goto :error
)

REM Normal exit
echo.
echo Application closed normally.

if "%READ_ONLY%"=="YES" (
    echo.
    echo Your data is stored at: %DATA_ROOT%
    echo You can access your database and files there.
)

goto :end

:error
echo.
echo ====================================================================
echo Startup Failed
echo ====================================================================
echo.
echo For help, see:
echo   - PORTABLE_DEPLOYMENT_GUIDE.md
echo   - README.md
echo.
pause
exit /b 1

:end
echo.
echo Press any key to exit...
pause >nul
exit /b 0
