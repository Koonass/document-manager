@echo off
setlocal enabledelayedexpansion

echo ============================================================
echo   Document Manager - OneDrive Deployment Helper
echo ============================================================
echo.
echo This script helps you deploy Document Manager to OneDrive
echo for shared access by multiple users.
echo.
echo Benefits:
echo   - No .exe files (avoids antivirus flags)
echo   - No server scripts needed
echo   - Automatic sync to all users
echo   - Shared database
echo.
echo ============================================================
echo.

REM Try to detect OneDrive paths (both personal and business)
set "PERSONAL_ONEDRIVE="
set "BUSINESS_ONEDRIVE="

echo Detecting OneDrive locations...
echo.

REM Check for personal OneDrive
if exist "%USERPROFILE%\OneDrive" (
    if not exist "%USERPROFILE%\OneDrive\*-*" (
        set "PERSONAL_ONEDRIVE=%USERPROFILE%\OneDrive"
        echo [1] Personal OneDrive found: !PERSONAL_ONEDRIVE!
    )
)

REM Check for business OneDrive (contains company name with dash)
for /d %%D in ("%USERPROFILE%\OneDrive - *") do (
    set "BUSINESS_ONEDRIVE=%%D"
    echo [2] Business OneDrive found: !BUSINESS_ONEDRIVE!
)

echo.
echo ============================================================
echo IMPORTANT: Choose Deployment Location
echo ============================================================
echo.
echo Multiple OneDrive folders detected!
echo.
echo For SHARED access across all users, you should deploy to:
echo   - Business/Company OneDrive (recommended)
echo   - Or a shared Teams folder
echo.
echo DO NOT use Personal OneDrive if you want to share with team!
echo.
echo ============================================================
echo.

if defined BUSINESS_ONEDRIVE (
    echo Recommended: !BUSINESS_ONEDRIVE!\Apps\DocumentManager
    echo.
    set /p "USE_BUSINESS=Use Business OneDrive? (Y/N): "

    if /i "!USE_BUSINESS!"=="Y" (
        set "TARGET_PATH=!BUSINESS_ONEDRIVE!\Apps\DocumentManager"
        goto :path_selected
    )
)

if defined PERSONAL_ONEDRIVE (
    echo Alternative: !PERSONAL_ONEDRIVE!\Apps\DocumentManager
    echo.
    set /p "USE_PERSONAL=Use Personal OneDrive? (Y/N): "

    if /i "!USE_PERSONAL!"=="Y" (
        set "TARGET_PATH=!PERSONAL_ONEDRIVE!\Apps\DocumentManager"
        goto :path_selected
    )
)

REM If neither selected or available, ask for custom path
echo.
echo No automatic path selected. Please enter custom path.
echo.
echo Common options:
echo   - Business: %USERPROFILE%\OneDrive - CompanyName\Apps\DocumentManager
echo   - Teams Shared: %USERPROFILE%\OneDrive - CompanyName\Shared Documents\Apps\DocumentManager
echo   - SharePoint: %USERPROFILE%\CompanyName\TeamSite - Documents\Apps\DocumentManager
echo.
set /p "TARGET_PATH=Enter full deployment path: "

:path_selected
echo.
echo Selected path: !TARGET_PATH!
echo.
set /p "CONFIRM_PATH=Is this correct? (Y/N): "

if /i not "!CONFIRM_PATH!"=="Y" (
    echo.
    echo Please enter the full path where you want to deploy:
    echo.
    echo Examples:
    echo   Business: C:\Users\YourName\OneDrive - CompanyName\Apps\DocumentManager
    echo   Shared:   C:\Users\YourName\OneDrive - CompanyName\Shared Documents\Apps\DocumentManager
    echo.
    set /p "TARGET_PATH=Deployment path: "
)

echo.
echo ============================================================
echo Deployment Plan
echo ============================================================
echo.
echo From: %CD%
echo To:   !TARGET_PATH!
echo.
echo The following will be copied:
echo   - All Python source files (src\)
echo   - Application launcher (START_APP.bat)
echo   - Setup scripts (SETUP_PYTHON_DEPS.bat)
echo   - Configuration files
echo   - Documentation
echo   - Label templates
echo.
echo The following will NOT be copied:
echo   - Virtual environment (venv\)
echo   - Git files (.git\)
echo   - Cache files (__pycache__)
echo   - Compiled Python files (.pyc)
echo   - Local databases
echo.
echo ============================================================
echo.
set /p "CONFIRM=Proceed with deployment? (Y/N): "

