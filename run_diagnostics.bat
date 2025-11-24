@echo off
echo ================================================================================
echo Print System Diagnostics
echo ================================================================================
echo.
echo Running diagnostic tests...
echo This will check your system and printers.
echo.

REM Try to find Python
set PYTHON_CMD=

REM Try python command
python --version >nul 2>&1
if %errorlevel% == 0 (
    set PYTHON_CMD=python
    goto :run_diagnostics
)

REM Try py launcher
py --version >nul 2>&1
if %errorlevel% == 0 (
    set PYTHON_CMD=py
    goto :run_diagnostics
)

REM Try python3
python3 --version >nul 2>&1
if %errorlevel% == 0 (
    set PYTHON_CMD=python3
    goto :run_diagnostics
)

REM Try common installation paths
if exist "C:\Python312\python.exe" (
    set PYTHON_CMD="C:\Python312\python.exe"
    goto :run_diagnostics
)

if exist "C:\Python311\python.exe" (
    set PYTHON_CMD="C:\Python311\python.exe"
    goto :run_diagnostics
)

if exist "C:\Python310\python.exe" (
    set PYTHON_CMD="C:\Python310\python.exe"
    goto :run_diagnostics
)

if exist "%LOCALAPPDATA%\Programs\Python\Python312\python.exe" (
    set PYTHON_CMD="%LOCALAPPDATA%\Programs\Python\Python312\python.exe"
    goto :run_diagnostics
)

if exist "%LOCALAPPDATA%\Programs\Python\Python311\python.exe" (
    set PYTHON_CMD="%LOCALAPPDATA%\Programs\Python\Python311\python.exe"
    goto :run_diagnostics
)

if exist "%LOCALAPPDATA%\Programs\Python\Python310\python.exe" (
    set PYTHON_CMD="%LOCALAPPDATA%\Programs\Python\Python310\python.exe"
    goto :run_diagnostics
)

REM If we get here, Python wasn't found
echo.
echo ERROR: Python not found!
echo.
echo Please make sure Python is installed.
echo You can download it from: https://www.python.org/downloads/
echo.
echo Or try running the diagnostics manually:
echo   1. Open Command Prompt
echo   2. Type: py src\print_diagnostics.py
echo      or: python src\print_diagnostics.py
echo.
echo If Python is installed but not in PATH, you can find python.exe and run:
echo   "C:\path\to\python.exe" src\print_diagnostics.py
echo.
pause
exit /b 1

:run_diagnostics
echo Found Python: %PYTHON_CMD%
echo.
%PYTHON_CMD% src\print_diagnostics.py

if %errorlevel% neq 0 (
    echo.
    echo ERROR: Diagnostics failed to run
    echo.
    echo Please check:
    echo   1. Python is installed correctly
    echo   2. You're in the correct directory
    echo   3. src\print_diagnostics.py exists
    echo.
    pause
    exit /b 1
)

echo.
echo ================================================================================
echo.
echo Diagnostic complete!
echo.
echo The report has been saved to: print_diagnostic_report.txt
echo.
echo You can now:
echo   1. Open print_diagnostic_report.txt
echo   2. Copy its contents
echo   3. Send it for debugging
echo.
echo Press any key to open the report file...
pause > nul

if exist print_diagnostic_report.txt (
    notepad print_diagnostic_report.txt
) else (
    echo.
    echo Report file not found. Check for errors above.
    echo.
    pause
)

echo.
echo Done!
pause
