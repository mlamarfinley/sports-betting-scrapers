# Lovable Connection Guide

## Overview
This guide explains how to connect your Lovable frontend to the Sports Betting Model API.

## API Base URL
```
https://web-production-37454.up.railway.app
```

## Available Endpoints

### Public Data Endpoints

#### 1. Get NBA Games
**Endpoint:** `GET /nba/games`
**Query Parameters:** 
- `limit` (optional, default: 100): Number of games to return

**Example:**
```javascript
fetch('https://web-production-37454.up.railway.app/nba/games?limit=50')
  .then(res => res.json())
  .then(data => console.log(data));
```

**Response:**
```json
{
  "status": "success",
  "count": 50,
  "games": [
    {
      "id": 1,
      "date": "2026-01-06",
      "home_team": "Lakers",
      "away_team": "Warriors",
      "home_score": 110,
      "away_score": 105
    }
  ]
}
```

#### 2. Get NBA Teams
**Endpoint:** `GET /nba/teams`

**Example:**
```javascript
fetch('https://web-production-37454.up.railway.app/nba/teams')
  .then(res => res.json())
  .then(data => console.log(data));
```

**Response:**
```json
{
  "status": "success",
  "count": 30,
  "teams": [
    {
      "id": 1,
      "name": "Los Angeles Lakers",
      "abbreviation": "LAL"
    }
  ]
}
```

#### 3. Get NBA Players
**Endpoint:** `GET /nba/players`
**Query Parameters:** 
- `limit` (optional, default: 100): Number of players to return

**Example:**
```javascript
fetch('https://web-production-37454.up.railway.app/nba/players?limit=20')
  .then(res => res.json())
  .then(data => console.log(data));
```

**Response:**
```json
{
  "status": "success",
  "count": 20,
  "players": [
    {
      "id": 1,
      "name": "LeBron James",
      "team": "Lakers",
      "position": "SF"
    }
  ]
}
```

## Connecting to Lovable

### Step 1: Set API Base URL
In your Lovable project, create a config file:

```javascript
// config/api.js
export const API_BASE_URL = 'https://web-production-37454.up.railway.app';
```

### Step 2: Create API Service
Create a service to handle API calls:

```javascript
// services/sportsApi.js
import { API_BASE_URL } from '../config/api';

export const sportsApi = {
  async getNBAGames(limit = 100) {
    const response = await fetch(`${API_BASE_URL}/nba/games?limit=${limit}`);
    return response.json();
  },
  
  async getNBATeams() {
    const response = await fetch(`${API_BASE_URL}/nba/teams`);
    return response.json();
  },
  
  async getNBAPlayers(limit = 100) {
    const response = await fetch(`${API_BASE_URL}/nba/players?limit=${limit}`);
    return response.json();
  }
};
```

### Step 3: Use in Components
Example React component:

```jsx
import React, { useEffect, useState } from 'react';
import { sportsApi } from '../services/sportsApi';

function NBADashboard() {
  const [games, setGames] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadData() {
      try {
        const data = await sportsApi.getNBAGames(50);
        if (data.status === 'success') {
          setGames(data.games);
        }
      } catch (error) {
        console.error('Error loading games:', error);
      } finally {
        setLoading(false);
      }
    }
    loadData();
  }, []);

  if (loading) return <div>Loading...</div>;

  return (
    <div>
      <h1>NBA Games</h1>
      {games.map(game => (
        <div key={game.id}>
          {game.away_team} @ {game.home_team} - {game.date}
        </div>
      ))}
    </div>
  );
}

export default NBADashboard;
```

## CORS Configuration
The API has CORS enabled with `allow_origins=["*"]` for development. Update line 12 in `src/api/main.py` with your Lovable domain for production:

```python
allow_origins=["https://your-lovable-domain.com"],
```

## Testing the API
Visit the interactive API documentation:
```
https://web-production-37454.up.railway.app/docs
```

## Next Steps
1. Initialize the database: `POST /admin/init-db`
2. Run scrapers to populate data: `POST /admin/scrape-nba`
3. Connect your Lovable frontend using the examples above
4. Start building your sports betting dashboard!

## Framework Status
✅ API deployed on Railway
✅ Database tables created  
✅ Data endpoints available
✅ CORS configured
✅ Scraper framework in place (NBA, NFL, MLB, NHL)
⏳ Data population (run scrapers to populate)
⏳ Frontend integration (your Lovable app)

## Support
For issues or questions, check the API logs in Railway or review the implementation in the GitHub repository.
