@echo off
REM ============================================
REM Install for user: jjanney
REM Python location: C:\Users\jjanney\AppData\Local\Programs\Python\Python312
REM NO ADMIN RIGHTS REQUIRED
REM ============================================

echo ============================================
echo Document Manager V2.3 - Installation
echo ============================================
echo.
echo Installing for user: jjanney
echo Python: C:\Users\jjanney\AppData\Local\Programs\Python\Python312
echo.

REM Set the Python path
set PYTHON="C:\Users\jjanney\AppData\Local\Programs\Python\Python312\python.exe"

REM Verify Python exists
if not exist %PYTHON% (
    echo ERROR: Python not found at expected location!
    echo.
    echo Please check the path. If Python is in a different location,
    echo edit this file and update the PYTHON variable.
    pause
    exit /b 1
)

echo Found Python:
%PYTHON% --version
echo.

echo ============================================
echo Step 1: Upgrading pip (no admin needed)
echo ============================================
%PYTHON% -m pip install --upgrade pip --user
echo.

echo ============================================
echo Step 2: Installing pandas
echo ============================================
%PYTHON% -m pip install pandas --user
echo.

echo ============================================
echo Step 3: Installing PyPDF2
echo ============================================
%PYTHON% -m pip install PyPDF2 --user
echo.

echo ============================================
echo Step 4: Installing pywin32
echo ============================================
%PYTHON% -m pip install pywin32 --user
echo.

echo ============================================
echo Step 5: Installing lxml
echo ============================================
%PYTHON% -m pip install lxml --user
echo.

echo ============================================
echo Step 6: Configuring pywin32
echo ============================================
%PYTHON% -m pywin32_postinstall -install
echo.

echo ============================================
echo Verifying Installation
echo ============================================
echo.

%PYTHON% -c "import sys; print('Python location:', sys.executable)"
echo.

echo Testing packages...
%PYTHON% -c "import pandas; print('✓ pandas OK')"
%PYTHON% -c "import PyPDF2; print('✓ PyPDF2 OK')"
%PYTHON% -c "import win32com.client; print('✓ pywin32 OK')"
%PYTHON% -c "import lxml; print('✓ lxml OK')"

if errorlevel 1 (
    echo.
    echo ERROR: Some packages failed verification
    echo Please review the errors above
    pause
    exit /b 1
)

echo.
echo ============================================
echo Creating START_APP.bat
echo ============================================

REM Create START_APP.bat with the correct Python path
(
    echo @echo off
    echo REM Document Manager V2.3 - Start Application
    echo REM Python: C:\Users\jjanney\AppData\Local\Programs\Python\Python312
    echo.
    echo echo Starting Document Manager V2.3...
    echo echo.
    echo "C:\Users\jjanney\AppData\Local\Programs\Python\Python312\python.exe" run_v2_3.py
    echo if errorlevel 1 ^(
    echo     echo.
    echo     echo ERROR: Application failed to start
    echo     echo Check document_manager_v2.3.log for details
    echo     pause
    echo ^)
) > START_APP.bat

echo Created START_APP.bat
echo.

echo ============================================
echo Installation Complete!
echo ============================================
echo.
echo All packages installed successfully!
echo.
echo To run the application:
echo   1. Double-click START_APP.bat
echo   OR
echo   2. Run: %PYTHON% run_v2_3.py
echo.
echo ============================================
pause
