@echo off
REM Copy ONLY essential files to USB (clean, minimal deployment)

setlocal EnableDelayedExpansion

echo ====================================================================
echo Copy Essential Files to USB Drive
echo ====================================================================
echo.

set /p USB_DRIVE="Enter USB drive letter (e.g., E): "

if not exist "%USB_DRIVE%:\" (
    echo ERROR: Drive %USB_DRIVE%: not found!
    pause
    exit /b 1
)

set "DEST=%USB_DRIVE%:\DocumentManager"

echo.
echo Destination: %DEST%
echo.
echo This will create a CLEAN portable package with:
echo   - Python interpreter and required packages
echo   - Application source code
echo   - Label template
echo   - Launcher scripts
echo   - Minimal documentation
echo.
echo Estimated size: ~250-300 MB
echo.
pause

REM Delete old installation if exists
if exist "%DEST%" (
    echo.
    echo Removing old installation...
    rmdir /S /Q "%DEST%" 2>nul
)

echo.
echo Creating directory structure...
mkdir "%DEST%"
mkdir "%DEST%\python"
mkdir "%DEST%\src"
mkdir "%DEST%\LABEL TEMPLATE"

echo.
echo [1/6] Copying Python (this takes 1-2 minutes)...
robocopy "portable-build\python" "%DEST%\python" /E /NFL /NDL /NJH /NJS /nc /ns /np /XD __pycache__ /XF *.pyc *.pyo
echo [OK] Python copied

echo.
echo [2/6] Copying application source...
robocopy "portable-build\src" "%DEST%\src" /E /NFL /NDL /NJH /NJS /nc /ns /np
echo [OK] Source copied

echo.
echo [3/6] Copying label template...
robocopy "portable-build\LABEL TEMPLATE" "%DEST%\LABEL TEMPLATE" /E /NFL /NDL /NJH /NJS /nc /ns /np
echo [OK] Template copied

echo.
echo [4/6] Copying launcher scripts...
copy /Y "portable-build\START_PORTABLE.bat" "%DEST%\" >nul
copy /Y "portable-build\START_PORTABLE_READONLY.bat" "%DEST%\" >nul
copy /Y "portable-build\SETUP_FOR_NEW_USER.bat" "%DEST%\" >nul
echo [OK] Launchers copied

echo.
echo [5/6] Copying Python scripts...
copy /Y "portable-build\run_v2_4.py" "%DEST%\" >nul
copy /Y "portable-build\run_v2_4_readonly.py" "%DEST%\" >nul
copy /Y "portable-build\setup_new_deployment.py" "%DEST%\" >nul
copy /Y "portable-build\settings_v2_4_template.json" "%DEST%\" >nul
copy /Y "portable-build\requirements.txt" "%DEST%\" >nul
echo [OK] Scripts copied

echo.
echo [6/6] Copying essential documentation...
copy /Y "portable-build\PORTABLE_QUICK_START.txt" "%DEST%\" >nul 2>&1
copy /Y "portable-build\README.md" "%DEST%\" >nul 2>&1
copy /Y "portable-build\READONLY_USB_GUIDE.txt" "%DEST%\" >nul 2>&1
echo [OK] Documentation copied

echo.
echo ====================================================================
echo Copy Complete!
echo ====================================================================
echo.
echo Location: %DEST%
echo.

REM Calculate size
for /f "tokens=3" %%a in ('dir "%DEST%" /-c /s ^| find "bytes"') do set size=%%a
set /a size_mb=%size:~0,-6%
echo Total size: ~%size_mb% MB
echo.

echo What was excluded to save space:
echo   - Build scripts and tools
echo   - Extra documentation (50+ .md/.txt files)
echo   - Test data
echo   - Temporary files
echo   - Python cache files
echo.
echo Ready to use!
echo   1. Safely eject USB
echo   2. Plug into any Windows PC
echo   3. Run: START_PORTABLE.bat
echo.
pause
