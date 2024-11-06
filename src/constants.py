CURRENT_SEASON = 2024

# Columns to scrape from FBRef fixtures page.
FBREF_COLUMNS = ['home_team', 'away_team', 'score', 'date', 'home_xg', 'away_xg']

# League names
PREMIER_LEAGUE = "Premier League"
CHAMPIONSHIP = "Championship"
LEAGUE_ONE = "League One"
LEAGUE_TWO = "League Two"

ENGLISH_LEAGUES = [PREMIER_LEAGUE, CHAMPIONSHIP, LEAGUE_ONE, LEAGUE_TWO]

# This dictionary maps leagues to their FBRef league IDs.
LEAGUE_ID_MAPPING = {
    PREMIER_LEAGUE : 9,
    CHAMPIONSHIP : 10,
    LEAGUE_ONE : 15,
    LEAGUE_TWO : 16
}