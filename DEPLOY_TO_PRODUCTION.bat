@echo off
REM ================================================================================
REM Document Manager - Deployment Script
REM ================================================================================
REM
REM This script copies tested code from TESTING folder to PRODUCTION folder
REM
REM Usage:
REM   1. Test all changes in TESTING folder using START_APP_TEST.bat
REM   2. When ready to deploy, run this script
REM   3. Users will get updates next time they restart the app
REM
REM For network deployment, update the paths below:
REM   - Set NETWORK_PATH to your network share (e.g., \\SERVER\Apps\DocumentManager)
REM
REM ================================================================================

setlocal enabledelayedexpansion

echo.
echo ================================================================================
echo Document Manager - Deployment Script
echo ================================================================================
echo.

REM ================================================================================
REM Configuration - EDIT THESE FOR NETWORK DEPLOYMENT
REM ================================================================================

REM For local testing, use current directory
set SOURCE_DIR=%~dp0
set SOURCE_DIR=%SOURCE_DIR:~0,-1%

REM For network deployment, set this to your network path
REM Example: set NETWORK_PATH=\\SERVER\Apps\DocumentManager
set NETWORK_PATH=

REM If NETWORK_PATH is set, use it for production/testing structure
if not "%NETWORK_PATH%"=="" (
    set SOURCE_DIR=%NETWORK_PATH%\TESTING
    set DEST_DIR=%NETWORK_PATH%\PRODUCTION
    set BACKUP_DIR=%NETWORK_PATH%\BACKUPS
) else (
    REM Local deployment (same folder, just mark as production-ready)
    set DEST_DIR=%SOURCE_DIR%
    set BACKUP_DIR=%SOURCE_DIR%\backups
)

echo Source (Testing): %SOURCE_DIR%
echo Destination (Production): %DEST_DIR%
echo Backup location: %BACKUP_DIR%
echo.

REM ================================================================================
REM Verify Source Files Exist
REM ================================================================================

echo Checking source files...
echo.

if not exist "%SOURCE_DIR%\run_v2_3.py" (
    echo ERROR: Source file run_v2_3.py not found in:
    echo   %SOURCE_DIR%
    echo.
    echo Please ensure you're running this script from the correct location.
    echo.
    pause
    exit /b 1
)

if not exist "%SOURCE_DIR%\src" (
    echo ERROR: Source folder 'src' not found in:
    echo   %SOURCE_DIR%
    echo.
    echo Please ensure all application files are present.
    echo.
    pause
    exit /b 1
)

echo ✓ Source files verified
echo.

REM ================================================================================
REM Show What Will Be Deployed
REM ================================================================================

echo The following will be deployed to production:
echo.
echo Files:
echo   - run_v2_3.py
echo   - requirements.txt
echo   - START_APP.bat (production launcher)
echo.
echo Folders:
echo   - src\ (all Python modules)
echo   - LABEL TEMPLATE\ (Word template)
echo.
echo Files NOT copied (data/config):
echo   - settings_v2_3.json (keep existing settings)
echo   - *.db (database files)
echo   - network_printers.json (keep existing printer config)
echo   - user_preferences.json (keep existing preferences)
echo.

REM ================================================================================
REM Confirmation
REM ================================================================================

echo ================================================================================
echo.
set /p CONFIRM="Deploy these changes to PRODUCTION? (yes/no): "
echo.

if /i not "%CONFIRM%"=="yes" (
    echo.
    echo Deployment cancelled.
    echo.
    pause
    exit /b 0
)

REM ================================================================================
REM Create Backup
REM ================================================================================

echo ================================================================================
echo Creating backup...
echo ================================================================================
echo.

REM Create backup directory with timestamp
for /f "tokens=2-4 delims=/ " %%a in ('date /t') do (set DATE=%%c-%%a-%%b)
for /f "tokens=1-2 delims=: " %%a in ('time /t') do (set TIME=%%a-%%b)
set TIMESTAMP=%DATE%_%TIME::=-%
set TIMESTAMP=%TIMESTAMP: =0%

set BACKUP_TARGET=%BACKUP_DIR%\backup_%TIMESTAMP%

if not exist "%BACKUP_DIR%" mkdir "%BACKUP_DIR%"

