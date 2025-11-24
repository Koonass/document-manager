@echo off
REM Test printer connectivity and print queue

echo ============================================
echo PRINTER DIAGNOSTIC
echo ============================================
echo.

set PRINTER_NAME=\\vcoloprint\FB-Labels

echo Testing printer: %PRINTER_NAME%
echo.

echo ============================================
echo 1. Checking if printer is accessible...
echo ============================================
ping vcoloprint -n 2
echo.

echo ============================================
echo 2. Listing all installed printers...
echo ============================================
wmic printer get name,printerstatus,workoffline
echo.

echo ============================================
echo 3. Checking print queue for this printer...
echo ============================================
echo Current jobs in queue:
wmic printjob where "name like '%%vcoloprint%%'" get name,jobstatus,document
echo.

echo ============================================
echo 4. Printer details...
echo ============================================
wmic printer where "name='%PRINTER_NAME%'" get name,printerstatus,workoffline,drivername
echo.

echo ============================================
echo 5. Testing print with notepad...
echo ============================================
echo Creating test file...
echo This is a test print > test_print.txt
echo.
echo Sending to printer...
notepad /p test_print.txt
echo.
echo Check if test page printed.
echo If nothing printed, there's a printer connectivity issue.
echo.

pause
