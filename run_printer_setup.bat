@echo off
REM Quick launcher for printer diagnostics tool
REM Run this on your work machine to configure printers

echo.
echo ============================================
echo  Document Manager - Printer Setup
echo ============================================
echo.

REM Try to find Python (works even if not in PATH)
set PYTHON_CMD=

REM Method 1: Check if python is in PATH
where python >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    set PYTHON_CMD=python
    goto :run_diagnostics
)

REM Method 2: Check common Python installation locations
if exist "C:\Python312\python.exe" set PYTHON_CMD=C:\Python312\python.exe
if exist "C:\Python311\python.exe" set PYTHON_CMD=C:\Python311\python.exe
if exist "C:\Python310\python.exe" set PYTHON_CMD=C:\Python310\python.exe
if exist "C:\Python39\python.exe" set PYTHON_CMD=C:\Python39\python.exe
if exist "C:\Python38\python.exe" set PYTHON_CMD=C:\Python38\python.exe

if defined PYTHON_CMD goto :run_diagnostics

REM Method 3: Check AppData local installations
if exist "%LOCALAPPDATA%\Programs\Python\Python312\python.exe" set PYTHON_CMD=%LOCALAPPDATA%\Programs\Python\Python312\python.exe
if exist "%LOCALAPPDATA%\Programs\Python\Python311\python.exe" set PYTHON_CMD=%LOCALAPPDATA%\Programs\Python\Python311\python.exe
if exist "%LOCALAPPDATA%\Programs\Python\Python310\python.exe" set PYTHON_CMD=%LOCALAPPDATA%\Programs\Python\Python310\python.exe
if exist "%LOCALAPPDATA%\Programs\Python\Python39\python.exe" set PYTHON_CMD=%LOCALAPPDATA%\Programs\Python\Python39\python.exe

if defined PYTHON_CMD goto :run_diagnostics

REM Method 4: Check Program Files
if exist "C:\Program Files\Python312\python.exe" set PYTHON_CMD=C:\Program Files\Python312\python.exe
if exist "C:\Program Files\Python311\python.exe" set PYTHON_CMD=C:\Program Files\Python311\python.exe
if exist "C:\Program Files\Python310\python.exe" set PYTHON_CMD=C:\Program Files\Python310\python.exe

if defined PYTHON_CMD goto :run_diagnostics

REM Python not found
echo ERROR: Python not found!
echo.
echo Please install Python or edit this file to point to your Python installation.
echo.
echo To find your Python installation, open Command Prompt and run:
echo   where python
echo.
echo Then edit this .bat file and set PYTHON_CMD to that path.
echo.
pause
exit /b 1

:run_diagnostics
echo Found Python: %PYTHON_CMD%
echo.
echo Starting printer diagnostics tool...
echo.

"%PYTHON_CMD%" printer_diagnostics.py

if errorlevel 1 (
    echo.
    echo ERROR: Failed to start diagnostics tool
    echo.
    echo Possible issues:
    echo   - Missing dependencies
    echo.
    echo Try running:
    echo   "%PYTHON_CMD%" -m pip install -r requirements.txt
    echo.
    pause
)
