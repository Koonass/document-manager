@echo off
echo ====================================================================
echo CSV Validation Test - Document Manager v2.4
echo ====================================================================
echo.
echo This will test the new CSV validation and cleanup features
echo.

python test_csv_features.py

echo.
echo Test complete. Press any key to exit...
pause > nul
