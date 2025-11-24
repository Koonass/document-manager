# Build Portable Package for Document Manager v2.4
# This script downloads portable Python and installs all dependencies

param(
    [string]$PythonVersion = "3.11.9",
    [string]$TargetDir = ".\portable-build"
)

$ErrorActionPreference = "Stop"

Write-Host "=====================================================================" -ForegroundColor Cyan
Write-Host "Document Manager v2.4 - Portable Package Builder" -ForegroundColor Cyan
Write-Host "=====================================================================" -ForegroundColor Cyan
Write-Host ""

# Determine architecture
$arch = if ([Environment]::Is64BitOperatingSystem) { "amd64" } else { "win32" }
Write-Host "[INFO] Detected architecture: $arch" -ForegroundColor Green

# URLs
$pythonUrl = "https://www.python.org/ftp/python/$PythonVersion/python-$PythonVersion-embed-$arch.zip"
$getPipUrl = "https://bootstrap.pypa.io/get-pip.py"

Write-Host ""
Write-Host "[1/7] Creating build directory..." -ForegroundColor Yellow
if (Test-Path $TargetDir) {
    Write-Host "      Build directory exists, cleaning..." -ForegroundColor Gray
    Remove-Item -Path "$TargetDir\python" -Recurse -Force -ErrorAction SilentlyContinue
}
New-Item -ItemType Directory -Path "$TargetDir\python" -Force | Out-Null
Write-Host "      [OK] Build directory ready" -ForegroundColor Green

