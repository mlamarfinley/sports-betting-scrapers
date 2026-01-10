"""Database models for sports betting scrapers"""

from sqlalchemy import Column, Integer, String, Date, DateTime, Float, ForeignKey, func
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


# NBA Tables
class NBAGame(Base):
    __tablename__ = "nba_games"
    
    game_id = Column(String(20), primary_key=True)
    date = Column(Date, nullable=False)
    home_team = Column(String(50))
    away_team = Column(String(50))
    home_score = Column(Integer)
    away_score = Column(Integer)
    season = Column(Integer)
    scraped_at = Column(DateTime(timezone=True), server_default=func.now())

class NBATeam(Base):
    __tablename__ = "nba_teams"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100))
    abbreviation = Column(String(10))
    scraped_at = Column(DateTime(timezone=True), server_default=func.now())

class NBAPlayer(Base):
    __tablename__ = "nba_players"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100))
    team = Column(String(50))
    position = Column(String(10))
    scraped_at = Column(DateTime(timezone=True), server_default=func.now())



class NBAPlayerStat(Base):
    __tablename__ = "nba_player_stats"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    game_id = Column(String(20), ForeignKey("nba_games.game_id"))
    player_name = Column(String(100))
    team = Column(String(50))
    minutes = Column(String(10))
    points = Column(Integer)
    rebounds = Column(Integer)
    assists = Column(Integer)
    steals = Column(Integer)
    blocks = Column(Integer)
    turnovers = Column(Integer)
    fg_made = Column(Integer)
    fg_attempted = Column(Integer)
    three_made = Column(Integer)
    three_attempted = Column(Integer)
    ft_made = Column(Integer)
    ft_attempted = Column(Integer)


# NFL Tables
class NFLGame(Base):
    __tablename__ = "nfl_games"
    
    game_id = Column(String(20), primary_key=True)
    date = Column(Date, nullable=False)
    home_team = Column(String(50))
    away_team = Column(String(50))
    home_score = Column(Integer)
    away_score = Column(Integer)
    season = Column(Integer)
    week = Column(Integer)
    scraped_at = Column(DateTime(timezone=True), server_default=func.now())


class NFLPlayerStat(Base):
    __tablename__ = "nfl_player_stats"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    game_id = Column(String(20), ForeignKey("nfl_games.game_id"))
    player_name = Column(String(100))
    team = Column(String(50))
    position = Column(String(10))
    pass_attempts = Column(Integer)
    pass_completions = Column(Integer)
    pass_yards = Column(Integer)
    pass_touchdowns = Column(Integer)
    interceptions = Column(Integer)
    rush_attempts = Column(Integer)
    rush_yards = Column(Integer)
    rush_touchdowns = Column(Integer)
    receptions = Column(Integer)
    receiving_yards = Column(Integer)
    receiving_touchdowns = Column(Integer)
    targets = Column(Integer)


# NHL Tables
class NHLGame(Base):
    __tablename__ = "nhl_games"
    
    game_id = Column(String(20), primary_key=True)
    date = Column(Date, nullable=False)
    home_team = Column(String(50))
    away_team = Column(String(50))
    home_score = Column(Integer)
    away_score = Column(Integer)
    season = Column(Integer)
    scraped_at = Column(DateTime(timezone=True), server_default=func.now())


class NHLPlayerStat(Base):
    __tablename__ = "nhl_player_stats"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    game_id = Column(String(20), ForeignKey("nhl_games.game_id"))
    player_name = Column(String(100))
    team = Column(String(50))
    position = Column(String(10))
    goals = Column(Integer)
    assists = Column(Integer)
    points = Column(Integer)
    plus_minus = Column(Integer)
    pim = Column(Integer)
    shots = Column(Integer)
    time_on_ice = Column(String(10))


# Soccer Tables  
class SoccerMatch(Base):
    __tablename__ = "soccer_matches"
    
    match_id = Column(String(20), primary_key=True)
    date = Column(Date, nullable=False)
    home_team = Column(String(100))
    away_team = Column(String(100))
    home_score = Column(Integer)
    away_score = Column(Integer)
    league = Column(String(100))
    season = Column(String(20))
    scraped_at = Column(DateTime(timezone=True), server_default=func.now())


