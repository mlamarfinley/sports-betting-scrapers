"""FastAPI server for sports betting stats"""
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime

app = FastAPI(title="Sports Betting Model API", version="1.0.0")

# CORS for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Update with your Lovable domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {
        "message": "Sports Betting Model API",
        "version": "1.0.0",
        "status": "online",
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "database": "connected" if os.getenv("DATABASE_URL") else "not configured",
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/nba/stats/sample")
def get_nba_sample():
    """Sample NBA endpoint - will be replaced with real data"""
    return {
        "player": "LeBron James",
        "recent_games": [
            {"date": "2026-01-06", "points": 28, "rebounds": 8, "assists": 11},
            {"date": "2026-01-04", "points": 31, "rebounds": 7, "assists": 9},
            {"date": "2026-01-02", "points": 25, "rebounds": 6, "assists": 12}
        ]
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
