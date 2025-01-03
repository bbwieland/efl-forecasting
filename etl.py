import constants as c
import utils as utils
import time

from urllib.request import urlopen
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np

from typing import List, Tuple, Dict, Any

import logging

pd.options.mode.chained_assignment = None 

logging.basicConfig(level = logging.INFO)
logger = logging.getLogger(name="FootballReferenceScraper")


def get_fbref_url(league: str, season: int, league_ids: dict = c.LEAGUE_ID_MAPPING) -> str:
    """Creates a FBRef URL matching the supplied parameters.

    Parameters
    ----------
    league : str
        The league to scrape. Should be one of the English top four leagues.
    season : int
        The starting season to scrape (i.e. to scrape 2024-25, supply 2024 here)
    league_ids : dict, optional
        A mapping for FBRef league IDs by league name, by default c.LEAGUE_ID_MAPPING

    Returns
    -------
    str
        A URL to scrape.
    """

    if league not in c.ENGLISH_LEAGUES:
        raise ValueError(f"League must be contained in c.ENGLISH_LEAGUES!")

    # We need to hyphenate the league name
    league_name = league.replace(" ", "-")

    # Gets the league ID from the supplied dictionary of league IDs
    league_id = league_ids[league]

    # Uses the supplied season to create a season string compatible with site URLs.
    season_end = season + 1
    season_str = f"{season}-{season_end}"

    url = f"https://fbref.com/en/comps/{league_id}/{season_str}/schedule/{season_str}-{league_name}-Scores-and-Fixtures"

    return url

def raw_scrape_fbref_matches(url: str, columns: List[str] = c.FBREF_COLUMNS) -> pd.DataFrame:
    """Scrapes a supplied Football Reference URL for match results.

    Parameters
    ----------
    url : str
        The FBRef URL to scrape.
    columns : List[str], optional
        Which columns to include in the output dataframe, by default c.FBREF_COLUMNS

    Returns
    -------
    pd.DataFrame
        A dataframe of FBRef data.
    """

    page = urlopen(url).read()

    soup = BeautifulSoup(page, "html.parser")
    table = soup.find("tbody")
    
    rows = table.find_all("tr")

    df_dict = {}
    for row in rows:
        if (row.find('th', {"scope":"row"}) != None):

            for column in columns:
                cell = row.find("td", {"data-stat" : column})
                raw_text = cell.text.strip().encode()
                text = raw_text.decode("utf-8")

                if column in df_dict:
                    df_dict[column].append(text)
                
                else:
                    df_dict[column] = [text]

    raw_df = pd.DataFrame.from_dict(df_dict)

    logger.info(f"Successfully scraped {url}")
    return raw_df

def clean_fbref_matches(match_df: pd.DataFrame, league: str, season: int) -> pd.DataFrame:
    """Cleans scraped FBRef scores to a usable modeling format

    Parameters
    ----------
    match_df : pd.DataFrame
        The match dataframe to clean
    league : str
        The league to include in the cleaned df

    Returns
    -------
    pd.DataFrame
        A dataframe containing cleaned match data
    """

    subset_df = match_df[(match_df[c.HOME] != "") & (match_df[c.HOME] != "")].reset_index(drop=True)

    subset_df[c.LEAGUE] = league
    subset_df[c.SEASON] = season

    home_score, away_score = list(), list()

    for score in subset_df[c.SCORE]:
        home, away = utils.split_score(score=score)
        home_score.append(home)
        away_score.append(away)

    home_xg, away_xg = list(), list()

    for xg in subset_df[c.HOME_XG]:
        clean_xg = utils.clean_xg(xg=xg)
        home_xg.append(clean_xg)

    for xg in subset_df[c.AWAY_XG]:
        clean_xg = utils.clean_xg(xg=xg)
        away_xg.append(clean_xg)

    subset_df[c.HOME_G] = pd.Series(home_score)
    subset_df[c.AWAY_G] = pd.Series(away_score)
    subset_df[c.HOME_XG] = pd.Series(home_xg)
    subset_df[c.AWAY_XG] = pd.Series(away_xg)

    clean_df = subset_df[c.MATCH_DATA_COLUMNS]
    return clean_df

def scrape_league_season(league: str, season: int) -> pd.DataFrame:
    """High-level wrapper to scrape and preprocess FBRef data over a given timeframe.

    Parameters
    ----------
    league : str
        The league to scrape data from.
    season : int
        The season to scrape data from.

    Returns
    -------
    pd.DataFrame
        A dataframe containing the necessary FBRef match results.
    """

    url = get_fbref_url(league=league, season=season)
    raw_df = raw_scrape_fbref_matches(url=url)
    clean_df = clean_fbref_matches(match_df=raw_df, league=league, season=season)

    return clean_df

def scrape_leagues_seasons(seasons: List[int], leagues: List[str] = c.ENGLISH_LEAGUES_WITH_XG, to_csv: bool = True, sleep: int = c.DEFAULT_SLEEP) -> pd.DataFrame:
    """Scrapes data over multiple seasons & leagues in the English Football League.

    Parameters
    ----------
    leagues : List[str]
        The leagues to scrape data from.
    seasons : List[int]
        The seasons to scrape data from.
    to_csv : bool, optional
        Whether to save the data to a csv, by default True
    sleep : int, optional
        How long to sleep the system for in-between runs, by default c.DEFAULT_SLEEP

    Returns
    -------
    pd.DataFrame
        A dataframe containing match results.
    """

    sleep_time = len(seasons) * len(leagues) * sleep
    logging.info(f"Performing a bulk Football Reference scrape. Note that {sleep_time} seconds of system sleep are built into the scrape.")

    match_data = pd.DataFrame()

    for season in seasons:
        for league in leagues:
            time.sleep(sleep)
            new_data = scrape_league_season(league=league, season=season)
            match_data = pd.concat([match_data, new_data], ignore_index=True)

    logging.info(f"Successfully scraped data for {len(leagues)} leagues and {len(seasons)} seasons of EFL match results!")

    if to_csv: 
        match_data.to_csv(c.MATCH_DATA_CSV, index=False)
        return match_data

    else:
        return match_data
    
