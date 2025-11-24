@echo off
REM Diagnostic tool for folder label printing issues
REM Run this and share the output for troubleshooting

echo ====================================================================
echo FOLDER LABEL PRINTING DIAGNOSTIC
echo ====================================================================
echo.
echo This will check your system configuration for label printing issues.
echo The results will be saved to: diagnostic_report.txt
echo.
pause

REM Try to find Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python or run from the portable setup
    pause
    exit /b 1
)

REM Run the diagnostic script and save output
echo Running diagnostics...
echo.

python diagnose_label_printing.py > diagnostic_report.txt 2>&1

echo.
echo ====================================================================
echo Diagnostic complete!
echo Results saved to: diagnostic_report.txt
echo ====================================================================
echo.
echo Opening the report...
echo.

REM Display the report
type diagnostic_report.txt

echo.
echo ====================================================================
echo Please share the diagnostic_report.txt file for troubleshooting.
echo ====================================================================
echo.
pause
