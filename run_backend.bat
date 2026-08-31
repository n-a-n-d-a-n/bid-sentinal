@echo off
echo ===================================================
echo     PROCUREX — Starting Backend & Bootstrapping
echo ===================================================
call .venv\Scripts\activate.bat
cd backend
python scripts/sih_bootstrap.py
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
pause
