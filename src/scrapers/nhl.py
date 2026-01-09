"""NHL scraper - Hockey-Reference.com"""
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from sqlalchemy.orm import Session

def scrape_nhl_data(session: Session, season: int = 2026):
    """Scrape NHL data from Hockey-Reference"""
    try:
        from src.database.models import NHLGame, NHLTeam, NHLPlayer, NHLPlayerStats
        print(f"NHL scraper initialized for season {season}")
        return {"status": "success", "message": "NHL scraper framework ready", "games_scraped": 0}
    except Exception as e:
        return {"status": "error", "message": str(e)}
