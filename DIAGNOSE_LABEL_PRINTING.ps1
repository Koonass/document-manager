# PowerShell version of diagnostic script
# Alternative to .bat file if needed

Write-Host "====================================================================" -ForegroundColor Cyan
Write-Host "FOLDER LABEL PRINTING DIAGNOSTIC" -ForegroundColor Cyan
Write-Host "====================================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "This will check your system configuration for label printing issues."
Write-Host "The results will be saved to: diagnostic_report.txt"
Write-Host ""
Read-Host "Press Enter to continue"

# Check for Python
try {
    $pythonVersion = python --version 2>&1
    Write-Host "Python found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "ERROR: Python is not installed or not in PATH" -ForegroundColor Red
    Write-Host "Please install Python or run from the portable setup" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

# Run the diagnostic script
Write-Host ""
Write-Host "Running diagnostics..." -ForegroundColor Yellow
Write-Host ""

# Run and capture output
python diagnose_label_printing.py 2>&1 | Tee-Object -FilePath diagnostic_report.txt

Write-Host ""
Write-Host "====================================================================" -ForegroundColor Green
Write-Host "Diagnostic complete!" -ForegroundColor Green
Write-Host "Results saved to: diagnostic_report.txt" -ForegroundColor Green
Write-Host "====================================================================" -ForegroundColor Green
Write-Host ""
Write-Host "Please share the diagnostic_report.txt file for troubleshooting." -ForegroundColor Cyan
Write-Host ""
Read-Host "Press Enter to exit"
