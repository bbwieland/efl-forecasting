import re

def split_score(score: str) -> tuple:
    """Splits a score string into home and away scores.

    Parameters
    ----------
    score : str
        A string containing a match score, e.g. '1-0'

    Returns
    -------
    tuple
        A tuple containing home_score and away_score as integers
    """

    if len(score) > 0:
        match = re.match(r'\(?\d*\)?\s*(\d+)[^\w\s](\d+)\s*\(?\d*\)?', score)
        home_score, away_score = int(match.group(1)), int(match.group(2))


    else:
        home_score, away_score = None, None

    return home_score, away_score

def clean_xg(xg: str) -> float:

    if len(xg) > 0:
        clean_xg = float(xg)

    else:
        clean_xg = None
    
    return clean_xg