REM Only backup if destination exists
if exist "%DEST_DIR%\run_v2_3.py" (
    echo Backing up current production to:
    echo   %BACKUP_TARGET%
    echo.

    mkdir "%BACKUP_TARGET%" 2>nul

    REM Backup critical files
    if exist "%DEST_DIR%\run_v2_3.py" copy "%DEST_DIR%\run_v2_3.py" "%BACKUP_TARGET%\" >nul
    if exist "%DEST_DIR%\src" xcopy "%DEST_DIR%\src" "%BACKUP_TARGET%\src\" /E /I /Q >nul

    echo ✓ Backup created
    echo.
) else (
    echo No existing production files to backup (first deployment)
    echo.
)

REM ================================================================================
REM Deploy Files
REM ================================================================================

echo ================================================================================
echo Deploying to production...
echo ================================================================================
echo.

REM Create destination if it doesn't exist
if not exist "%DEST_DIR%" (
    echo Creating production directory...
    mkdir "%DEST_DIR%"
    echo.
)

REM Copy main files
echo Copying main application files...
copy "%SOURCE_DIR%\run_v2_3.py" "%DEST_DIR%\" >nul
if exist "%SOURCE_DIR%\requirements.txt" copy "%SOURCE_DIR%\requirements.txt" "%DEST_DIR%\" >nul
copy "%SOURCE_DIR%\START_APP.bat" "%DEST_DIR%\" >nul
echo ✓ Main files copied
echo.

REM Copy src directory
echo Copying source code modules...
if exist "%DEST_DIR%\src" rmdir /s /q "%DEST_DIR%\src"
xcopy "%SOURCE_DIR%\src" "%DEST_DIR%\src\" /E /I /Q >nul
echo ✓ Source modules copied
echo.

REM Copy template folder if it exists
if exist "%SOURCE_DIR%\LABEL TEMPLATE" (
    echo Copying label template...
    if not exist "%DEST_DIR%\LABEL TEMPLATE" mkdir "%DEST_DIR%\LABEL TEMPLATE"
    xcopy "%SOURCE_DIR%\LABEL TEMPLATE" "%DEST_DIR%\LABEL TEMPLATE\" /E /I /Q >nul
    echo ✓ Template copied
    echo.
)

REM Copy documentation files
echo Copying documentation...
if exist "%SOURCE_DIR%\README.md" copy "%SOURCE_DIR%\README.md" "%DEST_DIR%\" >nul 2>&1
if exist "%SOURCE_DIR%\PRINTING_GUIDE.md" copy "%SOURCE_DIR%\PRINTING_GUIDE.md" "%DEST_DIR%\" >nul 2>&1
if exist "%SOURCE_DIR%\NETWORK_DEPLOYMENT_GUIDE.md" copy "%SOURCE_DIR%\NETWORK_DEPLOYMENT_GUIDE.md" "%DEST_DIR%\" >nul 2>&1
echo ✓ Documentation copied
echo.

REM ================================================================================
REM Verify Deployment
REM ================================================================================

echo ================================================================================
echo Verifying deployment...
echo ================================================================================
echo.

set ERRORS=0

if not exist "%DEST_DIR%\run_v2_3.py" (
    echo ✗ ERROR: run_v2_3.py not found in production
    set ERRORS=1
)

if not exist "%DEST_DIR%\src" (
    echo ✗ ERROR: src folder not found in production
    set ERRORS=1
)

if not exist "%DEST_DIR%\START_APP.bat" (
    echo ✗ ERROR: START_APP.bat not found in production
    set ERRORS=1
)

if %ERRORS% equ 0 (
    echo ✓ Deployment verified successfully
    echo.
    echo ================================================================================
    echo DEPLOYMENT COMPLETE
    echo ================================================================================
    echo.
    echo Production has been updated successfully!
    echo.
    echo Next steps:
    echo   1. Notify users that updates are available
    echo   2. Ask users to restart the application (close and run START_APP.bat)
    echo   3. Monitor for any issues after deployment
    echo.
    echo Backup location (for rollback if needed):
    echo   %BACKUP_TARGET%
    echo.
    echo ================================================================================
) else (
    echo.
    echo ✗✗✗ DEPLOYMENT FAILED ✗✗✗
    echo.
    echo Some files were not copied successfully.
    echo Please check the errors above and try again.
    echo.
    echo To rollback, restore files from:
    echo   %BACKUP_TARGET%
    echo.
)

echo.
pause
