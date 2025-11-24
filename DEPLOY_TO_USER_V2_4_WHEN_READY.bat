@echo off
REM Deployment Script for Document Manager v2.4.1
REM This script copies updated files to the user's installation

echo ========================================
echo  Document Manager v2.4.1 Deployment
echo ========================================
echo.

REM Prompt for user installation path
set /p USER_PATH="Enter user's installation path (e.g., C:\Users\jjanney\OneDrive\Document Manager): "

if not exist "%USER_PATH%" (
    echo.
    echo ERROR: Path does not exist: %USER_PATH%
    echo Please check the path and try again.
    echo.
    pause
    exit /b 1
)

echo.
echo Deploying to: %USER_PATH%
echo.
echo This will update the following:
echo   - 6 modified files in src\
echo   - 2 new files in src\
echo   - 2 optional helper files
echo.
set /p CONFIRM="Continue with deployment? (Y/N): "

if /i not "%CONFIRM%"=="Y" (
    echo.
    echo Deployment cancelled.
    pause
    exit /b 0
)

echo.
echo ========================================
echo  Step 1: Copying Modified Files
echo ========================================
echo.

copy "src\enhanced_expanded_view.py" "%USER_PATH%\src\" >nul
if %ERRORLEVEL% EQU 0 (echo ✓ enhanced_expanded_view.py) else (echo ✗ enhanced_expanded_view.py FAILED)

copy "src\main_v2_4.py" "%USER_PATH%\src\" >nul
if %ERRORLEVEL% EQU 0 (echo ✓ main_v2_4.py) else (echo ✗ main_v2_4.py FAILED)

copy "src\statistics_calendar_widget.py" "%USER_PATH%\src\" >nul
if %ERRORLEVEL% EQU 0 (echo ✓ statistics_calendar_widget.py) else (echo ✗ statistics_calendar_widget.py FAILED)

copy "src\word_template_processor.py" "%USER_PATH%\src\" >nul
if %ERRORLEVEL% EQU 0 (echo ✓ word_template_processor.py) else (echo ✗ word_template_processor.py FAILED)

copy "src\verify_template.py" "%USER_PATH%\src\" >nul
if %ERRORLEVEL% EQU 0 (echo ✓ verify_template.py) else (echo ✗ verify_template.py FAILED)

copy "src\enhanced_database_manager.py" "%USER_PATH%\src\" >nul
if %ERRORLEVEL% EQU 0 (echo ✓ enhanced_database_manager.py) else (echo ✗ enhanced_database_manager.py FAILED)

echo.
echo ========================================
echo  Step 2: Copying New Files
echo ========================================
echo.

copy "src\csv_batch_processor.py" "%USER_PATH%\src\" >nul
if %ERRORLEVEL% EQU 0 (echo ✓ csv_batch_processor.py ^(NEW^)) else (echo ✗ csv_batch_processor.py FAILED)

copy "src\shipping_schedule_view.py" "%USER_PATH%\src\" >nul
if %ERRORLEVEL% EQU 0 (echo ✓ shipping_schedule_view.py ^(NEW^)) else (echo ✗ shipping_schedule_view.py FAILED)

echo.
echo ========================================
echo  Step 3: Copying Optional Files
echo ========================================
echo.

copy "FIX_WORD_COM_CACHE.bat" "%USER_PATH%\" >nul
if %ERRORLEVEL% EQU 0 (echo ✓ FIX_WORD_COM_CACHE.bat ^(optional^)) else (echo ✗ FIX_WORD_COM_CACHE.bat FAILED)

copy "FOLDER_LABEL_PRINTING_FIX.md" "%USER_PATH%\" >nul
if %ERRORLEVEL% EQU 0 (echo ✓ FOLDER_LABEL_PRINTING_FIX.md ^(optional^)) else (echo ✗ FOLDER_LABEL_PRINTING_FIX.md FAILED)

echo.
echo ========================================
echo  Deployment Complete!
echo ========================================
echo.
echo What's new in v2.4.1:
echo   • CSV Processing View - Validate and upload CSVs
echo   • Shipping Schedule View - Date-grouped schedule
echo   • Fixed folder label printing AttributeError
echo   • Improved CSV display in calendar
echo   • CSV files now properly detected and matched
echo.
echo Next steps:
echo   1. User should close Document Manager if running
echo   2. User should restart the application
echo   3. Click SYNC DATA to verify CSV matching works
echo   4. Test new sidebar buttons (Process CSVs, Shipping Schedule)
echo.
pause