if /i not "!CONFIRM!"=="Y" (
    echo.
    echo Deployment cancelled.
    pause
    exit /b 0
)

echo.
echo ============================================================
echo Starting Deployment...
echo ============================================================
echo.

REM Create target directory
if not exist "!TARGET_PATH!" (
    echo Creating directory: !TARGET_PATH!
    mkdir "!TARGET_PATH!" 2>nul
    if errorlevel 1 (
        echo ERROR: Could not create target directory
        echo Please check the path and try again.
        pause
        exit /b 1
    )
)

REM Create DATA subdirectory
echo Creating DATA folder structure...
mkdir "!TARGET_PATH!\DATA" 2>nul
mkdir "!TARGET_PATH!\DATA\BisTrack Exports" 2>nul
mkdir "!TARGET_PATH!\DATA\PDFs" 2>nul
mkdir "!TARGET_PATH!\DATA\Archive" 2>nul

REM Copy main application files
echo.
echo Copying application files...
echo   - Python launcher...
copy /Y "run_v2_3.py" "!TARGET_PATH!\" >nul 2>&1

echo   - Batch files...
copy /Y "START_APP.bat" "!TARGET_PATH!\" >nul 2>&1
copy /Y "SETUP_PYTHON_DEPS.bat" "!TARGET_PATH!\" >nul 2>&1

echo   - Configuration files...
copy /Y "requirements.txt" "!TARGET_PATH!\" >nul 2>&1
copy /Y "settings_v2_3_onedrive_example.json" "!TARGET_PATH!\" >nul 2>&1

REM Check if settings_v2_3.json already exists (don't overwrite)
if exist "!TARGET_PATH!\settings_v2_3.json" (
    echo   - Settings file already exists, skipping...
) else (
    echo   - Creating settings file from OneDrive template...
    copy /Y "settings_v2_3_onedrive_example.json" "!TARGET_PATH!\settings_v2_3.json" >nul 2>&1
)

echo   - Source code (src\)...
xcopy /Y /E /I "src" "!TARGET_PATH!\src" >nul 2>&1

echo   - Label templates...
xcopy /Y /E /I "LABEL TEMPLATE" "!TARGET_PATH!\LABEL TEMPLATE" >nul 2>&1

echo   - Documentation...
copy /Y "README.md" "!TARGET_PATH!\" >nul 2>&1
copy /Y "ONEDRIVE_DEPLOYMENT_GUIDE.md" "!TARGET_PATH!\" >nul 2>&1
copy /Y "ONEDRIVE_QUICK_START.md" "!TARGET_PATH!\" >nul 2>&1
copy /Y "SHARED_DATABASE_SETUP.md" "!TARGET_PATH!\" >nul 2>&1
copy /Y "PRINTING_GUIDE.md" "!TARGET_PATH!\" >nul 2>&1
copy /Y "USER_MANAGEMENT.md" "!TARGET_PATH!\" >nul 2>&1

REM Optional: Copy sample files if they exist
if exist "sample csv" (
    echo   - Sample files...
    xcopy /Y /E /I "sample csv" "!TARGET_PATH!\sample csv" >nul 2>&1
)

echo.
echo ============================================================
echo Deployment Complete!
echo ============================================================
echo.
echo Files deployed to: !TARGET_PATH!
echo.
echo Next Steps:
echo.
echo 1. Wait for OneDrive to sync (check OneDrive icon in system tray)
echo.
echo 2. Each user should:
echo    a. Navigate to: !TARGET_PATH!
echo    b. Double-click: SETUP_PYTHON_DEPS.bat (one time setup)
echo    c. Right-click START_APP.bat and create desktop shortcut
echo    d. Rename shortcut to "Document Manager"
echo.
echo 3. Test with first user, then second user to verify sync
echo.
echo For detailed instructions, see:
echo    ONEDRIVE_QUICK_START.md (in the deployed folder)
echo.
echo ============================================================
echo.
set /p "OPEN_FOLDER=Open deployed folder now? (Y/N): "

if /i "!OPEN_FOLDER!"=="Y" (
    explorer "!TARGET_PATH!"
)

echo.
echo Deployment complete! Press any key to exit...
pause >nul
