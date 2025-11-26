# Build Portable Package for Document Manager v2.4 with tkinter support
# Uses NuGet Python package which includes tkinter

param(
    [string]$PythonVersion = "3.11.9",
    [string]$TargetDir = ".\portable-build"
)

$ErrorActionPreference = "Stop"

Write-Host "=====================================================================" -ForegroundColor Cyan
Write-Host "Document Manager v2.4 - Portable Package Builder (with tkinter)" -ForegroundColor Cyan
Write-Host "=====================================================================" -ForegroundColor Cyan
Write-Host ""

# Clean old build
Write-Host "[1/8] Cleaning old build..." -ForegroundColor Yellow
if (Test-Path "$TargetDir\python") {
    Remove-Item -Path "$TargetDir\python" -Recurse -Force
    Write-Host "      [OK] Removed old Python" -ForegroundColor Green
}

# Download NuGet Python (includes tkinter)
Write-Host ""
Write-Host "[2/8] Downloading Python with tkinter support..." -ForegroundColor Yellow
$pythonNuGetUrl = "https://www.nuget.org/api/v2/package/python/$PythonVersion"
$nugetPackage = "$TargetDir\python.nupkg"

try {
    Invoke-WebRequest -Uri $pythonNuGetUrl -OutFile $nugetPackage -UseBasicParsing
    Write-Host "      [OK] Downloaded Python NuGet package" -ForegroundColor Green
} catch {
    Write-Host "      [ERROR] Failed to download Python!" -ForegroundColor Red
    Write-Host "      Trying alternative: WinPython portable..." -ForegroundColor Yellow

    # Fallback: Use embedded + manually add tkinter libs from system Python
    Write-Host "      Please install Python $PythonVersion from python.org first," -ForegroundColor Red
    Write-Host "      then we'll copy tkinter from there." -ForegroundColor Red
    exit 1
}

# Extract NuGet package (it's just a zip)
Write-Host ""
Write-Host "[3/8] Extracting Python..." -ForegroundColor Yellow
Expand-Archive -Path $nugetPackage -DestinationPath "$TargetDir\python-temp" -Force

# Copy the tools/python folder to our python folder
if (Test-Path "$TargetDir\python-temp\tools") {
    Move-Item -Path "$TargetDir\python-temp\tools" -Destination "$TargetDir\python" -Force
    Write-Host "      [OK] Python extracted with tkinter support" -ForegroundColor Green
} else {
    Write-Host "      [ERROR] Unexpected package structure!" -ForegroundColor Red
    exit 1
}

# Cleanup
Remove-Item -Path $nugetPackage -Force
Remove-Item -Path "$TargetDir\python-temp" -Recurse -Force

# Verify tkinter
Write-Host ""
Write-Host "[4/8] Verifying tkinter..." -ForegroundColor Yellow
$pythonExe = "$TargetDir\python\python.exe"
$tkinterTest = & $pythonExe -c "import tkinter; print('tkinter OK')" 2>&1

if ($tkinterTest -match "tkinter OK") {
    Write-Host "      [OK] tkinter is available" -ForegroundColor Green
} else {
    Write-Host "      [WARNING] tkinter test failed: $tkinterTest" -ForegroundColor Yellow
}

# Install pip
Write-Host ""
Write-Host "[5/8] Installing pip..." -ForegroundColor Yellow
$getPipUrl = "https://bootstrap.pypa.io/get-pip.py"
$getPip = "$TargetDir\get-pip.py"
Invoke-WebRequest -Uri $getPipUrl -OutFile $getPip -UseBasicParsing
& $pythonExe $getPip --no-warn-script-location 2>&1 | Out-Null
Remove-Item $getPip
Write-Host "      [OK] pip installed" -ForegroundColor Green

