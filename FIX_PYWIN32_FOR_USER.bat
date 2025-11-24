@echo off
REM Fix pywin32 for the EXACT Python that START_APP.bat uses

echo ========================================
echo  Fix pywin32 for User Installation
echo ========================================
echo.

REM Navigate to user's installation directory
set "USER_PATH=C:\Users\jjanney\Contract Lumber\Designers (FB) - General\BISTRACK CONNECTOR\Document Manager"

if not exist "%USER_PATH%" (
    echo ERROR: User installation not found
    pause
    exit /b 1
)

cd /d "%USER_PATH%"

echo Installation directory: %CD%
echo.

REM Find Python
echo Finding Python...
echo.

set PYTHON_CMD=

python --version >nul 2>&1
if %errorlevel% == 0 (
    set PYTHON_CMD=python
    goto :found_python
)

py --version >nul 2>&1
if %errorlevel% == 0 (
    set PYTHON_CMD=py
    goto :found_python
)

if exist "%LOCALAPPDATA%\Programs\Python\Python312\python.exe" (
    set "PYTHON_CMD=%LOCALAPPDATA%\Programs\Python\Python312\python.exe"
    goto :found_python
)

echo ERROR: Python not found!
pause
exit /b 1

:found_python
echo Found Python: %PYTHON_CMD%
%PYTHON_CMD% --version
echo.

REM Install pywin32
echo Installing pywin32...
echo.
%PYTHON_CMD% -m pip uninstall pywin32 -y
%PYTHON_CMD% -m pip install pywin32

echo.
echo Clearing cache...
echo.
%PYTHON_CMD% -c "import win32com.client; import shutil; shutil.rmtree(win32com.client.gencache.GetGeneratePath(), ignore_errors=True)"

echo.
echo Clearing __pycache__...
if exist "%USER_PATH%\src\__pycache__\" (
    rmdir /S /Q "%USER_PATH%\src\__pycache__\"
    echo Cleared
)

echo.
echo ========================================
echo  DONE!
echo ========================================
echo.
echo pywin32 installed successfully.
echo.
echo NEXT STEPS:
echo 1. Close Document Manager if running
echo 2. Launch using START_APP.bat
echo 3. Try folder label printing
echo.
pause
