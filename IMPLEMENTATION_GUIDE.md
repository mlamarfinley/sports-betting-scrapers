# Complete Implementation Guide: Sports Betting Model - Railway + Scrapers

## Current Status
✅ **Railway project**: sports-betting-model with Postgres database (empty)
✅ **GitHub repo**: mlamarfinley/sports-betting-scrapers
✅ **Dependencies**: requirements.txt created

---

## Architecture Overview

```
Data Sources (Basketball-Reference, FBref, etc.)
    ↓ scrapers/
    ↓
Postgres on Railway
    ↓ api/
    ↓
Lovable Dashboard (frontend)
```

---

## Project Structure

```
sports-betting-scrapers/
├── requirements.txt          ✅ Created
├── .env.example              # Template for DATABASE_URL
├── railway.json              # Railway deployment config
├── Procfile                  # Worker + API processes
├── alembic.ini               # DB migrations config
├── alembic/
│   └── versions/
│       └── 001_init_schema.py
├── src/
│   ├── database/
│   │   ├── __init__.py
│   │   ├── connection.py     # SQLAlchemy engine
│   │   └── models.py         # Table definitions
│   ├── scrapers/
│   │   ├── __init__.py
│   │   ├── nba.py            # Basketball-Reference scraper
│   │   ├── nfl.py            # Pro-Football-Reference
│   │   ├── nhl.py            # Hockey-Reference
│   │   ├── soccer.py         # FBref scraper
│   │   ├── tennis.py         # ATP/WTA scraper
│   │   ├── lol.py            # gol.gg scraper
│   │   ├── cs2.py            # Bo3.gg CS2
│   │   ├── dota2.py          # Bo3.gg Dota2
│   │   └── cod.py            # Breaking Point CDL
│   ├── api/
│   │   ├── __init__.py
│   │   ├── main.py           # FastAPI app
│   │   └── endpoints/
│   │       ├── nba.py
│   │       ├── nfl.py
│   │       └── ...
│   └── workers/
│       ├── scheduler.py      # APScheduler cron jobs
│       └── run_scrapers.py   # Entry point
└── tests/
    └── test_scrapers.py
```

---

## Step 1: Database Schema

Create **alembic/versions/001_init_schema.py**:

```python
"""Initialize sports betting schema"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = '001'
down_revision = None

def upgrade():
    # NBA
    op.create_table(
        'nba_games',
        sa.Column('game_id', sa.String(20), primary_key=True),
        sa.Column('date', sa.Date, nullable=False),
        sa.Column('home_team', sa.String(50)),
        sa.Column('away_team', sa.String(50)),
        sa.Column('home_score', sa.Integer),
        sa.Column('away_score', sa.Integer),
        sa.Column('season', sa.Integer),
        sa.Column('scraped_at', sa.DateTime(timezone=True), server_default=sa.func.now())
    )
    
    op.create_table(
        'nba_player_stats',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('game_id', sa.String(20), sa.ForeignKey('nba_games.game_id')),
        sa.Column('player_name', sa.String(100)),
        sa.Column('team', sa.String(50)),
        sa.Column('minutes', sa.String(10)),
        sa.Column('points', sa.Integer),
        sa.Column('rebounds', sa.Integer),
        sa.Column('assists', sa.Integer),
        sa.Column('steals', sa.Integer),
        sa.Column('blocks', sa.Integer),
        sa.Column('turnovers', sa.Integer),
        sa.Column('fg_made', sa.Integer),
        sa.Column('fg_attempted', sa.Integer),
        sa.Column('three_made', sa.Integer),
        sa.Column('three_attempted', sa.Integer),
        sa.Column('ft_made', sa.Integer),
        sa.Column('ft_attempted', sa.Integer),
    )

    # Repeat similar pattern for NFL, NHL, Soccer, esports tables...

def downgrade():
    op.drop_table('nba_player_stats')
    op.drop_table('nba_games')
```

---

## Step 2: NBA Scraper (Basketball-Reference)

Create **src/scrapers/nba.py**:

