@echo off
REM Auto-setup script for Document Manager v2.4
REM This script prepares the application for first-time use by any user

echo ====================================================================
echo Document Manager v2.4 - First Time Setup
echo ====================================================================
echo.
echo This script will:
echo  1. Create settings file from template (if needed)
echo  2. Create required DATA folder structure
echo  3. Validate template files exist
echo  4. Launch the application when ready
echo.
pause

REM Change to script directory
cd /d "%~dp0"

echo.
echo [1/4] Checking settings file...
echo -----------------------------------------------------------------------

if exist "settings_v2_4.json" (
    echo [OK] Settings file already exists: settings_v2_4.json
    echo      Using existing configuration.
) else (
    if exist "settings_v2_4_template.json" (
        echo [SETUP] Copying template to create settings_v2_4.json...
        copy "settings_v2_4_template.json" "settings_v2_4.json" >nul
        if errorlevel 1 (
            echo [ERROR] Failed to copy settings template!
            goto :error
        )
        echo [OK] Settings file created from template.
    ) else (
        echo [ERROR] Template file 'settings_v2_4_template.json' not found!
        echo        Cannot create settings file.
        goto :error
    )
)

echo.
echo [2/4] Creating DATA folder structure...
echo -----------------------------------------------------------------------

REM Create main DATA folder
if not exist "DATA" (
    mkdir "DATA"
    echo [OK] Created: DATA\
) else (
    echo [OK] Already exists: DATA\
)

REM Create subdirectories
if not exist "DATA\BisTrack Exports" (
    mkdir "DATA\BisTrack Exports"
    echo [OK] Created: DATA\BisTrack Exports\
) else (
    echo [OK] Already exists: DATA\BisTrack Exports\
)

if not exist "DATA\PDFs" (
    mkdir "DATA\PDFs"
    echo [OK] Created: DATA\PDFs\
) else (
    echo [OK] Already exists: DATA\PDFs\
)

if not exist "DATA\Archive" (
    mkdir "DATA\Archive"
    echo [OK] Created: DATA\Archive\
) else (
    echo [OK] Already exists: DATA\Archive\
)

echo.
echo [3/4] Validating template files...
echo -----------------------------------------------------------------------

if exist "LABEL TEMPLATE\Contract_Lumber_Label_Template.docx" (
    echo [OK] Label template found.
) else (
    echo [WARNING] Label template not found at:
    echo           LABEL TEMPLATE\Contract_Lumber_Label_Template.docx
    echo.
    echo           Label printing will not work until template is added.
    echo           You can continue, but add the template before printing.
)

echo.
echo [4/4] Checking Python installation...
echo -----------------------------------------------------------------------

python --version >nul 2>&1
if errorlevel 1 (
    echo [WARNING] Python not found in PATH!
    echo.
    echo You may need to:
    echo  - Install Python from python.org
    echo  - OR use portable Python setup (see PORTABLE_PYTHON_SETUP.md)
    echo  - OR run STARTUP_PORTABLE.bat if using embedded Python
    echo.
    set PYTHON_MISSING=1
) else (
    python --version
    echo [OK] Python is available.
    set PYTHON_MISSING=0
)

echo.
echo ====================================================================
echo Setup Complete!
echo ====================================================================
echo.

if "%PYTHON_MISSING%"=="1" (
    echo [NOTICE] Python is not available. Please install Python or use
    echo          portable Python before running the application.
    echo.
    echo Press any key to exit...
    pause >nul
    exit /b 0
)

echo Folder structure created:
echo   Document Manager\
echo   ├── DATA\
echo   │   ├── BisTrack Exports\  (place HTML exports here)
echo   │   ├── PDFs\              (generated labels saved here)
echo   │   └── Archive\           (archived records stored here)
echo   ├── settings_v2_4.json     (your configuration)
echo   └── LABEL TEMPLATE\
echo.
echo Ready to launch! Press any key to start Document Manager v2.4...
pause >nul

echo.
echo Starting application...
python run_v2_4.py

goto :end

:error
echo.
echo ====================================================================
echo Setup Failed!
echo ====================================================================
echo.
echo Please check the error messages above and try again.
echo If problems persist, see the documentation or contact support.
echo.
pause
exit /b 1

:end
echo.
echo Application closed. Press any key to exit...
pause >nul
exit /b 0
