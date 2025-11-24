@echo off
REM Helper script to copy deployment files to a test/production location
REM Excludes development files, user data, and build artifacts

echo ====================================================================
echo Document Manager - Copy Files for Deployment
echo ====================================================================
echo.
echo This script will copy ONLY the necessary files for deployment.
echo It will NOT copy user data, databases, or development files.
echo.

set /p TARGET="Enter target folder path (e.g., C:\Apps\DocumentManager-Test): "

if "%TARGET%"=="" (
    echo Error: No target path specified!
    pause
    exit /b 1
)

echo.
echo Target: %TARGET%
echo.
echo Creating target directory...

if not exist "%TARGET%" (
    mkdir "%TARGET%"
    if errorlevel 1 (
        echo Failed to create target directory!
        pause
        exit /b 1
    )
)

echo.
echo ====================================================================
echo Copying files...
echo ====================================================================

REM Copy source code
echo [1/8] Copying src/ folder...
xcopy /E /I /Y "src" "%TARGET%\src" >nul
if errorlevel 1 (
    echo ERROR: Failed to copy src/
    pause
    exit /b 1
)
echo     [OK] src/ copied

REM Copy label template
echo [2/8] Copying LABEL TEMPLATE/ folder...
xcopy /E /I /Y "LABEL TEMPLATE" "%TARGET%\LABEL TEMPLATE" >nul
if errorlevel 1 (
    echo ERROR: Failed to copy LABEL TEMPLATE/
    pause
    exit /b 1
)
echo     [OK] LABEL TEMPLATE/ copied

REM Copy launcher scripts
echo [3/8] Copying .bat files...
copy /Y *.bat "%TARGET%\" >nul 2>&1
echo     [OK] Batch files copied

REM Copy Python entry points
echo [4/8] Copying Python entry points...
copy /Y run_*.py "%TARGET%\" >nul 2>&1
copy /Y setup_new_deployment.py "%TARGET%\" >nul 2>&1
echo     [OK] Python files copied

REM Copy template settings (not actual settings!)
echo [5/8] Copying settings templates...
copy /Y settings_v2_*_template.json "%TARGET%\" >nul 2>&1
copy /Y settings_v2_*_example.json "%TARGET%\" >nul 2>&1
echo     [OK] Settings templates copied

REM Copy requirements
echo [6/8] Copying requirements.txt...
copy /Y requirements.txt "%TARGET%\" >nul 2>&1
echo     [OK] requirements.txt copied

REM Copy documentation
echo [7/8] Copying documentation...
copy /Y *.md "%TARGET%\" >nul 2>&1
copy /Y *.txt "%TARGET%\" >nul 2>&1
echo     [OK] Documentation copied

REM Copy git files
echo [8/8] Copying .gitignore...
copy /Y .gitignore "%TARGET%\" >nul 2>&1
echo     [OK] .gitignore copied

echo.
echo ====================================================================
echo Copy Complete!
echo ====================================================================
echo.
echo Deployment files copied to:
echo %TARGET%
echo.
echo What was copied:
echo   [x] src/ folder
echo   [x] LABEL TEMPLATE/
echo   [x] Batch scripts (.bat)
echo   [x] Python scripts (.py)
echo   [x] Settings templates
echo   [x] Documentation
echo.
echo What was NOT copied (intentionally):
echo   [ ] DATA/ folder (created by setup)
echo   [ ] settings_v2_4.json (created by setup)
echo   [ ] venv/, python/ (not needed)
echo   [ ] *.db files (user data)
echo   [ ] samples/, tests/ (test data)
echo.
echo Next steps:
echo   1. Navigate to: %TARGET%
echo   2. Run: SETUP_FOR_NEW_USER.bat
echo   3. Test the application
echo.
pause
