#!/bin/bash
export PYTHONPATH="${PYTHONPATH}:/app"
cd /app
python init_db.py

uvicorn src.api.main:app --host 0.0.0.0 --port $PORT
