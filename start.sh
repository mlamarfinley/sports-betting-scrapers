#!/bin/bash
export PYTHONPATH="/app:${PYTHONPATH}"
cd /app
echo "Initializing database..."
python init_db.py || echo "Database already initialized"
echo "Starting API server..."
exec uvicorn src.api.main:app --host 0.0.0.0 --port ${PORT:-8000}
