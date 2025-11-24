@echo off
REM ============================================
REM Create Custom Installer for Any User
REM ============================================

echo ============================================
echo Custom Installer Creator
echo ============================================
echo.
echo This will create a custom installer for a specific user
echo with their Python path.
echo.

REM Get username
set /p USERNAME="Enter Windows username: "

REM Get Python version (default 312)
set /p PYVER="Enter Python version (e.g., 312, 311, 310) [default: 312]: "
if "%PYVER%"=="" set PYVER=312

REM Build the path
set PYTHON_PATH=C:\Users\%USERNAME%\AppData\Local\Programs\Python\Python%PYVER%\python.exe

echo.
echo Python path will be: %PYTHON_PATH%
echo.
set /p CONFIRM="Is this correct? (yes/no): "

if /i not "%CONFIRM%"=="yes" if /i not "%CONFIRM%"=="y" (
    echo.
    echo Cancelled. Please run again with correct information.
    pause
    exit /b 0
)

REM Create the installer file
set INSTALLER_FILE=INSTALL_FOR_%USERNAME%.bat

echo.
echo Creating: %INSTALLER_FILE%
echo.

(
echo @echo off
echo REM ============================================
echo REM Install for user: %USERNAME%
echo REM Python location: %PYTHON_PATH%
echo REM NO ADMIN RIGHTS REQUIRED
echo REM ============================================
echo.
echo echo ============================================
echo echo Document Manager V2.3 - Installation
echo echo ============================================
echo echo.
echo echo Installing for user: %USERNAME%
echo echo Python: %PYTHON_PATH%
echo echo.
echo.
echo REM Set the Python path
echo set PYTHON="%PYTHON_PATH%"
echo.
echo REM Verify Python exists
echo if not exist %%PYTHON%% ^(
echo     echo ERROR: Python not found at expected location!
echo     echo.
echo     echo Please check the path. If Python is in a different location,
echo     echo edit this file and update the PYTHON variable.
echo     pause
echo     exit /b 1
echo ^)
echo.
echo echo Found Python:
echo %%PYTHON%% --version
echo echo.
echo.
echo echo ============================================
echo echo Step 1: Upgrading pip ^(no admin needed^)
echo echo ============================================
echo %%PYTHON%% -m pip install --upgrade pip --user
echo echo.
echo.
echo echo ============================================
echo echo Step 2: Installing pandas
echo echo ============================================
echo %%PYTHON%% -m pip install pandas --user
echo echo.
echo.
echo echo ============================================
echo echo Step 3: Installing PyPDF2
echo echo ============================================
echo %%PYTHON%% -m pip install PyPDF2 --user
echo echo.
echo.
echo echo ============================================
echo echo Step 4: Installing pywin32
echo echo ============================================
echo %%PYTHON%% -m pip install pywin32 --user
echo echo.
echo.
echo echo ============================================
echo echo Step 5: Installing lxml
echo echo ============================================
echo %%PYTHON%% -m pip install lxml --user
echo echo.
echo.
echo echo ============================================
echo echo Step 6: Configuring pywin32
echo echo ============================================
echo %%PYTHON%% -m pywin32_postinstall -install
echo echo.
echo.
echo echo ============================================
echo echo Verifying Installation
echo echo ============================================
echo echo.
echo.
echo %%PYTHON%% -c "import sys; print('Python location:', sys.executable)"
echo echo.
echo.
echo echo Testing packages...
echo %%PYTHON%% -c "import pandas; print('pandas OK')"
echo %%PYTHON%% -c "import PyPDF2; print('PyPDF2 OK')"
echo %%PYTHON%% -c "import win32com.client; print('pywin32 OK')"
echo %%PYTHON%% -c "import lxml; print('lxml OK')"
echo.
echo if errorlevel 1 ^(
echo     echo.
echo     echo ERROR: Some packages failed verification
echo     echo Please review the errors above
echo     pause
echo     exit /b 1
echo ^)
echo.
echo echo.
echo echo ============================================
echo echo Creating START_APP.bat
echo echo ============================================
echo.
echo REM Create START_APP.bat with the correct Python path
echo ^(
echo     echo @echo off
echo     echo REM Document Manager V2.3 - Start Application
echo     echo REM Python: %PYTHON_PATH%
echo     echo.
echo     echo echo Starting Document Manager V2.3...
echo     echo echo.
echo     echo "%PYTHON_PATH%" run_v2_3.py
echo     echo if errorlevel 1 ^^^(
echo     echo     echo.
echo     echo     echo ERROR: Application failed to start
echo     echo     echo Check document_manager_v2.3.log for details
echo     echo     pause
echo     echo ^^^)
echo ^) ^> START_APP.bat
echo.
echo echo Created START_APP.bat
echo echo.
echo.
echo echo ============================================
echo echo Installation Complete!
echo echo ============================================
echo echo.
echo echo All packages installed successfully!
echo echo.
echo echo To run the application:
echo echo   1. Double-click START_APP.bat
echo echo   OR
echo echo   2. Run: %%PYTHON%% run_v2_3.py
echo echo.
echo echo ============================================
echo pause
) > "%INSTALLER_FILE%"

echo.
echo ============================================
echo Created: %INSTALLER_FILE%
echo ============================================
echo.
echo User can now run:
echo   %INSTALLER_FILE%
echo.
echo This will:
echo   1. Install all required packages (no admin needed)
echo   2. Create START_APP.bat with correct Python path
echo   3. Verify everything works
echo.
pause
