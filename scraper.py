import argparse
from typing import Tuple
import src.constants as c
import src.etl as etl

def get_args() -> Tuple[str, any]:
    """
    Parses arguments from the command line.

    Parameters
    ----------
    None.

    Returns
    -------
    args: Arguments to pass to the command line function run.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("--first_season", help="Number of days before current date to include in pitch model.", required=True, type=int)
    args = parser.parse_args()

    return args

def main():
    args = get_args()
    all_seasons = list(range(args.first_season, c.CURRENT_SEASON + 1))
    etl.scrape_leagues_seasons(seasons=all_seasons)

if __name__ == '__main__':
    main()