@echo off
echo ============================================================
echo   Document Manager - Single File Installer Builder
echo ============================================================
echo.
echo This will create a single .exe installer file that contains
echo everything needed to install Document Manager.
echo.
echo The process will:
echo   1. Install PyInstaller (if needed)
echo   2. Package all application files
echo   3. Create a single DocumentManager_Installer.exe
echo.
echo This may take several minutes...
echo.
pause
echo.

python create_installer.py

echo.
echo ============================================================
echo Done! Check the output above for the installer location.
echo ============================================================
pause
