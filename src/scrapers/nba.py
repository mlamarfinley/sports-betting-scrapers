"""NBA scraper using Basketball-Reference"""

import re
import time
import requests
import pandas as pd
from bs4 import BeautifulSoup
from datetime import datetime, date
from sqlalchemy.orm import Session
from src.database.connection import engine
from src.database.models import NBAGame, NBAPlayerStat

BR_BASE = "https://www.basketball-reference.com"


def scrape_nba_month(season: int, month_slug: str):
    """
    Scrape NBA games for a specific month.
    month_slug: 'january', 'february', etc.
    """
    url = f"{BR_BASE}/leagues/NBA_{season}_games-{month_slug}.html"
    print(f"Fetching {url}...")
    
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find all box score links
        links = soup.select('td[data-stat="box_score_text"] a')
        game_urls = [BR_BASE + a['href'] for a in links]
        
        print(f"Found {len(game_urls)} games for {season} {month_slug}")
        
        with Session(engine) as db:
            for url in game_urls:
                scrape_single_game(url, season, db)
                time.sleep(3)  # Rate limiting
                
    except Exception as e:
        print(f"Error scraping {season} {month_slug}: {e}")


def scrape_single_game(url: str, season: int, db: Session):
    """
    Scrape a single NBA game's box score.
    """
    game_id = url.rstrip('/').split('/')[-1].replace('.html', '')
    
    # Check if already scraped
    existing = db.query(NBAGame).filter(NBAGame.game_id == game_id).first()
    if existing:
        print(f"  {game_id} already scraped, skipping")
        return
    
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        html = response.text
        
        # Basketball-Reference hides tables in comments
        html = html.replace('<!--', '').replace('-->', '')
        soup = BeautifulSoup(html, 'html.parser')
        
        # Extract game metadata
        scorebox = soup.find('div', {'class': 'scorebox'})
        if not scorebox:
            print(f"  No scorebox found for {game_id}")
            return
        
        teams = scorebox.find_all('div', recursive=False)
        if len(teams) < 2:
            print(f"  Could not parse teams for {game_id}")
            return
        
        away_team = teams[0].find('a').text if teams[0].find('a') else teams[0].find('strong').text
        home_team = teams[1].find('a').text if teams[1].find('a') else teams[1].find('strong').text
        
        scores = scorebox.find_all('div', {'class': 'score'})
        away_score = int(scores[0].text) if len(scores) > 0 and scores[0].text.strip() else None
        home_score = int(scores[1].text) if len(scores) > 1 and scores[1].text.strip() else None
        
        # Extract date
        meta = soup.find('div', {'class': 'scorebox_meta'})
        date_str = meta.find('div').text if meta else game_id[:8]
        game_date = datetime.strptime(game_id[:8], '%Y%m%d').date()
        
        # Save game
        game = NBAGame(
            game_id=game_id,
            date=game_date,
            home_team=home_team,
            away_team=away_team,
            home_score=home_score,
            away_score=away_score,
            season=season
        )
        db.add(game)
        db.commit()
        
        # Extract player stats
        tables = soup.find_all('table', {'id': re.compile(r'box-.*-game-basic')})
        
        for table in tables:
            team_abbr = table.get('id', '').split('-')[1]
            df = pd.read_html(str(table), header=1)[0]
            
            # Clean dataframe
            df = df[df['Player'] != 'Player']  # Remove header rows
            df = df[df['Player'].notna()]  # Remove empty rows
            df = df[~df['Player'].str.contains('Reserves|Did Not Play', na=False)]
            
            for _, row in df.iterrows():
                player_stat = NBAPlayerStat(
                    game_id=game_id,
                    player_name=row.get('Player', ''),
                    team=team_abbr,
                    minutes=str(row.get('MP', '')),
                    points=safe_int(row.get('PTS')),
                    rebounds=safe_int(row.get('TRB')),
                    assists=safe_int(row.get('AST')),
                    steals=safe_int(row.get('STL')),
                    blocks=safe_int(row.get('BLK')),
                    turnovers=safe_int(row.get('TOV')),
                    fg_made=safe_int(row.get('FG')),
                    fg_attempted=safe_int(row.get('FGA')),
                    three_made=safe_int(row.get('3P')),
                    three_attempted=safe_int(row.get('3PA')),
                    ft_made=safe_int(row.get('FT')),
                    ft_attempted=safe_int(row.get('FTA'))
                )
                db.add(player_stat)
        
        db.commit()
        print(f"  ✓ Scraped {game_id}: {away_team} @ {home_team}")
        
    except Exception as e:
        db.rollback()
        print(f"  Error scraping {game_id}: {e}")


def safe_int(value):
    """Convert to int, return None if fails"""
    try:
        return int(float(value)) if pd.notna(value) else None
    except:
        return None


def scrape_current_month():
    """Scrape current month's games"""
    now = datetime.now()
    season = now.year if now.month > 6 else now.year
    month_slug = now.strftime('%B').lower()
    scrape_nba_month(season, month_slug)


if __name__ == "__main__":
    scrape_current_month()
