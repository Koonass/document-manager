@echo off
REM ============================================
REM Check Word Template Bookmarks
REM ============================================

echo ============================================
echo Checking Template Bookmarks
echo ============================================
echo.

set PYTHON="C:\Users\jjanney\AppData\Local\Programs\Python\Python312\python.exe"

REM Check if Python exists
if not exist %PYTHON% (
    echo Python not found at: %PYTHON%
    echo.
    echo Trying alternative Python commands...
    set PYTHON=python
)

echo Using Python: %PYTHON%
%PYTHON% --version
echo.

echo Running template verification...
echo.

%PYTHON% src\verify_template.py

echo.
echo ============================================
echo.
pause
