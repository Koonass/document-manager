@echo off
REM ============================================
REM Create Clean Distribution Package
REM Document Manager V2.3
REM ============================================

echo ============================================
echo Creating Distribution Package
echo ============================================
echo.

set DIST_FOLDER=Document_Manager_v2.3_Distribution
set SOURCE_FOLDER=%CD%

REM Remove old distribution folder if exists
if exist "%DIST_FOLDER%" (
    echo Removing old distribution folder...
    rmdir /S /Q "%DIST_FOLDER%"
)

echo Creating distribution folder structure...
mkdir "%DIST_FOLDER%"
mkdir "%DIST_FOLDER%\src"
mkdir "%DIST_FOLDER%\LABEL TEMPLATE"

echo.
echo Copying core files...

REM Copy root files
copy "run_v2_3.py" "%DIST_FOLDER%\" >nul
copy "requirements.txt" "%DIST_FOLDER%\" >nul
copy "INSTALL.bat" "%DIST_FOLDER%\" >nul
copy "INSTALLATION_INSTRUCTIONS.md" "%DIST_FOLDER%\" >nul
copy "diagnose_label_printing.py" "%DIST_FOLDER%\" >nul
copy "FIX_BOOKMARK_MISMATCH.py" "%DIST_FOLDER%\" >nul
copy "FOLDER_PRINTING_GUIDE.md" "%DIST_FOLDER%\" >nul
copy "LABEL_PRINTING_TROUBLESHOOTING.md" "%DIST_FOLDER%\" >nul
copy "CLEAN_INSTALLATION_PACKAGE.md" "%DIST_FOLDER%\" >nul

echo Copying source files...

REM Copy src folder files
copy "src\__init__.py" "%DIST_FOLDER%\src\" >nul
copy "src\main_v2_3.py" "%DIST_FOLDER%\src\" >nul
copy "src\pdf_processor.py" "%DIST_FOLDER%\src\" >nul
copy "src\enhanced_database_v2.py" "%DIST_FOLDER%\src\" >nul
copy "src\relationship_manager.py" "%DIST_FOLDER%\src\" >nul
copy "src\statistics_calendar_widget.py" "%DIST_FOLDER%\src\" >nul
copy "src\enhanced_expanded_view.py" "%DIST_FOLDER%\src\" >nul
copy "src\enhanced_search_view.py" "%DIST_FOLDER%\src\" >nul
copy "src\archive_manager.py" "%DIST_FOLDER%\src\" >nul
copy "src\word_template_processor.py" "%DIST_FOLDER%\src\" >nul
copy "src\error_logger.py" "%DIST_FOLDER%\src\" >nul
copy "src\verify_template.py" "%DIST_FOLDER%\src\" >nul

echo Copying template files...

REM Copy template
copy "LABEL TEMPLATE\Contract_Lumber_Label_Template.docx" "%DIST_FOLDER%\LABEL TEMPLATE\" >nul

echo.
echo Creating README_FIRST.txt...

(
echo Document Manager V2.3 - Installation Package
echo =============================================
echo.
echo QUICK START:
echo 1. Double-click INSTALL.bat to install required packages
echo 2. Double-click START_APP.bat to run the application
echo.
echo For detailed instructions, see INSTALLATION_INSTRUCTIONS.md
echo.
echo System Requirements:
echo - Windows 7 or later
echo - Python 3.8+ installed
echo - Microsoft Word ^(for folder label printing^)
echo.
echo Questions? Check the log file: document_manager_v2.3.log
echo.
echo FILES INCLUDED:
echo - run_v2_3.py              : Application launcher
echo - INSTALL.bat              : Automated installation
echo - requirements.txt         : Python dependencies
echo - src/                     : Application source code
echo - LABEL TEMPLATE/          : Word template for labels
echo.
echo SETUP STEPS:
echo 1. Run INSTALL.bat
echo 2. Run START_APP.bat
echo 3. Configure file paths in Settings
echo 4. ^(Optional^) Configure printer settings
echo.
echo For troubleshooting:
echo - Run diagnose_label_printing.py
echo - Check FOLDER_PRINTING_GUIDE.md
echo - Review INSTALLATION_INSTRUCTIONS.md
) > "%DIST_FOLDER%\README_FIRST.txt"

echo.
echo ============================================
echo Distribution Package Created!
echo ============================================
echo.
echo Location: %CD%\%DIST_FOLDER%
echo.
echo Package contents:
dir /B "%DIST_FOLDER%"
echo.
echo Source files:
dir /B "%DIST_FOLDER%\src"
echo.
echo Template:
dir /B "%DIST_FOLDER%\LABEL TEMPLATE"
echo.
echo ============================================
echo Next Steps:
echo ============================================
echo 1. Test the installation on a clean machine
echo 2. Create a ZIP file for distribution:
echo    - Right-click folder ^> Send to ^> Compressed folder
echo 3. Share the ZIP with end users
echo.
echo Distribution package is ready at:
echo %CD%\%DIST_FOLDER%
echo.
pause
