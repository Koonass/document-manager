@echo off
REM Safe cleanup script - moves unnecessary files to CLEANUP_BACKUP folder
REM Review the backup folder before permanently deleting

echo ========================================
echo  Production Folder Cleanup
echo ========================================
echo.
echo This script will MOVE (not delete) unnecessary files
echo to a backup folder: CLEANUP_BACKUP
echo.
echo You can review the files and delete them later.
echo.
echo Files that will be kept:
echo   - START_APP.bat
echo   - run_v2_3.py
echo   - settings_v2_3.json
echo   - requirements.txt
echo   - SETUP_NEW_USER.bat
echo   - FIX_PYWIN32_FOR_USER.bat
echo   - src/ folder
echo   - LABEL TEMPLATE/ folder
echo   - Database files
echo.
echo Everything else will be moved to CLEANUP_BACKUP/
echo.
pause

REM Create backup folder
if not exist "CLEANUP_BACKUP\" (
    mkdir "CLEANUP_BACKUP"
    echo Created CLEANUP_BACKUP folder
)
echo.

echo Moving files to CLEANUP_BACKUP...
echo.

REM Move documentation files
echo Moving documentation files...
move /Y *.md "CLEANUP_BACKUP\" 2>nul
move /Y *.txt "CLEANUP_BACKUP\" 2>nul
REM But keep requirements.txt
move /Y "CLEANUP_BACKUP\requirements.txt" . 2>nul
move /Y "CLEANUP_BACKUP\PRODUCTION_FILES_CHECKLIST.txt" . 2>nul

REM Move old version files
echo Moving old version files...
move /Y run_v2_1.py "CLEANUP_BACKUP\" 2>nul
move /Y run_v2_2.py "CLEANUP_BACKUP\" 2>nul
move /Y run_v2_4.py "CLEANUP_BACKUP\" 2>nul

REM Move test scripts
echo Moving test scripts...
move /Y test_*.py "CLEANUP_BACKUP\" 2>nul
move /Y diagnose_*.py "CLEANUP_BACKUP\" 2>nul
move /Y check_*.py "CLEANUP_BACKUP\" 2>nul
move /Y fix_*.py "CLEANUP_BACKUP\" 2>nul
move /Y simple_*.py "CLEANUP_BACKUP\" 2>nul
move /Y read_*.py "CLEANUP_BACKUP\" 2>nul
move /Y create_*.py "CLEANUP_BACKUP\" 2>nul
move /Y update_*.py "CLEANUP_BACKUP\" 2>nul
move /Y show_*.py "CLEANUP_BACKUP\" 2>nul

REM Move deployment/build batch files
echo Moving deployment batch files...
move /Y DEPLOY_*.bat "CLEANUP_BACKUP\" 2>nul
move /Y BUILD_*.bat "CLEANUP_BACKUP\" 2>nul
move /Y TEST_*.bat "CLEANUP_BACKUP\" 2>nul
move /Y DEBUG_*.bat "CLEANUP_BACKUP\" 2>nul
move /Y DIAGNOSE_*.bat "CLEANUP_BACKUP\" 2>nul
move /Y CHECK_*.bat "CLEANUP_BACKUP\" 2>nul
move /Y INSTALL*.bat "CLEANUP_BACKUP\" 2>nul
move /Y VERIFY_*.bat "CLEANUP_BACKUP\" 2>nul
move /Y FIX_WORD_COM_CACHE.bat "CLEANUP_BACKUP\" 2>nul
move /Y CLEAR_*.bat "CLEANUP_BACKUP\" 2>nul
move /Y LIST_*.bat "CLEANUP_BACKUP\" 2>nul
move /Y SHOW_*.bat "CLEANUP_BACKUP\" 2>nul
move /Y STEP_*.bat "CLEANUP_BACKUP\" 2>nul
move /Y RUN_*.bat "CLEANUP_BACKUP\" 2>nul

REM Move old settings files
echo Moving old settings files...
move /Y settings.json "CLEANUP_BACKUP\" 2>nul
move /Y settings_v2.json "CLEANUP_BACKUP\" 2>nul
move /Y settings_v2_2.json "CLEANUP_BACKUP\" 2>nul
move /Y settings_v2_4.json "CLEANUP_BACKUP\" 2>nul
move /Y settings_v2_3_network_example.json "CLEANUP_BACKUP\" 2>nul
move /Y settings_v2_3_onedrive_example.json "CLEANUP_BACKUP\" 2>nul
move /Y print_presets.json "CLEANUP_BACKUP\" 2>nul

REM Move folders
echo Moving unnecessary folders...
if exist "archive\" (
    move /Y "archive" "CLEANUP_BACKUP\" 2>nul
)
if exist "samples\" (
    move /Y "samples" "CLEANUP_BACKUP\" 2>nul
)
if exist "sample csv\" (
    move /Y "sample csv" "CLEANUP_BACKUP\" 2>nul
)
if exist "tests\" (
    move /Y "tests" "CLEANUP_BACKUP\" 2>nul
)
if exist "document-manager-web\" (
    move /Y "document-manager-web" "CLEANUP_BACKUP\" 2>nul
)
if exist "TEAMS_DEPLOYMENT\" (
    move /Y "TEAMS_DEPLOYMENT" "CLEANUP_BACKUP\" 2>nul
)
if exist "DESIGN FILES\" (
    echo WARNING: DESIGN FILES folder found - review manually before moving
    REM Uncomment to move: move /Y "DESIGN FILES" "CLEANUP_BACKUP\" 2>nul
)
if exist "venv\" (
    move /Y "venv" "CLEANUP_BACKUP\" 2>nul
)
if exist "python\" (
    move /Y "python" "CLEANUP_BACKUP\" 2>nul
)

REM Move other files
echo Moving other files...
move /Y .gitignore "CLEANUP_BACKUP\" 2>nul
move /Y *.backup* "CLEANUP_BACKUP\" 2>nul
move /Y *.log "CLEANUP_BACKUP\" 2>nul
move /Y bookmark_output.txt "CLEANUP_BACKUP\" 2>nul
move /Y download_*.ps1 "CLEANUP_BACKUP\" 2>nul
move /Y setup_*.ps1 "CLEANUP_BACKUP\" 2>nul
move /Y printer_diagnostics.py "CLEANUP_BACKUP\" 2>nul

echo.
echo ========================================
echo  Cleanup Complete!
echo ========================================
echo.
echo All unnecessary files moved to: CLEANUP_BACKUP\
echo.
echo NEXT STEPS:
echo 1. Test the application to ensure it still works
echo 2. Review files in CLEANUP_BACKUP\
echo 3. If everything works, delete CLEANUP_BACKUP\ folder
echo.
echo Production folder should now contain only:
echo   - START_APP.bat
echo   - run_v2_3.py
echo   - settings_v2_3.json
echo   - requirements.txt
echo   - SETUP_NEW_USER.bat
echo   - FIX_PYWIN32_FOR_USER.bat
echo   - PRODUCTION_FILES_CHECKLIST.txt
echo   - src\ folder
echo   - LABEL TEMPLATE\ folder
echo   - Database file(s)
echo   - CLEANUP_BACKUP\ (review and delete)
echo.
pause
