@echo off
echo.
echo ============================================
echo Testing Template Bookmark Filling
echo ============================================
echo.

REM Change to script directory
cd /d "%~dp0"

echo Current directory: %CD%
echo.

REM Set Python path
set PYTHON="C:\Users\jjanney\AppData\Local\Programs\Python\Python312\python.exe"

echo Checking Python...
if not exist %PYTHON% (
    echo ERROR: Python not found at %PYTHON%
    echo.
    echo Trying alternative...
    set PYTHON=python
)

%PYTHON% --version
echo.

echo Checking if script exists...
if not exist "TEST_TEMPLATE_TO_PDF.py" (
    echo ERROR: TEST_TEMPLATE_TO_PDF.py not found in current directory
    echo.
    echo Current directory contents:
    dir /b *.py
    echo.
    pause
    exit /b 1
)

echo ✓ Script found
echo.

echo Running template test...
echo.
echo ============================================
echo.

%PYTHON% TEST_TEMPLATE_TO_PDF.py

echo.
echo ============================================
echo.

if exist "TEST_LABEL_OUTPUT.pdf" (
    echo ✓ PDF created successfully!
    echo Location: %CD%\TEST_LABEL_OUTPUT.pdf
    echo.
    echo Opening PDF...
    start "" "TEST_LABEL_OUTPUT.pdf"
) else (
    echo ❌ PDF was not created
    echo Check error messages above
)

echo.
pause
