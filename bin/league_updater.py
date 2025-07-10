#!/usr/bin/env python3

from datetime import datetime
from typing import Optional
import pytz
import sys
import os

from fefelson_sports.sports.leagues import NBA, NCAAB, MLB


est = pytz.timezone('America/New_York')

leagues = {"MLB": MLB, }

def main(leagueId: Optional[str] = None) -> None:
    """Main function to update leagues based on input."""
    if leagueId:
        league = leagues[leagueId]()
        league.update()
    else:
        for league in leagues.values():
            league().update()
         

if __name__ == "__main__":
    # Parse command-line arguments
    league_id = sys.argv[1] if len(sys.argv) > 1 else None

    timeNow = datetime.now().astimezone(est)

    if timeNow.hour > 3 and timeNow.hour < 22:
        main(league_id)
