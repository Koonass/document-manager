@echo off
echo.
echo Checking template path...
echo.

set TEMPLATE="C:\Users\jjanney\Contract Lumber\Designers (FB) - General\BISTRACK CONNECTOR\Document Manager\LABEL TEMPLATE\Contract_Lumber_Label_Template.docx"

echo Template path: %TEMPLATE%
echo.

if exist %TEMPLATE% (
    echo ✓ Template found!
    dir %TEMPLATE%
) else (
    echo ❌ Template NOT found at this location
    echo.
    echo Searching for template...
    where /R "C:\Users\jjanney" Contract_Lumber_Label_Template.docx
)

echo.
pause
