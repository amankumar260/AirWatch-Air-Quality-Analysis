@echo off
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
  echo Creating Python virtual environment...
  python -m venv .venv
  if errorlevel 1 goto error
)
echo Installing or checking required libraries...
.venv\Scripts\python.exe -m pip install -r requirements.txt
if errorlevel 1 goto error
echo Starting AirWatch dashboard. Keep this window open while using the dashboard.
.venv\Scripts\python.exe -m streamlit run app.py
if errorlevel 1 goto error
goto end
:error
echo Something went wrong. Check that Python is installed and see the error above.
pause
:end
