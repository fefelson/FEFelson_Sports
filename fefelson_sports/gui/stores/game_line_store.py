import pandas as pd

from ...database.models.database import get_db_session


class GameLineStore:

    
        

    def _moving_avg(data, n):
        # Calculate moving averages (6-game and 13-game)
        a, b = 6, 13
        valueList = []
        if len(data) >= n:
            valueList = [sum(data[(i-n):i])/n for i in range(n, len(data)+1)] # average of n number of games
        return valueList
        

    def get_win_loss_chart(gameLog):
        gameLog = gameLog.dropna()
        results = gameLog["result"]
        homeList = []
        awayList = []
        sixAvg = GameLineStore._moving_avg(results, 6)
        thirteenAvg = GameLineStore._moving_avg(results, 13)

        x=0
        for _, row in gameLog.iterrows():
            if row["is_home"]:
                homeList.append((x, row["result"])) # adds i for placement
            else:
                awayList.append((x, row["result"]))
            x+= 1

        return homeList, awayList, sixAvg, thirteenAvg


    def get_pts_spread_chart(gameLog):
        gameLog = gameLog.dropna()
        ptsSpreads = [row["pts_spread"]*-1 for _, row in gameLog.iterrows()]
        homeList = []
        awayList = []
        sixAvg = GameLineStore._moving_avg(ptsSpreads, 6)
        thirteenAvg = GameLineStore._moving_avg(ptsSpreads, 13)

        x = 0
        for _, row in gameLog.iterrows():
            if row["is_home"]:
                homeList.append((x, row["pts_spread"]*-1)) # adds i for placement
            else:
                awayList.append((x, row["pts_spread"]*-1)) # multiplies by -1 for clarity vs/ wins chart
            x+= 1
        return homeList, awayList, sixAvg, thirteenAvg
    

    def get_ats_chart(gameLog):
        gameLog = gameLog.dropna() 
        ats =gameLog["ats"]
        winList = []
        lossList = []
        sixAvg = GameLineStore._moving_avg(ats, 6)
        thirteenAvg = GameLineStore._moving_avg(ats, 13)

        x=0
        for _, row in gameLog.iterrows():
            if row["is_winner"]:
                winList.append((x, row["ats"]+row["is_cover"])) # adds i for placement
            else:
                lossList.append((x, row["ats"]+row["is_cover"])) # adds is_cover to add depth to 0.5 case without affectig push case
            x+=1
        return winList, lossList, sixAvg, thirteenAvg
        

        

