# PowerShell launcher for printer diagnostics tool
# Run this on your work machine to configure printers

Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host " Document Manager - Printer Setup" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# Try to find Python
$pythonCmd = $null

# Method 1: Check if python is in PATH
Write-Host "Looking for Python installation..." -ForegroundColor Yellow

$pythonInPath = Get-Command python -ErrorAction SilentlyContinue
if ($pythonInPath) {
    $pythonCmd = "python"
    Write-Host "✓ Found Python in PATH" -ForegroundColor Green
}

# Method 2: Check common installation locations
if (-not $pythonCmd) {
    $commonLocations = @(
        "C:\Python312\python.exe",
        "C:\Python311\python.exe",
        "C:\Python310\python.exe",
        "C:\Python39\python.exe",
        "C:\Python38\python.exe",
        "$env:LOCALAPPDATA\Programs\Python\Python312\python.exe",
        "$env:LOCALAPPDATA\Programs\Python\Python311\python.exe",
        "$env:LOCALAPPDATA\Programs\Python\Python310\python.exe",
        "$env:LOCALAPPDATA\Programs\Python\Python39\python.exe",
        "C:\Program Files\Python312\python.exe",
        "C:\Program Files\Python311\python.exe",
        "C:\Program Files\Python310\python.exe"
    )

    foreach ($location in $commonLocations) {
        if (Test-Path $location) {
            $pythonCmd = $location
            Write-Host "✓ Found Python at: $location" -ForegroundColor Green
            break
        }
    }
}

# Method 3: Try py launcher
if (-not $pythonCmd) {
    $pyLauncher = Get-Command py -ErrorAction SilentlyContinue
    if ($pyLauncher) {
        $pythonCmd = "py"
        Write-Host "✓ Found Python launcher (py.exe)" -ForegroundColor Green
    }
}

# If still not found, error
if (-not $pythonCmd) {
    Write-Host ""
    Write-Host "✗ ERROR: Python not found!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please install Python or locate your Python installation." -ForegroundColor Yellow
    Write-Host ""
    Write-Host "To find Python, try running in Command Prompt:" -ForegroundColor Yellow
    Write-Host "  where python" -ForegroundColor White
    Write-Host "  py --version" -ForegroundColor White
    Write-Host ""
    Write-Host "Then edit this script and set the path manually:" -ForegroundColor Yellow
    Write-Host '  $pythonCmd = "C:\Your\Python\Path\python.exe"' -ForegroundColor White
    Write-Host ""
    Write-Host "See: MANUAL_RUN_INSTRUCTIONS.txt for more help" -ForegroundColor Cyan
    Write-Host ""
    Read-Host "Press Enter to exit"
    exit 1
}

# Run diagnostics tool
Write-Host ""
Write-Host "Starting printer diagnostics tool..." -ForegroundColor Yellow
Write-Host ""

try {
    & $pythonCmd printer_diagnostics.py

    if ($LASTEXITCODE -ne 0) {
        Write-Host ""
        Write-Host "✗ ERROR: Failed to start diagnostics tool" -ForegroundColor Red
        Write-Host ""
        Write-Host "Possible issues:" -ForegroundColor Yellow
        Write-Host "  - Missing Python dependencies" -ForegroundColor White
        Write-Host ""
        Write-Host "Try running:" -ForegroundColor Yellow
        Write-Host "  $pythonCmd -m pip install -r requirements.txt" -ForegroundColor White
        Write-Host ""
        Read-Host "Press Enter to exit"
        exit 1
    }
}
catch {
    Write-Host ""
    Write-Host "✗ ERROR: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host ""
    Write-Host "See: MANUAL_RUN_INSTRUCTIONS.txt for help" -ForegroundColor Cyan
    Write-Host ""
    Read-Host "Press Enter to exit"
    exit 1
}
