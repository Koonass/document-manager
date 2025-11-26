@echo off
REM Copy only essential files to USB drive

echo ====================================================================
echo Copy Portable Package to USB Drive
echo ====================================================================
echo.
echo This will copy ONLY the necessary files (not temp/cache files)
echo.

set /p USB_DRIVE="Enter USB drive letter (e.g., E): "

if not exist "%USB_DRIVE%:\" (
    echo ERROR: Drive %USB_DRIVE%: not found!
    pause
    exit /b 1
)

set "SOURCE=portable-build"
set "DEST=%USB_DRIVE%:\DocumentManager"

echo.
echo Source: %SOURCE%
echo Destination: %DEST%
echo.
echo This will copy:
echo   - python\ folder (Python + packages)
echo   - src\ folder (application code)
echo   - LABEL TEMPLATE\ folder
echo   - Launcher scripts (.bat files)
echo   - Python scripts (.py files)
echo   - Settings template
echo   - Documentation
echo.
pause

echo.
echo Copying files...
echo.

REM Create destination if it doesn't exist
if not exist "%DEST%" mkdir "%DEST%"

REM Copy python folder (exclude __pycache__ and .pyc files)
echo [1/7] Copying Python...
xcopy /E /I /Y /EXCLUDE:exclude.txt "%SOURCE%\python" "%DEST%\python" >nul
echo [OK] Python copied

REM Copy src folder
echo [2/7] Copying application source...
xcopy /E /I /Y "%SOURCE%\src" "%DEST%\src" >nul
echo [OK] Source copied

REM Copy LABEL TEMPLATE
echo [3/7] Copying label template...
xcopy /E /I /Y "%SOURCE%\LABEL TEMPLATE" "%DEST%\LABEL TEMPLATE" >nul
echo [OK] Template copied

REM Copy batch scripts
echo [4/7] Copying launcher scripts...
copy /Y "%SOURCE%\*.bat" "%DEST%\" >nul
echo [OK] Scripts copied

REM Copy Python entry points
echo [5/7] Copying Python files...
copy /Y "%SOURCE%\run_v2_4.py" "%DEST%\" >nul
copy /Y "%SOURCE%\run_v2_4_readonly.py" "%DEST%\" >nul
copy /Y "%SOURCE%\setup_new_deployment.py" "%DEST%\" >nul
echo [OK] Python files copied

REM Copy settings template
echo [6/7] Copying settings template...
copy /Y "%SOURCE%\settings_v2_4_template.json" "%DEST%\" >nul
copy /Y "%SOURCE%\requirements.txt" "%DEST%\" >nul
echo [OK] Settings copied

REM Copy documentation (only essential guides)
echo [7/7] Copying documentation...
copy /Y "%SOURCE%\README.md" "%DEST%\" >nul 2>&1
copy /Y "%SOURCE%\PORTABLE_QUICK_START.txt" "%DEST%\" >nul 2>&1
copy /Y "%SOURCE%\PORTABLE_DEPLOYMENT_GUIDE.md" "%DEST%\" >nul 2>&1
copy /Y "%SOURCE%\READONLY_USB_GUIDE.txt" "%DEST%\" >nul 2>&1
copy /Y "%SOURCE%\DEPLOYMENT_README.md" "%DEST%\" >nul 2>&1
echo [OK] Documentation copied

echo.
echo ====================================================================
echo Copy Complete!
echo ====================================================================
echo.
echo Files copied to: %DEST%
echo.
echo What was NOT copied (saves space):
echo   - Test files
echo   - Build scripts
echo   - Extra documentation
echo   - Temporary files
echo   - __pycache__ folders
echo.
echo You can now:
echo   1. Safely eject USB drive
echo   2. Test on another computer
echo   3. Distribute to users
echo.
pause
