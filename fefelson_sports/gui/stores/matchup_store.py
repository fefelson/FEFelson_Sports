from datetime import datetime
from json import load
from pytz import timezone

import os

from ...models.model_classes import MatchupData


##########################################################################
##########################################################################


est = timezone('America/New_York')



##########################################################################
##########################################################################


class MatchupStore:   


    def _get_basepath(self, league, gamedate):
        if not gamedate:
            gamedate = datetime.today().astimezone(est)

        leagueId = league._leagueId
        season = league.get_current_season()

        _, month, day = str(gamedate.date()).split("-")
        module_dir = os.path.dirname(os.path.abspath(__file__))
        return f"{module_dir}/../../../data/matchups/{leagueId}/{season}/{month}/{day}/"


    def get_gamedate(self, leagues, gamedate=None):
        matchups = {}
        for league in leagues.values():
            basePath = self._get_basepath(league, gamedate)
            for filePath in [basePath+fileName for fileName in os.listdir(basePath)]:
                with open(filePath) as fileIn:
                    data = MatchupData(**load(fileIn))
                    matchups[data.gameId] = data
        return [m for m in sorted(matchups.values(), key=lambda x: datetime.fromisoformat(x.gameTime)) if datetime.fromisoformat(m.gameTime) > datetime.now().astimezone(est) ]
    

    def get_matchup(self, league, gameId, gamedate=None):
        basePath = self._get_basepath(league, gamedate)
        filePath = f"{basePath}{gameId}.json"
        with open(filePath) as fileIn:
            return MatchupData(**load(fileIn))
            

    def get_tracking(self, index, matchup):
        if index == "pts_spread":
            timestamps = [record['timestamp'] for record in matchup.odds if record['home_spread'] != ""]
            lineItem = [abs(float(record['home_spread'])) for record in matchup.odds if record['home_spread'] != ""]  # Convert to int for plotting
            title = "Pts Spread Movement"
        if index == "total":
            timestamps = [record['timestamp'] for record in matchup.odds if record['total'] != ""]
            lineItem = [abs(float(record['total'])) for record in matchup.odds if record['total'] != ""]  # Convert to int for plotting
            title = "Total Movement"
        # Parse timestamps into datetime objects
        datetimes = [datetime.strptime(ts, '%Y-%m-%d %H:%M:%S.%f%z') for ts in timestamps]

        # Calculate time differences in seconds relative to the first timestamp
        x_seconds = [(dt - datetimes[0]).total_seconds() / 60 for dt in datetimes]  # Convert to minutes for better scaling

        # For x-axis labels, use the time part of the datetime
        time_labels = [dt.strftime('%a %H:%M') for dt in datetimes]

        return {
            "xData":x_seconds,
            "yData":lineItem,
            "label": f"{lineItem[0]} to {lineItem[-1]}",
            "title": title
        }

            

        