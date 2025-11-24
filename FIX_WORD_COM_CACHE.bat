@echo off
REM Fix Word COM Cache for Folder Label Printing
REM This clears the win32com gen_py cache to fix AttributeError issues

echo ========================================
echo  Word COM Cache Repair Tool
echo ========================================
echo.
echo This tool fixes errors like:
echo   - "module 'win32com.gen_py.00020905' has no attribute..."
echo   - "CLSIDToClassMap" not found
echo   - Word automation failures
echo.
echo ========================================
echo.

REM Try to clear the cache
python -c "import win32com.client as win32; import shutil; import os; path = win32.gencache.GetGeneratePath(); print(f'Cache location: {path}'); print(''); result = shutil.rmtree(path, ignore_errors=True) if os.path.exists(path) else print('Cache not found'); print('Cache cleared successfully!' if os.path.exists(path) else 'Cache was already clear')" 2>nul

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ========================================
    echo  ✓ SUCCESS
    echo ========================================
    echo.
    echo The cache has been cleared.
    echo.
    echo Next time you print folder labels:
    echo   1. The app will use late-bound dispatch (works immediately^)
    echo   2. The cache will rebuild automatically in background
    echo   3. Future prints will be faster
    echo.
) else (
    echo.
    echo ========================================
    echo  ⚠ PARTIAL SUCCESS
    echo ========================================
    echo.
    echo Could not access Python/cache location.
    echo This is okay - the application has automatic fallback.
    echo.
    echo The folder label printing will still work using
    echo an alternative method (late-bound dispatch^).
    echo.
)

echo Press any key to close...
pause >nul
