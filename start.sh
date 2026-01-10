#!/bin/bash
export PYTHONPATH="/app:${PYTHONPATH}"
cd /app
echo "Initializing database..."
python init_db.py || echo "Database already initialized"
echo "Running NBA scraper..."
# python -c "from src.scrapers.nba import scrape_upcoming_days; scrape_upcoming_days(4)" || echo "Scraper run failed or completed"
echo "Starting API server..."
exec uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}
