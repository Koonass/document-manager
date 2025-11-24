@echo off
REM ============================================
REM Diagnose Python Installation Issues
REM ============================================

echo ============================================
echo Python Installation Diagnostic
echo ============================================
echo.

echo [1] Checking which Python 'python' command uses...
echo ----------------------------------------
where python
python --version
echo.

echo [2] Checking which Python 'python3' command uses...
echo ----------------------------------------
where python3
python3 --version
echo.

echo [3] Checking which Python 'py' launcher uses...
echo ----------------------------------------
where py
py --version
py -0
echo.

echo [4] Checking which pip is being used...
echo ----------------------------------------
where pip
pip --version
echo.

echo [5] Checking if packages are installed in current Python...
echo ----------------------------------------
echo Testing with: python
python -c "import sys; print('Python path:', sys.executable)"
python -c "import pandas; print('pandas: OK')" 2>nul || echo pandas: NOT FOUND
python -c "import PyPDF2; print('PyPDF2: OK')" 2>nul || echo PyPDF2: NOT FOUND
python -c "import win32com.client; print('pywin32: OK')" 2>nul || echo pywin32: NOT FOUND
python -c "import lxml; print('lxml: OK')" 2>nul || echo lxml: NOT FOUND
echo.

echo [6] Checking if packages are installed in python3...
echo ----------------------------------------
echo Testing with: python3
python3 -c "import sys; print('Python path:', sys.executable)"
python3 -c "import pandas; print('pandas: OK')" 2>nul || echo pandas: NOT FOUND
python3 -c "import PyPDF2; print('PyPDF2: OK')" 2>nul || echo PyPDF2: NOT FOUND
python3 -c "import win32com.client; print('pywin32: OK')" 2>nul || echo pywin32: NOT FOUND
python3 -c "import lxml; print('lxml: OK')" 2>nul || echo lxml: NOT FOUND
echo.

echo [7] Finding all Python installations on C: drive...
echo ----------------------------------------
echo This may take a moment...
where /R C:\ python.exe 2>nul | findstr /V ".zip"
echo.

echo ============================================
echo DIAGNOSIS COMPLETE
echo ============================================
echo.
echo Please review the output above to identify:
echo 1. Which Python has the packages installed
echo 2. Which Python START_APP.bat is trying to use
echo 3. Any mismatches between pip and python commands
echo.
pause
