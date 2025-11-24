@echo off
REM Quick fix for printer issues - Updates print_presets.json with actual printer names

echo.
echo ============================================
echo  Fix Printer Configuration
echo ============================================
echo.
echo This will fix the issue where printers are
echo not printing because of empty configuration.
echo.
echo Press Ctrl+C to cancel, or
pause

REM Try to find Python
set PYTHON_CMD=

REM Check if python is in PATH
where python >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    set PYTHON_CMD=python
    goto :run_fix
)

REM Check py launcher
where py >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    set PYTHON_CMD=py
    goto :run_fix
)

REM Check common locations
if exist "C:\Python311\python.exe" set PYTHON_CMD=C:\Python311\python.exe
if exist "C:\Python310\python.exe" set PYTHON_CMD=C:\Python310\python.exe
if exist "%LOCALAPPDATA%\Programs\Python\Python311\python.exe" set PYTHON_CMD=%LOCALAPPDATA%\Programs\Python\Python311\python.exe

if defined PYTHON_CMD goto :run_fix

echo ERROR: Python not found!
echo Please run: python fix_printer_presets.py
pause
exit /b 1

:run_fix
echo.
echo Running printer fix tool...
echo.
"%PYTHON_CMD%" fix_printer_presets.py

if errorlevel 1 (
    echo.
    echo Fix tool encountered an error.
    echo See above for details.
    pause
) else (
    echo.
    echo ============================================
    echo  Fix Complete!
    echo ============================================
    echo.
    echo Your printers should now work.
    echo Try printing again from your application.
    echo.
    pause
)
