@echo off
REM Local development startup script (Windows)

if not exist .env (
    echo Copy .env.example to .env and set GROQ_API_KEY
    copy .env.example .env
)

call python -m venv venv 2>nul
call venv\Scripts\activate
pip install -r requirements.txt -q

echo Building vector index...
python scripts/build_index.py

echo Starting API on http://localhost:8000
start "FinSolve API" cmd /k "venv\Scripts\activate && uvicorn app.api.main:app --host 0.0.0.0 --port 8000"

timeout /t 5 /nobreak >nul

echo Starting Streamlit on http://localhost:8501
streamlit run streamlit_app/app.py
