@echo off
REM New User Setup - Run this ONCE on each new user's machine

echo ========================================
echo  Document Manager - New User Setup
echo ========================================
echo.
echo This will set up Document Manager on your computer.
echo You only need to run this ONCE.
echo.
echo What this does:
echo   1. Installs required Python package (pywin32)
echo   2. Creates a desktop shortcut
echo.
pause

REM Find Python
echo.
echo Finding Python installation...
echo.

set PYTHON_CMD=

python --version >nul 2>&1
if %errorlevel% == 0 (
    set PYTHON_CMD=python
    goto :found_python
)

py --version >nul 2>&1
if %errorlevel% == 0 (
    set PYTHON_CMD=py
    goto :found_python
)

if exist "%LOCALAPPDATA%\Programs\Python\Python312\python.exe" (
    set "PYTHON_CMD=%LOCALAPPDATA%\Programs\Python\Python312\python.exe"
    goto :found_python
)

echo ERROR: Python not found!
echo Please install Python first from: https://www.python.org/downloads/
echo Make sure to check "Add Python to PATH" during installation.
echo.
pause
exit /b 1

:found_python
echo [OK] Found Python: %PYTHON_CMD%
%PYTHON_CMD% --version
echo.

REM Install pywin32
echo Installing required package (pywin32)...
echo This is needed for Word automation and printer access.
echo.
%PYTHON_CMD% -m pip install pywin32 --quiet
if %errorlevel% == 0 (
    echo [OK] pywin32 installed successfully
) else (
    echo [WARNING] pywin32 installation had issues, but may still work
)

echo.
echo Creating desktop shortcut...
echo.

REM Get the directory where this script is located (the shared network folder)
set "APP_DIR=%~dp0"
set "SHORTCUT_TARGET=%APP_DIR%START_APP.bat"

REM Create shortcut using PowerShell
powershell -Command "$WshShell = New-Object -ComObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%USERPROFILE%\Desktop\Document Manager.lnk'); $Shortcut.TargetPath = '%SHORTCUT_TARGET%'; $Shortcut.WorkingDirectory = '%APP_DIR%'; $Shortcut.Description = 'Document Manager V2.3'; $Shortcut.Save()"

if exist "%USERPROFILE%\Desktop\Document Manager.lnk" (
    echo [OK] Desktop shortcut created
) else (
    echo [WARNING] Could not create shortcut automatically
    echo You can manually create a shortcut to: %SHORTCUT_TARGET%
)

echo.
echo ========================================
echo  Setup Complete!
echo ========================================
echo.
echo You can now use Document Manager from the desktop shortcut.
echo.
echo The application files are stored on the shared network drive:
echo %APP_DIR%
echo.
echo All users share the same:
echo   - Application files
echo   - Database
echo   - Settings
echo   - Templates
echo.
pause