Write-Host ""
Write-Host "[2/7] Downloading portable Python $PythonVersion..." -ForegroundColor Yellow
$pythonZip = "$TargetDir\python.zip"
try {
    Invoke-WebRequest -Uri $pythonUrl -OutFile $pythonZip -UseBasicParsing
    Write-Host "      [OK] Downloaded: $('{0:N2}' -f ((Get-Item $pythonZip).Length / 1MB)) MB" -ForegroundColor Green
} catch {
    Write-Host "      [ERROR] Failed to download Python!" -ForegroundColor Red
    Write-Host "      URL: $pythonUrl" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "[3/7] Extracting Python..." -ForegroundColor Yellow
try {
    Expand-Archive -Path $pythonZip -DestinationPath "$TargetDir\python" -Force
    Remove-Item $pythonZip
    Write-Host "      [OK] Python extracted" -ForegroundColor Green
} catch {
    Write-Host "      [ERROR] Failed to extract Python!" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "[4/7] Configuring Python (enabling pip and site-packages)..." -ForegroundColor Yellow
$pthFile = Get-ChildItem -Path "$TargetDir\python" -Filter "*._pth" | Select-Object -First 1
if ($pthFile) {
    $content = Get-Content $pthFile.FullName
    # Uncomment the import site line
    $content = $content -replace "^#import site", "import site"
    # Add Lib and Lib\site-packages if not present
    if ($content -notcontains "Lib") {
        $content += "Lib"
    }
    if ($content -notcontains "Lib\site-packages") {
        $content += "Lib\site-packages"
    }
    Set-Content -Path $pthFile.FullName -Value $content
    Write-Host "      [OK] Python configured for packages" -ForegroundColor Green
} else {
    Write-Host "      [WARNING] Could not find ._pth file" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "[5/7] Installing pip..." -ForegroundColor Yellow
try {
    $getPip = "$TargetDir\get-pip.py"
    Invoke-WebRequest -Uri $getPipUrl -OutFile $getPip -UseBasicParsing

    $pythonExe = "$TargetDir\python\python.exe"
    & $pythonExe $getPip --no-warn-script-location 2>&1 | Out-Null
    Remove-Item $getPip

    # Verify pip installed
    $pipCheck = & $pythonExe -m pip --version 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "      [OK] pip installed: $pipCheck" -ForegroundColor Green
    } else {
        throw "pip installation failed"
    }
} catch {
    Write-Host "      [ERROR] Failed to install pip!" -ForegroundColor Red
    Write-Host "      $_" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "[6/7] Installing application dependencies..." -ForegroundColor Yellow
Write-Host "      This may take 2-3 minutes..." -ForegroundColor Gray

$packages = @("PyQt5", "pywin32")
foreach ($package in $packages) {
    Write-Host "      Installing $package..." -ForegroundColor Gray
    try {
        & $pythonExe -m pip install $package --no-warn-script-location --quiet
        if ($LASTEXITCODE -eq 0) {
            Write-Host "      [OK] $package installed" -ForegroundColor Green
        } else {
            throw "Installation failed"
        }
    } catch {
        Write-Host "      [ERROR] Failed to install $package!" -ForegroundColor Red
        exit 1
    }
}

# Post-install for pywin32
Write-Host "      Configuring pywin32..." -ForegroundColor Gray
try {
    & $pythonExe -m pip install --upgrade pywin32 --no-warn-script-location --quiet
    $scriptsPath = "$TargetDir\python\Scripts"
    if (Test-Path "$scriptsPath\pywin32_postinstall.py") {
        & $pythonExe "$scriptsPath\pywin32_postinstall.py" -install -silent 2>&1 | Out-Null
    }
    Write-Host "      [OK] pywin32 configured" -ForegroundColor Green
} catch {
    Write-Host "      [WARNING] pywin32 post-install had issues (may still work)" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "[7/7] Copying application files..." -ForegroundColor Yellow

# Copy source code
if (Test-Path ".\src") {
    Copy-Item -Path ".\src" -Destination "$TargetDir\src" -Recurse -Force
    Write-Host "      [OK] src/ copied" -ForegroundColor Green
} else {
    Write-Host "      [WARNING] src/ folder not found!" -ForegroundColor Yellow
}

# Copy label template
if (Test-Path ".\LABEL TEMPLATE") {
    Copy-Item -Path ".\LABEL TEMPLATE" -Destination "$TargetDir\LABEL TEMPLATE" -Recurse -Force
    Write-Host "      [OK] LABEL TEMPLATE/ copied" -ForegroundColor Green
} else {
    Write-Host "      [WARNING] LABEL TEMPLATE/ folder not found!" -ForegroundColor Yellow
}

# Copy essential files
$filesToCopy = @(
    "run_v2_4.py",
    "setup_new_deployment.py",
    "settings_v2_4_template.json",
    "requirements.txt",
    "START_PORTABLE.bat",
    "SETUP_FOR_NEW_USER.bat",
    "README.md",
    "DEPLOYMENT_README.md",
    "PORTABLE_DEPLOYMENT_GUIDE.md",
    "PORTABLE_QUICK_START.txt"
)

foreach ($file in $filesToCopy) {
    if (Test-Path ".\$file") {
        Copy-Item -Path ".\$file" -Destination "$TargetDir\$file" -Force
        Write-Host "      [OK] $file copied" -ForegroundColor Green
    }
}

# Copy all documentation
Copy-Item -Path ".\*.md" -Destination "$TargetDir\" -Force -ErrorAction SilentlyContinue
Copy-Item -Path ".\*.txt" -Destination "$TargetDir\" -Force -ErrorAction SilentlyContinue

Write-Host ""
Write-Host "=====================================================================" -ForegroundColor Cyan
Write-Host "Portable Package Build Complete!" -ForegroundColor Cyan
Write-Host "=====================================================================" -ForegroundColor Cyan

$buildSize = (Get-ChildItem -Path $TargetDir -Recurse | Measure-Object -Property Length -Sum).Sum / 1MB
Write-Host ""
Write-Host "Build location: $TargetDir" -ForegroundColor Green
Write-Host "Total size: $('{0:N0}' -f $buildSize) MB" -ForegroundColor Green
Write-Host ""
Write-Host "Package contents:" -ForegroundColor White
Write-Host "  [x] Portable Python $PythonVersion" -ForegroundColor Gray
Write-Host "  [x] PyQt5 (GUI framework)" -ForegroundColor Gray
Write-Host "  [x] pywin32 (Word automation)" -ForegroundColor Gray
Write-Host "  [x] Application source code" -ForegroundColor Gray
Write-Host "  [x] Documentation" -ForegroundColor Gray
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "  1. Test: cd $TargetDir && .\START_PORTABLE.bat" -ForegroundColor White
Write-Host "  2. Copy entire '$TargetDir' folder to:" -ForegroundColor White
Write-Host "     - USB drive (E:\DocumentManager)" -ForegroundColor White
Write-Host "     - OneDrive folder" -ForegroundColor White
Write-Host "     - Network share" -ForegroundColor White
Write-Host "  3. Users run: START_PORTABLE.bat" -ForegroundColor White
Write-Host ""
Write-Host "This package is completely self-contained and portable!" -ForegroundColor Green
Write-Host ""
