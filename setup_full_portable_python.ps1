# Setup Full Portable Python with tkinter
# This downloads and configures a complete Python installation

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "  Setting Up Full Portable Python (with tkinter)" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

$ErrorActionPreference = "Stop"

# Clean up old embeddable version
if (Test-Path "python-embedded") {
    Write-Host "[1/5] Removing old embeddable Python..." -ForegroundColor Yellow
    Remove-Item "python-embedded" -Recurse -Force
    Write-Host "      Old version removed" -ForegroundColor Green
}

# Download full Python installer
Write-Host ""
Write-Host "[2/5] Downloading Python 3.12.0 full installer..." -ForegroundColor Yellow
$url = "https://www.python.org/ftp/python/3.12.0/python-3.12.0-amd64.exe"
$installer = "python-3.12.0-installer.exe"

if (-not (Test-Path $installer)) {
    try {
        Invoke-WebRequest -Uri $url -OutFile $installer -UseBasicParsing
        $sizeMB = [math]::Round((Get-Item $installer).Length / 1MB, 2)
        Write-Host "      Downloaded: $sizeMB MB" -ForegroundColor Green
    } catch {
        Write-Host "      ERROR: Failed to download Python" -ForegroundColor Red
        Write-Host "      $_" -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "      Installer already downloaded" -ForegroundColor Green
}

# Install Python portably (no registry, no PATH)
Write-Host ""
Write-Host "[3/5] Installing Python to python-portable folder..." -ForegroundColor Yellow
Write-Host "      This may take 2-3 minutes..." -ForegroundColor Gray

# Remove old portable if exists
if (Test-Path "python-portable") {
    Remove-Item "python-portable" -Recurse -Force
}

# Install Python in portable mode
# /quiet = silent install
# InstallAllUsers=0 = just for this folder
# PrependPath=0 = don't modify PATH
# Include_test=0 = skip tests
# TargetDir = where to install
$installArgs = @(
    "/quiet",
    "InstallAllUsers=0",
    "PrependPath=0",
    "Include_test=0",
    "Include_doc=0",
    "Include_dev=0",
    "Include_pip=1",
    "Include_tcltk=1",
    "TargetDir=$PWD\python-portable"
)

try {
    $process = Start-Process -FilePath $installer -ArgumentList $installArgs -Wait -PassThru

    if ($process.ExitCode -eq 0) {
        Write-Host "      Python installed successfully" -ForegroundColor Green
    } else {
        Write-Host "      ERROR: Installation failed with code $($process.ExitCode)" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "      ERROR: $_" -ForegroundColor Red
    exit 1
}

# Verify tkinter is available
Write-Host ""
Write-Host "[4/5] Verifying tkinter..." -ForegroundColor Yellow
try {
    $tkinterTest = & ".\python-portable\python.exe" -c "import tkinter; print('tkinter OK')" 2>&1
    if ($tkinterTest -match "tkinter OK") {
        Write-Host "      tkinter is available!" -ForegroundColor Green
    } else {
        Write-Host "      WARNING: tkinter test produced: $tkinterTest" -ForegroundColor Yellow
    }
} catch {
    Write-Host "      ERROR: tkinter not available" -ForegroundColor Red
    exit 1
}

# Install required packages
Write-Host ""
Write-Host "[5/5] Installing required packages..." -ForegroundColor Yellow
Write-Host "      This may take 2-3 minutes..." -ForegroundColor Gray

try {
    & ".\python-portable\python.exe" -m pip install --quiet --upgrade pip
    & ".\python-portable\python.exe" -m pip install pandas PyPDF2 pywin32 lxml
    Write-Host "      All packages installed" -ForegroundColor Green
} catch {
    Write-Host "      ERROR: Package installation failed" -ForegroundColor Red
    Write-Host "      $_" -ForegroundColor Red
    exit 1
}

# Test everything
Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "  Testing Portable Python Installation" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan

$testScript = @"
import sys
print(f'Python {sys.version.split()[0]}')

packages = []
try:
    import tkinter
    packages.append('[OK] tkinter')
except Exception as e:
    packages.append(f'[FAIL] tkinter: {e}')

try:
    import pandas
    packages.append(f'[OK] pandas {pandas.__version__}')
except Exception as e:
    packages.append(f'[FAIL] pandas: {e}')

try:
    import PyPDF2
    packages.append(f'[OK] PyPDF2 {PyPDF2.__version__}')
except Exception as e:
    packages.append(f'[FAIL] PyPDF2: {e}')

try:
    import win32com.client
    packages.append('[OK] pywin32')
except Exception as e:
    packages.append(f'[FAIL] pywin32: {e}')

try:
    import lxml
    packages.append(f'[OK] lxml {lxml.__version__}')
except Exception as e:
    packages.append(f'[FAIL] lxml: {e}')

for pkg in packages:
    print(pkg)
"@

$testScript | & ".\python-portable\python.exe" -

# Check size
Write-Host ""
$size = (Get-ChildItem -Path "python-portable" -Recurse | Measure-Object -Property Length -Sum).Sum / 1MB
Write-Host "Portable Python size: $([math]::Round($size, 2)) MB" -ForegroundColor Cyan

# Cleanup installer
Write-Host ""
Write-Host "Cleaning up installer..." -ForegroundColor Yellow
Remove-Item $installer -Force
Write-Host "Done!" -ForegroundColor Green

Write-Host ""
Write-Host "============================================================" -ForegroundColor Green
Write-Host "  SUCCESS! Full Portable Python Ready" -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Green
Write-Host ""
Write-Host "Location: python-portable\" -ForegroundColor White
Write-Host "Includes: tkinter, pip, and all required packages" -ForegroundColor White
Write-Host ""
Write-Host "Next: Update STARTUP_PORTABLE.bat to use python-portable" -ForegroundColor Yellow
Write-Host ""
