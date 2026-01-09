"""Main entry point that imports the FastAPI app from src"""
from src.api.main import app

# This allows uvicorn to find the app
# Run with: uvicorn main:app
