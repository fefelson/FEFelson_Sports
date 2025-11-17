#!/usr/bin/env python3
from datetime import datetime
from typing import Optional
import pytz

from fefelson_sports.models.leagues import MLB, NBA, NCAAB, NFL, NCAAF

est = pytz.timezone('America/New_York')


       

if __name__ == "__main__":
    # Parse command-line arguments

    timeNow = datetime.now().astimezone(est)

    if timeNow.hour >= 4 and timeNow.hour < 22:
    
        for league in (MLB, NFL, NBA, NCAAB, NCAAF, ):
            league().update()
