# PowerShell script to add Tesseract and Poppler to PATH
# Run this script as Administrator for system-wide changes, or run normally for user-level changes

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "OCR PATH Configuration Script" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if running as Administrator
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if (-not $isAdmin) {
    Write-Host "Note: Not running as Administrator. Changes will be for current user only." -ForegroundColor Yellow
    Write-Host "For system-wide changes, run PowerShell as Administrator and run this script again." -ForegroundColor Yellow
    Write-Host ""
}

# Find Tesseract
Write-Host "1. Searching for Tesseract OCR..." -ForegroundColor Green
$tesseractPaths = @(
    "C:\Program Files\Tesseract-OCR",
    "C:\Program Files (x86)\Tesseract-OCR",
    "$env:LOCALAPPDATA\Tesseract-OCR",
    "$env:ProgramFiles\Tesseract-OCR"
)

$tesseractFound = $false
$tesseractPath = $null

foreach ($path in $tesseractPaths) {
    if (Test-Path "$path\tesseract.exe") {
        $tesseractPath = $path
        $tesseractFound = $true
        Write-Host "   [OK] Found Tesseract at: $tesseractPath" -ForegroundColor Green
        break
    }
}

if (-not $tesseractFound) {
    Write-Host "   [X] Tesseract not found in common locations." -ForegroundColor Red
    Write-Host "   Please install Tesseract from: https://github.com/UB-Mannheim/tesseract/wiki" -ForegroundColor Yellow
    Write-Host "   Or run: choco install tesseract" -ForegroundColor Yellow
} else {
    # Add Tesseract to PATH
    $currentPath = [Environment]::GetEnvironmentVariable('Path', 'User')
    if ($currentPath -notlike "*$tesseractPath*") {
        $newPath = $currentPath + ';' + $tesseractPath
        [Environment]::SetEnvironmentVariable('Path', $newPath, 'User')
        Write-Host "   [OK] Added Tesseract to User PATH" -ForegroundColor Green
    } else {
        Write-Host "   [OK] Tesseract already in PATH" -ForegroundColor Green
    }
}

Write-Host ""

# Find Poppler
Write-Host "2. Searching for Poppler..." -ForegroundColor Green

# Check common Poppler locations
$popplerBasePaths = @(
    "C:\Program Files",
    "C:\Program Files (x86)",
    $env:LOCALAPPDATA,
    $env:ProgramFiles,
    "C:\"
)

$popplerFound = $false
$popplerBinPath = $null

# Search for poppler directories
foreach ($basePath in $popplerBasePaths) {
    if (Test-Path $basePath) {
        $popplerDirs = Get-ChildItem -Path $basePath -Directory -Filter "poppler*" -ErrorAction SilentlyContinue
        foreach ($dir in $popplerDirs) {
            # Check Library\bin first (common for Windows releases)
            $libBinPath = Join-Path $dir.FullName "Library\bin"
            if (Test-Path "$libBinPath\pdftoppm.exe") {
                $popplerBinPath = $libBinPath
                $popplerFound = $true
                Write-Host "   [OK] Found Poppler at: $popplerBinPath" -ForegroundColor Green
                break
            }
            # Check bin folder
            $binPath = Join-Path $dir.FullName "bin"
            if (Test-Path "$binPath\pdftoppm.exe") {
                $popplerBinPath = $binPath
                $popplerFound = $true
                Write-Host "   [OK] Found Poppler at: $popplerBinPath" -ForegroundColor Green
                break
            }
        }
        if ($popplerFound) { break }
    }
}

if (-not $popplerFound) {
    Write-Host "   [X] Poppler not found in common locations." -ForegroundColor Red
    Write-Host "   Please install Poppler from: https://github.com/oschwartz10612/poppler-windows/releases/" -ForegroundColor Yellow
    Write-Host "   Or run: choco install poppler" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "   After installing Poppler, add the 'bin' folder to PATH." -ForegroundColor Yellow
    Write-Host "   Example: If Poppler is at C:\poppler, add C:\poppler\bin to PATH" -ForegroundColor Yellow
} else {
    # Add Poppler to PATH
    $currentPath = [Environment]::GetEnvironmentVariable('Path', 'User')
    if ($currentPath -notlike "*$popplerBinPath*") {
        $newPath = $currentPath + ';' + $popplerBinPath
        [Environment]::SetEnvironmentVariable('Path', $newPath, 'User')
        Write-Host "   [OK] Added Poppler to User PATH" -ForegroundColor Green
    } else {
        Write-Host "   [OK] Poppler already in PATH" -ForegroundColor Green
    }
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Summary" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

if ($tesseractFound -and $popplerFound) {
    Write-Host "[OK] Both Tesseract and Poppler are configured!" -ForegroundColor Green
    Write-Host ""
    Write-Host "IMPORTANT: Close and reopen your terminal/PowerShell for PATH changes to take effect." -ForegroundColor Yellow
    Write-Host ""
    Write-Host "To verify, run:" -ForegroundColor Cyan
    Write-Host "  tesseract --version" -ForegroundColor White
    Write-Host "  pdftoppm -h" -ForegroundColor White
} elseif ($tesseractFound) {
    Write-Host "[OK] Tesseract is configured" -ForegroundColor Green
    Write-Host "[X] Poppler needs to be installed and added to PATH" -ForegroundColor Red
} elseif ($popplerFound) {
    Write-Host "[X] Tesseract needs to be installed and added to PATH" -ForegroundColor Red
    Write-Host "[OK] Poppler is configured" -ForegroundColor Green
} else {
    Write-Host "[X] Both Tesseract and Poppler need to be installed" -ForegroundColor Red
}

Write-Host ""
