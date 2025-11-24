@echo off
REM Verify the fix was deployed and clear Python cache

set "USER_PATH=C:\Users\jjanney\Contract Lumber\Designers (FB) - General\BISTRACK CONNECTOR\Document Manager"

echo ========================================
echo  Verifying Folder Printing Fix
echo ========================================
echo.

echo Checking if fix was deployed...
echo.

REM Check if the new method exists in the file
findstr /C:"_get_word_application" "%USER_PATH%\src\word_template_processor.py" >nul
if %ERRORLEVEL% EQU 0 (
    echo [OK] Fix is present in word_template_processor.py
) else (
    echo [ERROR] Fix NOT found in word_template_processor.py
    echo Please copy the file again!
    pause
    exit /b 1
)

echo.
echo Clearing Python bytecode cache...
echo.

REM Delete the __pycache__ folder
if exist "%USER_PATH%\src\__pycache__\" (
    echo Deleting: %USER_PATH%\src\__pycache__\
    rmdir /S /Q "%USER_PATH%\src\__pycache__\"
    echo [OK] Cache cleared!
) else (
    echo [OK] No cache to clear
)

echo.
echo ========================================
echo  Done!
echo ========================================
echo.
echo The fix is deployed and cache is cleared.
echo.
echo IMPORTANT: Restart the Document Manager application
echo for the fix to take effect!
echo.
pause
