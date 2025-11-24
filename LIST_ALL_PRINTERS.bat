@echo off
REM ============================================
REM List All Available Printers
REM Document Manager V2.3
REM ============================================

echo ============================================
echo Available Printers on This Computer
echo ============================================
echo.

REM Try to find Python
set PYTHON_PATH=

REM Check common Python locations
for %%P in (
    "python"
    "C:\Users\%USERNAME%\AppData\Local\Programs\Python\Python312\python.exe"
    "C:\Users\%USERNAME%\AppData\Local\Programs\Python\Python311\python.exe"
    "C:\Python312\python.exe"
) do (
    %%P --version >nul 2>&1
    if %errorlevel% equ 0 (
        set PYTHON_PATH=%%P
        goto :found_python
    )
)

echo ERROR: Could not find Python
echo Please install Python from: https://www.python.org/downloads/
pause
exit /b 1

:found_python

REM Create temporary Python script
echo import win32print > temp_list_printers.py
echo print("Installed Printers:") >> temp_list_printers.py
echo print("=" * 70) >> temp_list_printers.py
echo printers = win32print.EnumPrinters(win32print.PRINTER_ENUM_LOCAL ^| win32print.PRINTER_ENUM_CONNECTIONS) >> temp_list_printers.py
echo for i, (flags, desc, name, comment) in enumerate(printers, 1): >> temp_list_printers.py
echo     print(f"{i}. {name}") >> temp_list_printers.py
echo     if comment: >> temp_list_printers.py
echo         print(f"   Comment: {comment}") >> temp_list_printers.py
echo print() >> temp_list_printers.py
echo print("=" * 70) >> temp_list_printers.py
echo default_printer = win32print.GetDefaultPrinter() >> temp_list_printers.py
echo print(f"Default Printer: {default_printer}") >> temp_list_printers.py
echo print("=" * 70) >> temp_list_printers.py

REM Run the script
%PYTHON_PATH% temp_list_printers.py

REM Clean up
del temp_list_printers.py

echo.
echo.
echo Copy this information when troubleshooting printer issues.
echo.
pause