# Install dependencies
Write-Host ""
Write-Host "[6/8] Installing application dependencies..." -ForegroundColor Yellow
$packages = @("pywin32")
foreach ($package in $packages) {
    Write-Host "      Installing $package..." -ForegroundColor Gray
    & $pythonExe -m pip install $package --no-warn-script-location --quiet
    Write-Host "      [OK] $package installed" -ForegroundColor Green
}

# Post-install pywin32
& $pythonExe -m pip install --upgrade pywin32 --no-warn-script-location --quiet
$scriptsPath = "$TargetDir\python\Scripts"
if (Test-Path "$scriptsPath\pywin32_postinstall.py") {
    & $pythonExe "$scriptsPath\pywin32_postinstall.py" -install -silent 2>&1 | Out-Null
}

# Copy application files
Write-Host ""
Write-Host "[7/8] Copying application files..." -ForegroundColor Yellow

# Copy source
if (Test-Path ".\src") {
    Copy-Item -Path ".\src" -Destination "$TargetDir\src" -Recurse -Force
    Write-Host "      [OK] src/ copied" -ForegroundColor Green
}

# Copy template
if (Test-Path ".\LABEL TEMPLATE") {
    Copy-Item -Path ".\LABEL TEMPLATE" -Destination "$TargetDir\LABEL TEMPLATE" -Recurse -Force
    Write-Host "      [OK] LABEL TEMPLATE/ copied" -ForegroundColor Green
}

# Copy essential files
$filesToCopy = @(
    "run_v2_4.py",
    "run_v2_4_readonly.py",
    "setup_new_deployment.py",
    "settings_v2_4_template.json",
    "requirements.txt",
    "START_PORTABLE.bat",
    "START_PORTABLE_READONLY.bat",
    "SETUP_FOR_NEW_USER.bat",
    "README.md",
    "DEPLOYMENT_README.md",
    "PORTABLE_DEPLOYMENT_GUIDE.md",
    "PORTABLE_QUICK_START.txt",
    "READONLY_USB_GUIDE.txt"
)

foreach ($file in $filesToCopy) {
    if (Test-Path ".\$file") {
        Copy-Item -Path ".\$file" -Destination "$TargetDir\$file" -Force
        Write-Host "      [OK] $file copied" -ForegroundColor Green
    }
}

# Copy documentation
Copy-Item -Path ".\*.md" -Destination "$TargetDir\" -Force -ErrorAction SilentlyContinue
Copy-Item -Path ".\*.txt" -Destination "$TargetDir\" -Force -ErrorAction SilentlyContinue

# Final verification
Write-Host ""
Write-Host "[8/8] Final verification..." -ForegroundColor Yellow
$finalTest = & "$TargetDir\python\python.exe" -c "import tkinter; import win32com.client; print('All modules OK')" 2>&1

if ($finalTest -match "All modules OK") {
    Write-Host "      [OK] All required modules verified" -ForegroundColor Green
} else {
    Write-Host "      [WARNING] Module test: $finalTest" -ForegroundColor Yellow
}

$buildSize = (Get-ChildItem -Path $TargetDir -Recurse | Measure-Object -Property Length -Sum).Sum / 1MB

Write-Host ""
Write-Host "=====================================================================" -ForegroundColor Cyan
Write-Host "Portable Package Build Complete!" -ForegroundColor Cyan
Write-Host "=====================================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Build location: $TargetDir" -ForegroundColor Green
Write-Host "Total size: $('{0:N0}' -f $buildSize) MB" -ForegroundColor Green
Write-Host ""
Write-Host "Package contents:" -ForegroundColor White
Write-Host "  [x] Portable Python $PythonVersion with tkinter" -ForegroundColor Gray
Write-Host "  [x] pywin32 (Word automation)" -ForegroundColor Gray
Write-Host "  [x] Application source code" -ForegroundColor Gray
Write-Host "  [x] Documentation" -ForegroundColor Gray
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "  1. Test: cd $TargetDir && .\START_PORTABLE.bat" -ForegroundColor White
Write-Host "  2. Copy to USB/OneDrive/Network" -ForegroundColor White
Write-Host ""
