# Download Python Embeddable Package
Write-Host "Downloading Python 3.12 embeddable package..." -ForegroundColor Cyan

$url = "https://www.python.org/ftp/python/3.12.0/python-3.12.0-embed-amd64.zip"
$output = "python-3.12.0-embed-amd64.zip"

try {
    Invoke-WebRequest -Uri $url -OutFile $output -UseBasicParsing

    if (Test-Path $output) {
        $sizeMB = [math]::Round((Get-Item $output).Length / 1MB, 2)
        Write-Host "Download complete! Size: $sizeMB MB" -ForegroundColor Green

        # Extract
        Write-Host "`nExtracting to python-embedded folder..." -ForegroundColor Cyan
        if (Test-Path "python-embedded") {
            Remove-Item "python-embedded" -Recurse -Force
        }
        Expand-Archive -Path $output -DestinationPath "python-embedded" -Force
        Write-Host "Extraction complete!" -ForegroundColor Green

        # Cleanup zip
        Remove-Item $output
        Write-Host "`nPortable Python ready in python-embedded folder" -ForegroundColor Green

    } else {
        Write-Host "Download failed!" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "Error: $_" -ForegroundColor Red
    exit 1
}
