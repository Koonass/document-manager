@echo off
REM Fix pywin32 installation for Word printing

echo ========================================
echo  Fix pywin32 Installation
echo ========================================
echo.
echo This will install/reinstall pywin32 which is required
echo for folder label printing and printer diagnostics.
echo.
pause

echo.
echo Step 1: Uninstalling old pywin32 (if present)...
echo.
pip uninstall pywin32 -y

echo.
echo Step 2: Installing pywin32...
echo.
pip install pywin32

echo.
echo Step 3: Clearing gen_py cache...
echo.
python -c "import win32com.client as win32; import shutil; import os; path = win32com.gencache.GetGeneratePath(); print(f'Cache: {path}'); shutil.rmtree(path, ignore_errors=True) if os.path.exists(path) else None; print('Cache cleared')"

echo.
echo ========================================
echo  Installation Complete!
echo ========================================
echo.
echo Please restart the Document Manager application.
echo Folder label printing should now work.
echo.
pause