class SoccerPlayerStat(Base):
    __tablename__ = "soccer_player_stats"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    match_id = Column(String(20), ForeignKey("soccer_matches.match_id"))
    player_name = Column(String(100))
    team = Column(String(100))
    position = Column(String(20))
    goals = Column(Integer)
    assists = Column(Integer)
    shots = Column(Integer)
    shots_on_target = Column(Integer)
    xg = Column(Float)
    xa = Column(Float)
    passes_completed = Column(Integer)
    passes_attempted = Column(Integer)


# LoL Tables
class LoLMatch(Base):
    __tablename__ = "lol_matches"
    
    match_id = Column(String(50), primary_key=True)
    date = Column(DateTime, nullable=False)
    team1 = Column(String(100))
    team2 = Column(String(100))
    winner = Column(String(100))
    duration = Column(Integer)
    league = Column(String(100))
    season = Column(String(20))
    scraped_at = Column(DateTime(timezone=True), server_default=func.now())


class LoLPlayerStat(Base):
    __tablename__ = "lol_player_stats"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    match_id = Column(String(50), ForeignKey("lol_matches.match_id"))
    player_name = Column(String(100))
    team = Column(String(100))
    champion = Column(String(50))
    role = Column(String(20))
    kills = Column(Integer)
    deaths = Column(Integer)
    assists = Column(Integer)
    cs = Column(Integer)
    gold = Column(Integer)
    damage_dealt = Column(Integer)


# CS2 Tables
class CS2Match(Base):
    __tablename__ = "cs2_matches"
    
    match_id = Column(String(50), primary_key=True)
    date = Column(DateTime, nullable=False)
    team1 = Column(String(100))
    team2 = Column(String(100))
    team1_score = Column(Integer)
    team2_score = Column(Integer)
    tournament = Column(String(200))
    scraped_at = Column(DateTime(timezone=True), server_default=func.now())


class CS2PlayerStat(Base):
    __tablename__ = "cs2_player_stats"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    match_id = Column(String(50), ForeignKey("cs2_matches.match_id"))
    player_name = Column(String(100))
    team = Column(String(100))
    kills = Column(Integer)
    deaths = Column(Integer)
    assists = Column(Integer)
    adr = Column(Float)
    rating = Column(Float)


# Dota2 Tables
class Dota2Match(Base):
    __tablename__ = "dota2_matches"
    
    match_id = Column(String(50), primary_key=True)
    date = Column(DateTime, nullable=False)
    team1 = Column(String(100))
    team2 = Column(String(100))
    winner = Column(String(100))
    duration = Column(Integer)
    tournament = Column(String(200))
    scraped_at = Column(DateTime(timezone=True), server_default=func.now())


class Dota2PlayerStat(Base):
    __tablename__ = "dota2_player_stats"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    match_id = Column(String(50), ForeignKey("dota2_matches.match_id"))
    player_name = Column(String(100))
    team = Column(String(100))
    hero = Column(String(50))
    role = Column(String(20))
    kills = Column(Integer)
    deaths = Column(Integer)
    assists = Column(Integer)
    net_worth = Column(Integer)
    hero_damage = Column(Integer)


# CoD Tables
class CoDMatch(Base):
    __tablename__ = "cod_matches"
    
    match_id = Column(String(50), primary_key=True)
    date = Column(DateTime, nullable=False)
    team1 = Column(String(100))
    team2 = Column(String(100))
    team1_score = Column(Integer)
    team2_score = Column(Integer)
    mode = Column(String(50))
    event = Column(String(200))
    scraped_at = Column(DateTime(timezone=True), server_default=func.now())


class CoDPlayerStat(Base):
    __tablename__ = "cod_player_stats"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    match_id = Column(String(50), ForeignKey("cod_matches.match_id"))
    player_name = Column(String(100))
    team = Column(String(100))
    kills = Column(Integer)
    deaths = Column(Integer)
    assists = Column(Integer)
    damage = Column(Integer)
    kd_ratio = Column(Float)
