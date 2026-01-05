@echo off
echo Starting FairDeal Backend Server...
echo.
python -m uvicorn app.main:app --reload --port 8000
pause

