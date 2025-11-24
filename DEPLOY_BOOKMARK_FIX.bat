@echo off
REM Deploy bookmark fix to user installation

echo ========================================
echo  Deploy Bookmark Fix
echo ========================================
echo.
echo This will update word_template_processor.py
echo to include LotSub and Level bookmarks.
echo.

set "USER_PATH=C:\Users\jjanney\Contract Lumber\Designers (FB) - General\BISTRACK CONNECTOR\Document Manager"

copy "C:\code\Document Manager\src\word_template_processor.py" "%USER_PATH%\src\" /Y

if %ERRORLEVEL% EQU 0 (
    echo.
    echo [OK] File deployed successfully!
    echo.
    echo Clearing __pycache__...
    if exist "%USER_PATH%\src\__pycache__\" (
        rmdir /S /Q "%USER_PATH%\src\__pycache__\"
        echo [OK] Cache cleared
    )
    echo.
    echo ========================================
    echo  DONE!
    echo ========================================
    echo.
    echo The bookmarks LotSub and Level will now be filled.
    echo.
    echo NEXT STEP: Restart Document Manager and try printing again.
) else (
    echo.
    echo [ERROR] Deployment failed!
)

echo.
pause