```python
import re
import requests
import pandas as pd
from bs4 import BeautifulSoup
from datetime import datetime
from sqlalchemy.orm import Session

BR_BASE = "https://www.basketball-reference.com"

def scrape_nba_boxscores(season: int, month: str, db: Session):
    """
    Scrape NBA box scores for given season/month.
    month: "january", "february", etc.
    """
    url = f"{BR_BASE}/leagues/NBA_{season}_games-{month}.html"
    html = requests.get(url, timeout=10).text
    soup = BeautifulSoup(html, 'html.parser')
    
    # Find all game links
    links = soup.select('td[data-stat="box_score_text"] a')
    game_urls = [BR_BASE + a['href'] for a in links]
    
    print(f"Found {len(game_urls)} games for {season} {month}")
    
    for game_url in game_urls:
        scrape_single_game(game_url, season, db)
        time.sleep(3)  # Respect rate limits

def scrape_single_game(url: str, season: int, db: Session):
    """
    Scrape one game's box score and insert into DB.
    """
    html = requests.get(url, timeout=10).text
    # Basketball-Reference hides tables in HTML comments
    html = html.replace('<!--', '').replace('-->', '')
    soup = BeautifulSoup(html, 'html.parser')
    
    # Extract game_id from URL (e.g., .../boxscores/202501010LAL.html)
    game_id = url.split('/')[-1].replace('.html', '')
    
    # Find basic box score tables
    tables = soup.find_all('table', {'id': re.compile(r'box-.*-game-basic')})
    
    for table in tables:
        df = pd.read_html(str(table), header=1)[0]
        df = df[df['Player'] != 'Player']  # Remove header rows
        df['game_id'] = game_id
        df['season'] = season
        
        # Insert into nba_player_stats
        df.to_sql('nba_player_stats', db.connection(), if_exists='append', index=False)
    
    print(f"✓ Scraped {game_id}")
```

---

## Step 3: Worker / Scheduler

Create **src/workers/scheduler.py**:

```python
from apscheduler.schedulers.blocking import BlockingScheduler
from datetime import datetime
from src.scrapers import nba, nfl, nhl, soccer, tennis, lol, cs2, dota2, cod
from src.database.connection import get_db

scheduler = BlockingScheduler(timezone="America/New_York")

@scheduler.scheduled_job('cron', hour=2, minute=0)
def scrape_nba_daily():
    """Run every day at 2 AM EST"""
    db = next(get_db())
    month = datetime.now().strftime("%B").lower()
    nba.scrape_nba_boxscores(2025, month, db)

@scheduler.scheduled_job('cron', hour=3, minute=0)
def scrape_nfl_weekly():
    db = next(get_db())
    nfl.scrape_nfl_games(2025, db)

# Add more jobs for other sports...

if __name__ == "__main__":
    print("🚀 Starting sports scraper scheduler...")
    scheduler.start()
```

---

## Step 4: FastAPI Endpoints

Create **src/api/main.py**:

```python
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from src.database.connection import get_db

app = FastAPI(title="Sports Betting Model API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Update with your Lovable domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/nba/player-stats/{player_name}")
def get_nba_player_stats(player_name: str, db: Session = Depends(get_db)):
    query = f"""
        SELECT * FROM nba_player_stats 
        WHERE player_name ILIKE '%{player_name}%'
        ORDER BY game_id DESC LIMIT 10
    """
    result = db.execute(query).fetchall()
    return {"player": player_name, "recent_games": result}

@app.get("/health")
def health_check():
    return {"status": "ok", "timestamp": datetime.utcnow()}
```

---

## Step 5: Deploy to Railway

Create **Procfile**:
```
web: uvicorn src.api.main:app --host 0.0.0.0 --port $PORT
worker: python -m src.workers.scheduler
```

Create **railway.json**:
```json
{
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
```

Create **.env.example**:
```
DATABASE_URL=postgresql://user:pass@host:5432/dbname
PORT=8000
```

---

## Deployment Steps (Railway)

1. **Connect repo to Railway**:
   - In Railway project settings, click "Connect Repo"
   - Select `mlamarfinley/sports-betting-scrapers`

2. **Add environment variables**:
   - Go to Variables tab
   - Add `DATABASE_URL` (Railway will auto-provide from Postgres service)

3. **Run migrations**:
   ```bash
   railway run alembic upgrade head
   ```

4. **Deploy**:
   - Push code → Railway auto-deploys
   - Two services will run: `web` (API) and `worker` (scrapers)

---

## Next Actions for YOU

1. ✅ Clone `mlamarfinley/sports-betting-scrapers` locally
2. Create the file structure above (copy/paste from this guide)
3. Test NBA scraper locally:
   ```bash
   python -m src.scrapers.nba
   ```
4. Run migration to create tables:
   ```bash
   alembic upgrade head
   ```
5. Push to GitHub → Railway auto-deploys
6. Verify API at `https://your-railway-url.railway.app/docs`
7. Connect Lovable dashboard to API endpoint
8. Repeat pattern for NFL, NHL, Soccer, etc.

---

## Database Connection String

Railway Postgres URL format:
```
postgresql://postgres:PASSWORD@containers-us-west-xxx.railway.app:PORT/railway
```

Get from Railway → Postgres service → Variables tab → `DATABASE_URL`
