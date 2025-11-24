@echo off
REM Comprehensive diagnostic to find what broke

echo ========================================
echo  COMPREHENSIVE DIAGNOSTIC
echo ========================================
echo.

echo 1. PYTHON ENVIRONMENT
echo ========================================
echo.
echo Which Python is being used?
where python
echo.
python --version
echo.

echo.
echo 2. INSTALLED PACKAGES
echo ========================================
echo.
echo Checking pywin32 installation...
pip show pywin32
echo.

echo.
echo 3. CAN PYTHON IMPORT WIN32PRINT?
echo ========================================
echo.
python -c "import win32print; print('[OK] win32print imported successfully'); printers = win32print.EnumPrinters(2); print(f'Found {len(printers)} printers'); [print(f'  - {p[2]}') for p in printers]"
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] win32print import failed!
)
echo.

echo.
echo 4. CAN PYTHON IMPORT WIN32COM?
echo ========================================
echo.
python -c "import win32com.client as win32; print('[OK] win32com imported successfully'); word = win32.Dispatch('Word.Application'); print(f'[OK] Word version: {word.Version}'); word.Quit(); print('[OK] Word automation works!')"
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] win32com import or Word automation failed!
)
echo.

echo.
echo 5. CHECKING USER'S INSTALLATION PATH
echo ========================================
set "USER_PATH=C:\Users\jjanney\Contract Lumber\Designers (FB) - General\BISTRACK CONNECTOR\Document Manager"
echo.
echo User path: %USER_PATH%
echo.
if exist "%USER_PATH%\src\word_template_processor.py" (
    echo [OK] word_template_processor.py exists
    findstr /C:"_get_word_application" "%USER_PATH%\src\word_template_processor.py" >nul
    if %ERRORLEVEL% EQU 0 (
        echo [OK] Fix is present in the file
    ) else (
        echo [ERROR] Fix is NOT in the file
    )
) else (
    echo [ERROR] word_template_processor.py NOT found
)
echo.

echo.
echo 6. CHECKING FOR __pycache__
echo ========================================
echo.
if exist "%USER_PATH%\src\__pycache__\" (
    echo [WARNING] __pycache__ exists - may contain old bytecode
    dir "%USER_PATH%\src\__pycache__\word_template_processor*.pyc" 2>nul
) else (
    echo [OK] No __pycache__ folder
)
echo.

echo.
echo 7. WHAT PYTHON IS THE APP USING?
echo ========================================
echo.
echo Check the app startup - does it use:
echo   a) System Python: %USERPROFILE%\AppData\Local\Programs\Python\
echo   b) Virtual environment (venv)?
echo   c) Portable Python?
echo.
if exist "%USER_PATH%\venv\" (
    echo [FOUND] venv folder exists - app might be using this
    echo Location: %USER_PATH%\venv\
) else (
    echo [NOT FOUND] No venv folder
)
echo.

echo.
echo ========================================
echo  DIAGNOSTIC COMPLETE
echo ========================================
echo.
pause
