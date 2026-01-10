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

# Headers to avoid 403 errors
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}


def scrape_nba_month(season: int, month_slug: str):
    """
    Scrape NBA games for a specific month.
    month_slug: 'january', 'february', etc.
    """
    url = f"{BR_BASE}/leagues/NBA_{season}_games-{month_slug}.html"
    print(f"Fetching {url}...")
    
    try:
        response = requests.get(url, timeout=10, headers=HEADERS)
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
        response = requests.get(url, timeout=10, headers=HEADERS)
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


def scrape_upcoming_days(days=4):
    """
    Scrape NBA games for today and the next N days.
    This matches what Underdog Fantasy shows.
    """
    from datetime import timedelta
    
    print(f"Scraping NBA games for the next {days} days...")
    
    now = datetime.now()
    season = now.year if now.month > 6 else now.year
    
    with Session(engine) as db:
        for day_offset in range(days):
            target_date = now + timedelta(days=day_offset)
            date_str = target_date.strftime('%Y-%m-%d')
            
            # Basketball-Reference uses format: /boxscores/?month=01&day=10&year=2026
            url = f"{BR_BASE}/boxscores/?month={target_date.month:02d}&day={target_date.day:02d}&year={target_date.year}"
            print(f"Fetching games for {date_str}...")
            
            try:
                response = requests.get(url, timeout=10, headers=HEADERS)
                response.raise_for_status()
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Find all game boxes
                game_divs = soup.find_all('div', class_='game_summary')
                print(f"Found {len(game_divs)} games for {date_str}")
                
                for game_div in game_divs:
                    try:
                        # Extract game link
                        link = game_div.find('a', href=True)
                        if not link:
                            continue
                        
                        game_url = BR_BASE + link['href']
                        game_id = link['href'].split('/')[-1].replace('.html', '')
                        
                        # Check if already scraped
                        existing = db.query(NBAGame).filter(NBAGame.game_id == game_id).first()
                        if existing:
                            print(f"  {game_id} already scraped, skipping")
                            continue
                        
                        # Extract teams
                        teams = game_div.find_all('a', itemprop='name')
                        if len(teams) < 2:
                            continue
                        
                        away_team = teams[0].get_text(strip=True)
                        home_team = teams[1].get_text(strip=True)
                        
                        # Extract scores (if game has finished)
                        scores = game_div.find_all('td', class_='right')
                        away_score = None
                        home_score = None
                        if len(scores) >= 2:
                            try:
                                away_score = int(scores[0].get_text(strip=True))
                                home_score = int(scores[1].get_text(strip=True))
                            except:
                                pass  # Game hasn't finished yet
                        
                        # Create game record
                        game = NBAGame(
                            game_id=game_id,
                            date=target_date.date(),
                            home_team=home_team,
                            away_team=away_team,
                            home_score=home_score,
                            away_score=away_score,
                            season=season
                        )
                        db.add(game)
                        print(f"  ✓ Added {away_team} @ {home_team}")
                        
                    except Exception as e:
                        print(f"  Error processing game: {e}")
                        continue
                
                db.commit()
                time.sleep(2)  # Rate limiting
                
            except Exception as e:
                print(f"Error fetching {date_str}: {e}")
                continue
    
    print("✓ Finished scraping upcoming games")


if __name__ == "__main__":
    scrape_current_month()
