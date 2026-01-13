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
    """Get sample NBA endpoint data"""
    return {
        "player": "LeBron James",
        "recent_games": [
            {"date": "2026-01-06", "points": 28, "rebounds": 8, "assists": 11},
            {"date": "2026-01-04", "points": 31, "rebounds": 7, "assists": 9},
            {"date": "2026-01-02", "points": 25, "rebounds": 6, "assists": 12}
        ]
    }



# Data endpoints for Lovable frontend
@app.get("/nba/games")
def get_nba_games(limit: int = 100):
    """Get recent NBA games"""
    try:
        from src.database.connection import engine
        from src.database.models import NBAGame
        from sqlalchemy.orm import Session
        
        with Session(engine) as session:
            games = session.query(NBAGame).limit(limit).all()
            return {"status": "success", "count": len(games), "games": [{
                "id": g.id,
                "date": g.date.isoformat() if g.date else None,
                "home_team": g.home_team,
                "away_team": g.away_team,
                "home_score": g.home_score,
                "away_score": g.away_score
            } for g in games]}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/nba/teams")
def get_nba_teams():
    """Get all NBA teams"""
    try:
        from src.database.connection import engine
        from src.database.models import NBATeam
        from sqlalchemy.orm import Session
        
        with Session(engine) as session:
            teams = session.query(NBATeam).all()
            return {"status": "success", "count": len(teams), "teams": [{
                "id": t.id,
                "name": t.name,
                "abbreviation": t.abbreviation
            } for t in teams]}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/nba/players")
def get_nba_players(limit: int = 100):
    """Get NBA players"""
    try:
        from src.database.connection import engine
        from sqlalchemy.orm import Session
               from src.database.models import NBAPlayer
        
        with Session(engine) as session:
            players = session.query(NBAPlayer).limit(limit).all()
return {"status": "success", "count": len(players), "players": [{
                "id": p.id,
                "name": p.name,
                "team": p.team,
                "position": p.position
            } for p in players]}
    except Exception as e:
        return {"status": "error", "message": str(e)}


@app.post("/admin/init-db")
def init_database():
    """Initialize database tables"""
    try:
        from src.database.connection import engine
        from src.database.models import Base
        Base.metadata.create_all(engine)
        return {"status": "success", "message": "Database tables created"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.post("/admin/scrape-nba")
def scrape_nba_data():
    """Trigger NBA scraper for the next 4 days"""    try:    
        from src.scrapers.nba import scrape_nba_month
        from datetime import datetime
        from dateutil.relativedelta import relativedelta
    
            # Scrape past 4 days of data
            now = datetime.now()
            month_map = {
                            1: 'january', 2: 'february', 3: 'march', 4: 'april',
                5: 'may', 6: 'june', 7: 'july', 8: 'august',
                9: 'september', 10: 'october', 11: 'november', 12: 'december'
            }
    
            for i in range(4):
                target_date = now+- relativedelta(days=i)
                month_slug = month_map[target_date.month]
                target_season = target_date.year if target_date.month > 6 else target_date.year
                scrape_nba_month(target_season, month_slug)
    
                return {"status": "success", "message": "NBA data scraped"}
    except Exception as e:
        return {"status": "error", "message": str(e)}
