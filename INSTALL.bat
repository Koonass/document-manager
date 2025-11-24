@echo off
REM ============================================
REM Document Manager V2.3 - Installation Script
REM ============================================

echo ============================================
echo Document Manager V2.3 - Installation
echo ============================================
echo.

REM Try to find Python automatically
set PYTHON_PATH=

REM Check common Python locations
for %%P in (
    "C:\Users\%USERNAME%\AppData\Local\Programs\Python\Python312\python.exe"
    "C:\Users\%USERNAME%\AppData\Local\Programs\Python\Python311\python.exe"
    "C:\Users\%USERNAME%\AppData\Local\Programs\Python\Python310\python.exe"
    "C:\Python312\python.exe"
    "C:\Python311\python.exe"
    "C:\Python310\python.exe"
) do (
    if exist %%P (
        set PYTHON_PATH=%%P
        goto :found_python
    )
)

REM Try PATH
python --version >nul 2>&1
if %errorlevel% equ 0 (
    set PYTHON_PATH=python
    goto :found_python
)

echo ERROR: Could not find Python installation
echo.
echo Please edit this file and manually set PYTHON_PATH at the top
echo Example: set PYTHON_PATH="C:\Full\Path\To\python.exe"
echo.
echo Or install Python from: https://www.python.org/downloads/
pause
exit /b 1

:found_python
echo Found Python at: %PYTHON_PATH%
echo.

REM Verify Python works
%PYTHON_PATH% --version
if errorlevel 1 (
    echo ERROR: Python command failed
    pause
    exit /b 1
)

echo.
echo Upgrading pip...
%PYTHON_PATH% -m pip install --upgrade pip
if errorlevel 1 (
    echo WARNING: pip upgrade failed, continuing anyway...
)

echo.
echo Installing required packages...
echo - pandas (data processing)
echo - PyPDF2 (PDF handling)
echo - pywin32 (Windows integration, Word automation)
echo - lxml (HTML parsing)
echo.

%PYTHON_PATH% -m pip install -r requirements.txt
if errorlevel 1 (
    echo.
    echo ERROR: Package installation failed
    echo.
    echo Try running this as Administrator:
    echo   Right-click this file and select "Run as Administrator"
    pause
    exit /b 1
)

echo.
echo Running pywin32 post-install...
%PYTHON_PATH% -m pywin32_postinstall -install >nul 2>&1

echo.
echo ============================================
echo Installation Complete!
echo ============================================
echo.
echo Verifying installation...
%PYTHON_PATH% -c "import pandas; import PyPDF2; import win32com.client; import lxml; print('All packages verified!')"
if errorlevel 1 (
    echo.
    echo WARNING: Package verification failed
    echo Some packages may not be installed correctly
    pause
    exit /b 1
)

echo.
echo Creating START_APP.bat...
(
    echo @echo off
    echo REM Start Document Manager V2.3
    echo %PYTHON_PATH% run_v2_3.py
    echo pause
) > START_APP.bat

echo.
echo ============================================
echo Setup Complete!
echo ============================================
echo.
echo To run the application:
echo   1. Double-click START_APP.bat
echo   OR
echo   2. Run: %PYTHON_PATH% run_v2_3.py
echo.
echo Next steps:
echo   1. Configure file paths in the application
echo   2. Run diagnose_label_printing.py to verify label printing setup
echo.
pause
