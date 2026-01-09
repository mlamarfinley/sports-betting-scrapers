#!/bin/bash
export PYTHONPATH="${PYTHONPATH}:/app"
cd /app
uvicorn src.api.main:app --host 0.0.0.0 --port $PORT
