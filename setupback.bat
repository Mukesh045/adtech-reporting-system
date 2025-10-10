@echo off
python -m venv venv
call venv\Scripts\activate
pip install -r backend\requirements.txt
echo Setup complete. Run .\start_backend.bat to start the backend.
