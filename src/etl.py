import src.constants as c

from urllib.request import urlopen
from bs4 import BeautifulSoup
import pandas as pd

from typing import List

import logging

logging.basicConfig(level = logging.INFO)
logger = logging.getLogger(name="FootballReferenceScraper")


def get_fbref_url(league: str, season: int, league_ids: dict = c.LEAGUE_ID_MAPPING) -> str:
    """Creates a FB-Ref URL matching the supplied parameters.

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

    soup = BeautifulSoup(page)
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