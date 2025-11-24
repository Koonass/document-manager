@echo off
REM Deploy ONLY Folder Label Printing Fix to Production v2.3
REM This does NOT include any v2.4 CSV features

echo ========================================
echo  Folder Label Printing Fix
echo  Deploy to Production v2.3
echo ========================================
echo.
echo This will ONLY update folder label printing.
echo NO other features will be changed.
echo.

REM Prompt for user installation path
set /p USER_PATH="Enter user's v2.3 installation path: "

if not exist "%USER_PATH%" (
    echo.
    echo ERROR: Path does not exist: %USER_PATH%
    echo.
    pause
    exit /b 1
)

echo.
echo Deploying folder printing fix to: %USER_PATH%
echo.
echo Files to update:
echo   - src\word_template_processor.py
echo   - src\verify_template.py
echo   - FIX_WORD_COM_CACHE.bat (optional)
echo.
set /p CONFIRM="Continue? (Y/N): "

if /i not "%CONFIRM%"=="Y" (
    echo.
    echo Cancelled.
    pause
    exit /b 0
)

echo.
echo ========================================
echo  Deploying...
echo ========================================
echo.

copy "src\word_template_processor.py" "%USER_PATH%\src\" >nul
if %ERRORLEVEL% EQU 0 (echo ✓ word_template_processor.py) else (echo ✗ word_template_processor.py FAILED)

copy "src\verify_template.py" "%USER_PATH%\src\" >nul
if %ERRORLEVEL% EQU 0 (echo ✓ verify_template.py) else (echo ✗ verify_template.py FAILED)

copy "FIX_WORD_COM_CACHE.bat" "%USER_PATH%\" >nul
if %ERRORLEVEL% EQU 0 (echo ✓ FIX_WORD_COM_CACHE.bat ^(optional^)) else (echo - FIX_WORD_COM_CACHE.bat skipped)

echo.
echo ========================================
echo  ✓ Deployment Complete
echo ========================================
echo.
echo What was fixed:
echo   • Folder label printing AttributeError auto-fix
echo   • "CLSIDToClassMap" error handled automatically
echo   • Immediate fallback to working method
echo   • Cache cleared in background
echo.
echo User can continue using v2.3 normally.
echo Folder labels will now print without errors.
echo.
echo No restart required - fix activates on next print.
echo.
pause
