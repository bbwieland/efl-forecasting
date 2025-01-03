CURRENT_SEASON = 2024

# Columns to scrape from FBRef fixtures page.
FBREF_COLUMNS = ['home_team', 'away_team', 'score', 'date', 'home_xg', 'away_xg']

# League names
PREMIER_LEAGUE = "Premier League"
CHAMPIONSHIP = "Championship"
LEAGUE_ONE = "League One"
LEAGUE_TWO = "League Two"

ENGLISH_LEAGUES = [PREMIER_LEAGUE, CHAMPIONSHIP, LEAGUE_ONE, LEAGUE_TWO]
ENGLISH_LEAGUES_WITH_XG = [PREMIER_LEAGUE, CHAMPIONSHIP]

# This dictionary maps leagues to their FBRef league IDs.
LEAGUE_ID_MAPPING = {
    PREMIER_LEAGUE : 9,
    CHAMPIONSHIP : 10,
    LEAGUE_ONE : 15,
    LEAGUE_TWO : 16
}

HOME = "home_team"
AWAY = "away_team"
HOME_G = "home_score"
AWAY_G = "away_score"
HOME_XG = "home_xg"
AWAY_XG = "away_xg"
LEAGUE = "league"
GAME_DATE = "date"
SCORE = "score"
SEASON = "season"

MATCH_DATA_COLUMNS = [HOME, AWAY, LEAGUE, SEASON, GAME_DATE, HOME_G, AWAY_G, HOME_XG, AWAY_XG]
MATCH_DATA_CSV = "match_data.csv"

DEFAULT_SLEEP = 5

INDEX_SUFFIX = "_idx"

CATEGORICAL_INDEXES = [HOME + INDEX_SUFFIX, AWAY + INDEX_SUFFIX, LEAGUE + INDEX_SUFFIX, SEASON + INDEX_SUFFIX]
MODEL_NUMERIC_VARIABLES = [HOME_G, AWAY_G, HOME_XG, AWAY_XG]

MODEL_VARIABLES = CATEGORICAL_INDEXES + MODEL_NUMERIC_VARIABLES