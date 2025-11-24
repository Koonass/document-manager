@echo off
REM Wrapper to run PowerShell build script

echo ====================================================================
echo Document Manager v2.4 - Build Portable Package
echo ====================================================================
echo.
echo This will:
echo   1. Download portable Python 3.11.9 (~25MB)
echo   2. Install PyQt5 and pywin32 (~250MB)
echo   3. Copy application files
echo   4. Create complete portable package (~350MB total)
echo.
echo Build location: .\portable-build\
echo.
echo This will take 3-5 minutes depending on your internet speed.
echo.
pause

echo.
echo Starting build...
echo.

powershell.exe -ExecutionPolicy Bypass -File "%~dp0BUILD_PORTABLE_PACKAGE.ps1"

if errorlevel 1 (
    echo.
    echo ====================================================================
    echo Build Failed!
    echo ====================================================================
    echo.
    echo Check error messages above.
    echo.
    echo Common issues:
    echo   - No internet connection
    echo   - PowerShell execution policy blocked script
    echo   - Antivirus blocked downloads
    echo.
    pause
    exit /b 1
)

echo.
echo ====================================================================
echo Success!
echo ====================================================================
echo.
echo Portable package ready at: portable-build\
echo.
echo Next steps:
echo   1. Test it: cd portable-build ^&^& START_PORTABLE.bat
echo   2. Copy 'portable-build' folder to USB/OneDrive/Network
echo   3. Rename folder as desired (e.g., "DocumentManager")
echo   4. Users run START_PORTABLE.bat
echo.
pause
