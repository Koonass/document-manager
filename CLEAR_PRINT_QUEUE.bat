@echo off
REM Clear stuck print jobs

echo ============================================
echo CLEAR PRINT QUEUE
echo ============================================
echo.

echo This will clear all stuck print jobs.
echo.
set /p CONFIRM="Continue? (yes/no): "

if /i not "%CONFIRM%"=="yes" if /i not "%CONFIRM%"=="y" (
    echo Cancelled.
    pause
    exit /b 0
)

echo.
echo Stopping print spooler...
net stop spooler

echo.
echo Clearing print queue files...
del /Q /F /S "%systemroot%\System32\spool\PRINTERS\*.*"

echo.
echo Starting print spooler...
net start spooler

echo.
echo ============================================
echo Print queue cleared!
echo ============================================
echo.
echo Try printing again.
echo.
pause