def home_away_to_team_opponent(df: pd.DataFrame) -> pd.DataFrame:
    """Converts a dataframe with scores in home-away format to a dataframe containing team-games.

    Parameters
    ----------
    df : pd.DataFrame
        The dataframe of home & away results to process.

    Returns
    -------
    pd.DataFrame
        A dataframe containing team-games
    """

    team_games = []

    for _, row in df.iterrows():
        home_game = {
            "team": row[c.HOME],
            "opponent": row[c.AWAY],
            "team_score": row[c.HOME_G],
            "opponent_score": row[c.AWAY_G],
            "team_xg": row[c.HOME_XG],
            "opponent_xg": row[c.AWAY_XG],
            c.LEAGUE: row[c.LEAGUE],
            c.GAME_DATE: row[c.GAME_DATE], 
            c.SEASON : row[c.SEASON]
        }
        away_game = {
            "team": row[c.AWAY],
            "opponent": row[c.HOME],
            "team_score": row[c.AWAY_G],
            "opponent_score": row[c.HOME_G],
            "team_xg": row[c.AWAY_XG],
            "opponent_xg": row[c.HOME_XG],
            c.LEAGUE: row[c.LEAGUE],
            c.GAME_DATE: row[c.GAME_DATE], 
            c.SEASON : row[c.SEASON]
        }
        team_games.append(home_game)
        team_games.append(away_game)

    team_games_df = pd.DataFrame(team_games)

    output_df = team_games_df[["team", "opponent", c.LEAGUE, c.SEASON, c.GAME_DATE, "team_score", "opponent_score", "team_xg", "opponent_xg"]]
    output_df["goal_diff"] = output_df["team_score"] - output_df["opponent_score"]
    output_df["xg_diff"] = output_df["team_xg"] - output_df["opponent_xg"]

    return output_df

def encode_teams(input_df: pd.DataFrame) -> Tuple[pd.array, pd.array, pd.array]:
    """Encodes team IDs as categorical integers. 

    Parameters
    ----------
    input_df : pd.DataFrame
        The input dataframe to extract team encodings from.

    Returns
    -------
    Tuple[pd.array, pd.array, pd.array]
        A tuple of home team indexes, away team indexes, and home/away labels
    """

    home_teams = input_df[c.HOME]
    away_teams = input_df[c.AWAY]
    teams = pd.concat([home_teams, away_teams])

    _ , team_labels = pd.factorize(teams, sort=True)

    home_idx = pd.Categorical(home_teams, categories=team_labels).codes
    away_idx = pd.Categorical(away_teams, categories=team_labels).codes

    return home_idx, away_idx, team_labels

def encode_leagues(input_df: pd.DataFrame) -> Tuple[pd.array, pd.array]:

    leagues = input_df[c.LEAGUE]
    _ , league_labels = pd.factorize(leagues, sort=True)

    league_idx = pd.Categorical(leagues, categories=league_labels).codes

    return league_idx, league_labels

def encode_seasons(input_df: pd.DataFrame) -> Tuple[pd.array, pd.array]:

    seasons = input_df[c.SEASON]
    _ , season_labels = pd.factorize(seasons, sort=True)

    season_idx = pd.Categorical(seasons, categories=season_labels).codes

    return season_idx, season_labels


def format_data_for_stan(input_df: pd.DataFrame, past_matches: bool = True) -> dict:
    """Formats raw data for compilation into the Stan model.

    Parameters
    ----------
    input_df : pd.DataFrame
        a dataframe from match_data.csv 
    
    past_matches : bool, optional
        Whether to filter to only previous matches, defaults to True

    Returns
    -------
    dict
        A dictionary containing all necessary data for Stan to compile the model.
    """

    if past_matches:
        input_df = input_df.dropna()

    n_games = len(input_df.index)

    home_idx, away_idx, team_labels = encode_teams(input_df=input_df)
    season_idx, season_labels = encode_seasons(input_df=input_df)
    league_idx, league_labels = encode_leagues(input_df=input_df)

    n_teams = len(team_labels)
    n_seasons = len(season_labels)
    n_leagues = len(league_labels)

    home_goals = input_df[c.HOME_G].astype('int') 
    away_goals = input_df[c.AWAY_G].astype('int')

    home_xg = input_df[c.HOME_XG]
    away_xg = input_df[c.AWAY_XG]

    home = np.repeat(1, n_games)
    away = np.repeat(1, n_games)

    stan_dict = {
        'n_teams' : n_teams,
        'n_games' : n_games,
        'n_seasons' : n_seasons, 
        'n_leagues' : n_leagues,
        'season' : season_idx,
        'home_team_code' : home_idx,
        'away_team_code' : away_idx,
        'league_code' : league_idx,
        'home_goals' : home_goals,
        'away_goals' : away_goals,
        'home_xg' : home_xg,
        'away_xg' : away_xg,
        'home' : home,
        'away' : away
    }

    coords_dict = {
        'teams' : team_labels,
        'seasons' : season_labels,
        'leagues' : league_labels
    }

    return stan_dict, coords_dict