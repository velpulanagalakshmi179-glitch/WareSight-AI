@echo off
python -m pip install -r requirements.txt
python -m uvicorn backend.app:app --reload
