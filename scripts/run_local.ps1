# ==============================================================================
# AegisGov AI: Windows PowerShell Local Runner
# Automatically verifies virtualenv and starts the full-stack server
# ==============================================================================

Write-Host "======================================================" -ForegroundColor Cyan
Write-Host " 🚀 Starting AegisGov AI Sovereign Governance Platform" -ForegroundColor Cyan
Write-Host "======================================================" -ForegroundColor Cyan
Write-Host ""

$RootDir = Split-Path -Parent $PSScriptRoot
Set-Location $RootDir

# 1. Verify Python
if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Host "❌ Python is not installed or not in PATH!" -ForegroundColor Red
    Write-Host "Please install Python 3.9+ from https://www.python.org/downloads/"
    exit 1
}

# 2. Check / Create Virtualenv
$VenvActivate = Join-Path $RootDir "backend\venv\Scripts\Activate.ps1"
if (-not (Test-Path $VenvActivate)) {
    Write-Host "📦 Creating Python virtual environment in backend\venv..." -ForegroundColor Yellow
    python -m venv backend\venv
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Failed to create virtual environment." -ForegroundColor Red
        exit 1
    }
    Write-Host "📦 Installing dependencies from backend\requirements.txt..." -ForegroundColor Yellow
    & "$RootDir\backend\venv\Scripts\python.exe" -m pip install --upgrade pip
    & "$RootDir\backend\venv\Scripts\python.exe" -m pip install -r backend\requirements.txt
}

# 3. Ensure .env exists
$EnvFile = Join-Path $RootDir ".env"
$EnvExample = Join-Path $RootDir ".env.example"
if (-not (Test-Path $EnvFile) -and (Test-Path $EnvExample)) {
    Write-Host "📋 Copying .env.example to .env..." -ForegroundColor Yellow
    Copy-Item $EnvExample $EnvFile
}

Write-Host ""
Write-Host "======================================================" -ForegroundColor Green
Write-Host " ✅ Environment ready! Starting local server..." -ForegroundColor Green
Write-Host " 🌐 Access UI at: http://localhost:8080" -ForegroundColor White
Write-Host " 🏥 Health check: http://localhost:8080/api/health" -ForegroundColor White
Write-Host " (Press Ctrl+C to stop)" -ForegroundColor Gray
Write-Host "======================================================" -ForegroundColor Green
Write-Host ""

& "$RootDir\backend\venv\Scripts\python.exe" -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8080 --reload
