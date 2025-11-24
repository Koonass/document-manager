@echo off
REM ============================================
REM Fix Dependencies - Install to Correct Python
REM ============================================

echo ============================================
echo Dependency Fix Tool
echo ============================================
echo.
echo This script will find which Python you want to use
echo and install packages directly to that Python.
echo.

REM First, check if START_APP.bat exists
if exist START_APP.bat (
    echo Found existing START_APP.bat
    echo.
    echo Current START_APP.bat contents:
    type START_APP.bat
    echo.
    echo ----------------------------------------
)

echo Let's find the correct Python to use...
echo.

REM Option 1: Try python command
echo [Option 1] Testing 'python' command...
python --version >nul 2>&1
if %errorlevel% equ 0 (
    echo Found: python
    python --version
    set FOUND_PYTHON=python
    goto :ask_user
)

REM Option 2: Try python3 command
echo [Option 2] Testing 'python3' command...
python3 --version >nul 2>&1
if %errorlevel% equ 0 (
    echo Found: python3
    python3 --version
    set FOUND_PYTHON=python3
    goto :ask_user
)

REM Option 3: Try py launcher
echo [Option 3] Testing 'py' launcher...
py --version >nul 2>&1
if %errorlevel% equ 0 (
    echo Found: py
    py --version
    set FOUND_PYTHON=py
    goto :ask_user
)

echo.
echo ERROR: Could not find any Python installation!
echo.
echo Please install Python from: https://www.python.org/downloads/
echo Or manually specify the path by editing this file.
echo.
pause
exit /b 1

:ask_user
echo.
echo ============================================
echo Found Python: %FOUND_PYTHON%
echo ============================================
echo.
set /p CONFIRM="Do you want to use this Python? (yes/no): "
if /i not "%CONFIRM%"=="yes" if /i not "%CONFIRM%"=="y" (
    echo.
    echo Please run DIAGNOSE_PYTHON.bat to see all Python installations
    echo Then edit START_APP.bat manually with the correct path.
    pause
    exit /b 0
)

echo.
echo ============================================
echo Installing packages to: %FOUND_PYTHON%
echo ============================================
echo.

echo Step 1: Upgrading pip...
%FOUND_PYTHON% -m pip install --upgrade pip
echo.

echo Step 2: Installing pandas...
%FOUND_PYTHON% -m pip install pandas
echo.

echo Step 3: Installing PyPDF2...
%FOUND_PYTHON% -m pip install PyPDF2
echo.

echo Step 4: Installing pywin32...
%FOUND_PYTHON% -m pip install pywin32
echo.

echo Step 5: Installing lxml...
%FOUND_PYTHON% -m pip install lxml
echo.

echo Step 6: Running pywin32 post-install...
%FOUND_PYTHON% -m pywin32_postinstall -install
echo.

echo ============================================
echo Verifying Installation
echo ============================================
echo.

%FOUND_PYTHON% -c "import sys; print('Python:', sys.executable)"
echo.

%FOUND_PYTHON% -c "import pandas; print('✓ pandas installed')"
%FOUND_PYTHON% -c "import PyPDF2; print('✓ PyPDF2 installed')"
%FOUND_PYTHON% -c "import win32com.client; print('✓ pywin32 installed')"
%FOUND_PYTHON% -c "import lxml; print('✓ lxml installed')"

if errorlevel 1 (
    echo.
    echo ERROR: Some packages failed to install
    echo Try running as Administrator
    pause
    exit /b 1
)

echo.
echo ============================================
echo Creating/Updating START_APP.bat
echo ============================================
echo.

REM Create START_APP.bat with the correct Python
(
    echo @echo off
    echo REM Start Document Manager V2.3
    echo %FOUND_PYTHON% run_v2_3.py
    echo if errorlevel 1 pause
) > START_APP.bat

echo Created START_APP.bat using: %FOUND_PYTHON%
echo.

echo ============================================
echo SUCCESS! All packages installed
echo ============================================
echo.
echo You can now run the application with:
echo   START_APP.bat
echo.
echo Or manually with:
echo   %FOUND_PYTHON% run_v2_3.py
echo.
pause
