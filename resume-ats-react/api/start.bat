@echo off
echo Installing Python dependencies...
pip install -r "%~dp0requirements.txt"
if %errorlevel% neq 0 (
    echo Failed to install dependencies.
    exit /b %errorlevel%
)

echo Starting Resume Tailor API on port 8001...
python -m uvicorn api.main:app --host 0.0.0.0 --port 8001 --reload --app-dir "%~dp0.."
