"""League of Legends scraper using gol.gg"""
import re
import time
import requests
import pandas as pd
from bs4 import BeautifulSoup
from datetime import datetime
from sqlalchemy.orm import Session
from src.database.connection import engine
from src.database.models import LoLGame, LoLPlayerStat

GOL_BASE = "https://gol.gg"

def scrape_lol_tournament(tournament_id: str, season: str):
    """
    Scrape LoL games for a specific tournament.
    tournament_id: e.g., 'LCS', 'LEC', 'LCK', 'LPL'
    season: e.g., '2026-spring'
    """
    url = f"{GOL_BASE}/tournament/tournament-matchlist/{tournament_id}/"
    print(f"Fetching {url}...")
    
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find all match links
        match_table = soup.find('table', {'class': 'table_list'})
        if not match_table:
            print(f"No matches found for {tournament_id}")
            return
        
        match_links = match_table.find_all('a', href=re.compile(r'/game/stats/'))
        game_ids = [link['href'].split('/')[-2] for link in match_links]
        
        print(f"Found {len(game_ids)} games for {tournament_id} {season}")
        
        with Session(engine) as db:
            for game_id in game_ids:
                scrape_single_lol_game(game_id, tournament_id, season, db)
                time.sleep(2)  # Rate limiting
    
    except Exception as e:
        print(f"Error scraping {tournament_id}: {e}")

def scrape_single_lol_game(game_id: str, tournament: str, season: str, db: Session):
    """
    Scrape a single LoL game's stats.
    """
    # Check if already scraped
    from src.database.models import LoLGame
    existing = db.query(LoLGame).filter(LoLGame.game_id == game_id).first()
    if existing:
        print(f"  {game_id} already scraped, skipping")
        return
    
    try:
        url = f"{GOL_BASE}/game/stats/{game_id}/page-game/"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extract game metadata
        title = soup.find('h1')
        if not title:
            print(f"  No title found for {game_id}")
            return
        
        # Parse teams from title (e.g., "Team A vs Team B")
        title_text = title.text.strip()
        teams = re.split(r'\s+vs\s+', title_text, flags=re.IGNORECASE)
        if len(teams) < 2:
            print(f"  Could not parse teams from: {title_text}")
            return
        
        team_a = teams[0].strip()
        team_b = teams[1].strip()
        
        # Get winner from score or result
        score_divs = soup.find_all('div', {'class': 'score'})
        winner = None
        if len(score_divs) >= 2:
            score_a = score_divs[0].text.strip()
            score_b = score_divs[1].text.strip()
            if score_a > score_b:
                winner = team_a
            else:
                winner = team_b
        
        # Extract date
        date_elem = soup.find('div', {'class': 'game-date'})
        game_date = datetime.now().date()
        if date_elem:
            try:
                game_date = datetime.strptime(date_elem.text.strip(), '%Y-%m-%d').date()
            except:
                pass
        
        # Save game
        game = LoLGame(
            game_id=game_id,
            date=game_date,
            tournament=tournament,
            season=season,
            team_a=team_a,
            team_b=team_b,
            winner=winner
        )
        db.add(game)
        db.commit()
        
        # Extract player stats
        stats_table = soup.find('table', {'class': 'table_list playersInfosLine'})
        if stats_table:
            rows = stats_table.find_all('tr')[1:]  # Skip header
            
            for row in rows:
                cells = row.find_all('td')
                if len(cells) < 10:
                    continue
                
                player_name = cells[1].text.strip()
                champion = cells[2].text.strip()
                team = cells[0].text.strip()
                
                # Extract stats (KDA, CS, gold, damage)
                kills = safe_int(cells[3].text.strip())
                deaths = safe_int(cells[4].text.strip())
                assists = safe_int(cells[5].text.strip())
                cs = safe_int(cells[6].text.strip())
                gold = safe_int(cells[7].text.strip())
                damage = safe_int(cells[8].text.strip())
                
                player_stat = LoLPlayerStat(
                    game_id=game_id,
                    player_name=player_name,
                    champion=champion,
                    team=team,
                    kills=kills,
                    deaths=deaths,
                    assists=assists,
                    cs=cs,
                    gold=gold,
                    damage=damage
                )
                db.add(player_stat)
        
        db.commit()
        print(f"  ✓ Scraped {game_id}: {team_a} vs {team_b}")
    
    except Exception as e:
        db.rollback()
        print(f"  Error scraping {game_id}: {e}")

def safe_int(value):
    """Convert to int, return None if fails"""
    try:
        # Remove commas and convert
        cleaned = str(value).replace(',', '').strip()
        return int(float(cleaned)) if cleaned else None
    except:
        return None

def scrape_current_tournaments():
    """Scrape current major tournaments"""
    tournaments = ['LCS', 'LEC', 'LCK', 'LPL']
    season = '2026-spring'
    
    for tournament in tournaments:
        scrape_lol_tournament(tournament, season)
        time.sleep(5)  # Rate limiting between tournaments

if __name__ == "__main__":
    scrape_current_tournaments()
