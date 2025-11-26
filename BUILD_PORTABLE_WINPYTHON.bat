@echo off
REM Simple portable build using WinPython (includes tkinter)

echo ====================================================================
echo Document Manager v2.4 - Portable Build with WinPython
echo ====================================================================
echo.
echo This script will guide you through creating a portable package
echo with full Python including tkinter support.
echo.
echo REQUIREMENTS:
echo   1. Download WinPython from: https://winpython.github.io/
echo   2. Choose: WinPython 3.11.x (64-bit, dot version)
echo   3. Extract WinPython to a temp location
echo.
echo Recommended: WinPython 3.11.9.0 dot (includes Python + packages)
echo Download: ~50MB, Extract size: ~200MB
echo.
pause

set /p WINPYTHON_PATH="Enter path to WinPython folder (e.g., C:\WinPython\python-3.11.9.amd64): "

if not exist "%WINPYTHON_PATH%\python.exe" (
    echo.
    echo ERROR: python.exe not found at: %WINPYTHON_PATH%
    echo.
    echo Please check the path and try again.
    pause
    exit /b 1
)

echo.
echo [1/5] Verifying WinPython has tkinter...
"%WINPYTHON_PATH%\python.exe" -c "import tkinter; print('tkinter OK')" 2>nul
if errorlevel 1 (
    echo [ERROR] tkinter not found in WinPython!
    echo Please download the 'dot' version which includes tkinter.
    pause
    exit /b 1
)
echo [OK] tkinter verified

echo.
echo [2/5] Creating portable-build directory...
if not exist "portable-build" mkdir "portable-build"
if exist "portable-build\python" rmdir /S /Q "portable-build\python"
echo [OK] Directory ready

echo.
echo [3/5] Copying WinPython...
xcopy /E /I /Q "%WINPYTHON_PATH%" "portable-build\python"
echo [OK] Python copied

echo.
echo [4/5] Installing required packages...
portable-build\python\python.exe -m pip install pywin32 pandas PyPDF2 lxml --quiet
portable-build\python\Scripts\pywin32_postinstall.py -install -silent 2>nul
echo [OK] pywin32, pandas, and PyPDF2 installed

echo.
echo [5/5] Copying application files...
xcopy /E /I /Y "src" "portable-build\src" >nul
xcopy /E /I /Y "LABEL TEMPLATE" "portable-build\LABEL TEMPLATE" >nul
copy /Y run_v2_4.py "portable-build\" >nul
copy /Y run_v2_4_readonly.py "portable-build\" >nul
copy /Y setup_new_deployment.py "portable-build\" >nul
copy /Y settings_v2_4_template.json "portable-build\" >nul
copy /Y START_PORTABLE.bat "portable-build\" >nul
copy /Y START_PORTABLE_READONLY.bat "portable-build\" >nul
copy /Y SETUP_FOR_NEW_USER.bat "portable-build\" >nul
copy /Y *.md "portable-build\" >nul 2>&1
copy /Y *.txt "portable-build\" >nul 2>&1
echo [OK] Application files copied

echo.
echo ====================================================================
echo Build Complete!
echo ====================================================================
echo.
for /f %%A in ('dir /s /a "portable-build" ^| find "bytes"') do set size=%%A
echo Location: portable-build\
echo.
echo Testing the build...
portable-build\python\python.exe -c "import tkinter; import win32com.client; print('All modules OK')"

if errorlevel 1 (
    echo [WARNING] Module test failed
) else (
    echo [OK] All required modules present!
)

echo.
echo Ready to deploy! You can now:
echo   1. Test: cd portable-build ^&^& START_PORTABLE.bat
echo   2. Copy portable-build folder to USB drive
echo   3. Distribute to users
echo.
pause
