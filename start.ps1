# PowerEdu-AI Platform Startup Script
# Encoding: UTF-8 with BOM

# Set encoding for console output
$OutputEncoding = [System.Text.Encoding]::UTF8
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

# Clear screen and show banner
Clear-Host
Write-Host ""
Write-Host "================================" -ForegroundColor Cyan
Write-Host "   PowerEdu-AI Platform v1.0   " -ForegroundColor Green
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""

# Check Python environment
Write-Host "[1/6] Checking Python..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "SUCCESS: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "ERROR: Python not found. Please install Python 3.8+" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Check Node.js environment
Write-Host "[2/6] Checking Node.js..." -ForegroundColor Yellow
try {
    $nodeVersion = node --version 2>&1
    Write-Host "SUCCESS: Node.js $nodeVersion" -ForegroundColor Green
} catch {
    Write-Host "ERROR: Node.js not found. Please install Node.js 18.15+" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Install Python dependencies
Write-Host "[3/6] Installing Python dependencies..." -ForegroundColor Yellow
pip install -r requirements.txt -q
Write-Host "SUCCESS: Python dependencies installed" -ForegroundColor Green

# Initialize Django database
Write-Host "[4/6] Initializing Django database..." -ForegroundColor Yellow
Set-Location backend
python manage.py migrate --verbosity=0
python manage.py init_data
Write-Host "SUCCESS: Database initialized" -ForegroundColor Green

# Start Django backend
Write-Host "[5/6] Starting Django backend..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$(Get-Location)'; python manage.py runserver" -WindowStyle Normal
Write-Host "SUCCESS: Backend service started" -ForegroundColor Green

Set-Location ..

# Start React frontend
Write-Host "[6/6] Starting React frontend..." -ForegroundColor Yellow
Set-Location frontend
if (!(Test-Path "node_modules")) {
    Write-Host "  Installing frontend dependencies..." -ForegroundColor Gray
    npm install --silent
}
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$(Get-Location)'; npm run dev" -WindowStyle Normal
Write-Host "SUCCESS: Frontend service started" -ForegroundColor Green

Set-Location ..

# Wait for services to start
Write-Host ""
Write-Host "Waiting for services to start..." -ForegroundColor Gray
Start-Sleep -Seconds 3

# Display completion info
Write-Host ""
Write-Host "================================" -ForegroundColor Green
Write-Host "        SUCCESS!               " -ForegroundColor Green  
Write-Host "================================" -ForegroundColor Green
Write-Host ""
Write-Host "Access URLs:" -ForegroundColor Cyan
Write-Host "   Main Platform: http://localhost:5173" -ForegroundColor White
Write-Host "   AI Prediction: http://localhost:5173/prediction" -ForegroundColor White
Write-Host "   Backend API: http://localhost:8000" -ForegroundColor White
Write-Host "   Admin Panel: http://localhost:8000/admin" -ForegroundColor White
Write-Host "   API Docs: http://localhost:8000/api/docs" -ForegroundColor White
Write-Host ""
Write-Host "Admin Account:" -ForegroundColor Cyan
Write-Host "   Username: admin" -ForegroundColor White
Write-Host "   Password: 123456" -ForegroundColor White
Write-Host ""
Write-Host "AI prediction features are fully integrated!" -ForegroundColor Yellow
Write-Host ""

Read-Host "Press Enter to exit"
