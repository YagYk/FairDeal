Write-Host "Starting FairDeal Backend Server..." -ForegroundColor Green
Write-Host ""
python -m uvicorn app.main:app --reload --port 8000

