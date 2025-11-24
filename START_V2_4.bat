@echo off
REM Change to the directory where this batch file is located
cd /d "%~dp0"

echo ====================================================================
echo Starting Document Manager V2.4 - BisTrack CSV Management
echo ====================================================================
echo.

python run_v2_4.py

echo.
echo Application closed. Press any key to exit...
pause > nul
