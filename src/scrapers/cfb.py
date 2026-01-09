"""College Football scraper using Pro-Football-Reference"""
import re
import time
import requests
import pandas as pd
from bs4 import BeautifulSoup
from datetime import datetime
from sqlalchemy.orm import Session
from src.database.connection import engine
from src.database.models import CFBGame, CFBPlayerStat

PFR_BASE = "https://www.pro-football-reference.com"
CFB_BASE = "https://www.sports-reference.com/cfb"

def scrape_cfb_week(year: int, week: int):
    """
    Scrape college football games for a specific week.
    year: e.g., 2025, 2026
    week: 1-15 (regular season) or 16+ (bowl games)
    """
    url = f"{CFB_BASE}/years/{year}-schedule.html"
    print(f"Fetching {url}...")
    
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find the schedule table
        schedule_table = soup.find('table', {'id': 'schedule'})
        if not schedule_table:
            print(f"No schedule found for {year}")
            return
        
        # Parse the table
        df = pd.read_html(str(schedule_table))[0]
        
        # Filter for specific week
        if 'Wk' in df.columns:
            week_games = df[df['Wk'] == week]
        else:
            print("Week column not found, processing all games")
            week_games = df
        
        print(f"Found {len(week_games)} games for week {week} of {year}")
        
        with Session(engine) as db:
            for _, game_row in week_games.iterrows():
                try:
                    # Extract game info
                    date_str = game_row.get('Date', '')
                    winner = game_row.get('Winner', game_row.get('W', ''))
                    winner_pts = safe_int(game_row.get('Pts', game_row.get('PtsW', '')))
                    loser = game_row.get('Loser', game_row.get('L', ''))
                    loser_pts = safe_int(game_row.get('Pts.1', game_row.get('PtsL', '')))
                    
                    # Parse date
                    try:
                        game_date = datetime.strptime(date_str, '%Y-%m-%d').date()
                    except:
                        game_date = datetime.now().date()
                    
                    # Create game_id
                    game_id = f"{year}_{week}_{winner}_{loser}".replace(' ', '_')
                    
                    # Check if already scraped
                    existing = db.query(CFBGame).filter(CFBGame.game_id == game_id).first()
                    if existing:
                        continue
                    
                    # Determine home/away (if available)
                    notes = str(game_row.get('Notes', ''))
                    if '@' in notes:
                        # Away game for winner
                        home_team = loser
                        away_team = winner
                        home_score = loser_pts
                        away_score = winner_pts
                    else:
                        # Home game for winner or neutral
                        home_team = winner
                        away_team = loser
                        home_score = winner_pts
                        away_score = loser_pts
                    
                    # Save game
                    game = CFBGame(
                        game_id=game_id,
                        date=game_date,
                        year=year,
                        week=week,
                        home_team=home_team,
                        away_team=away_team,
                        home_score=home_score,
                        away_score=away_score,
                        winner=winner
                    )
                    db.add(game)
                    
                except Exception as e:
                    print(f"  Error processing game: {e}")
                    continue
            
            db.commit()
            print(f"  ✓ Scraped {len(week_games)} games for week {week}")
    
    except Exception as e:
        print(f"Error scraping week {week} of {year}: {e}")

def scrape_cfb_game_stats(game_url: str, game_id: str, db: Session):
    """
    Scrape individual game box score for player stats.
    """
    try:
        response = requests.get(game_url, timeout=10)
        response.raise_for_status()
        html = response.text
        
        # CFB Reference may hide tables in comments like NBA
        html = html.replace('<!--', '').replace('-->', '')
        soup = BeautifulSoup(html, 'html.parser')
        
        # Find passing, rushing, receiving tables
        stat_tables = soup.find_all('table', {'class': re.compile(r'stats_table')})
        
        for table in stat_tables:
            table_id = table.get('id', '')
            
            # Determine stat type
            if 'passing' in table_id:
                stat_type = 'passing'
            elif 'rushing' in table_id:
                stat_type = 'rushing'
            elif 'receiving' in table_id:
                stat_type = 'receiving'
            elif 'defense' in table_id:
                stat_type = 'defense'
            else:
                continue
            
            # Parse table
            df = pd.read_html(str(table), header=1)[0]
            df = df[df['Player'].notna()]
            df = df[~df['Player'].str.contains('Player|Team Total', na=False)]
            
            # Extract team from table context
            team_header = table.find_previous('h2')
            team = team_header.text.strip() if team_header else 'Unknown'
            
            for _, row in df.iterrows():
                player_name = row.get('Player', '')
                
                if stat_type == 'passing':
                    stat = CFBPlayerStat(
                        game_id=game_id,
                        player_name=player_name,
                        team=team,
                        stat_type='passing',
                        pass_cmp=safe_int(row.get('Cmp')),
                        pass_att=safe_int(row.get('Att')),
                        pass_yds=safe_int(row.get('Yds')),
                        pass_td=safe_int(row.get('TD')),
                        pass_int=safe_int(row.get('Int'))
                    )
                elif stat_type == 'rushing':
                    stat = CFBPlayerStat(
                        game_id=game_id,
                        player_name=player_name,
                        team=team,
                        stat_type='rushing',
                        rush_att=safe_int(row.get('Att')),
                        rush_yds=safe_int(row.get('Yds')),
                        rush_td=safe_int(row.get('TD'))
                    )
                elif stat_type == 'receiving':
                    stat = CFBPlayerStat(
                        game_id=game_id,
                        player_name=player_name,
                        team=team,
                        stat_type='receiving',
                        rec_tgt=safe_int(row.get('Tgt')),
                        rec_rec=safe_int(row.get('Rec')),
                        rec_yds=safe_int(row.get('Yds')),
                        rec_td=safe_int(row.get('TD'))
                    )
                elif stat_type == 'defense':
                    stat = CFBPlayerStat(
                        game_id=game_id,
                        player_name=player_name,
                        team=team,
                        stat_type='defense',
                        def_tackles=safe_int(row.get('Tkl')),
                        def_sacks=safe_float(row.get('Sk')),
                        def_int=safe_int(row.get('Int'))
                    )
                else:
                    continue
                
                db.add(stat)
        
        db.commit()
        print(f"  ✓ Scraped player stats for {game_id}")
    
    except Exception as e:
        db.rollback()
        print(f"  Error scraping stats for {game_id}: {e}")

def safe_int(value):
    """Convert to int, return None if fails"""
    try:
        return int(float(value)) if pd.notna(value) else None
    except:
        return None

def safe_float(value):
    """Convert to float, return None if fails"""
    try:
        return float(value) if pd.notna(value) else None
    except:
        return None

def scrape_current_cfb_week():
    """Scrape current week's college football games"""
    now = datetime.now()
    # CFB season is Aug-Jan, determine year and approximate week
    if now.month >= 8:
        year = now.year
        # Rough estimate: week 1 starts ~Sept 1
        week = max(1, (now - datetime(now.year, 9, 1)).days // 7)
    else:
        year = now.year - 1
        week = 15  # Bowl season
    
    scrape_cfb_week(year, week)

if __name__ == "__main__":
    scrape_current_cfb_week()
