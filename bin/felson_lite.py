from datetime import datetime, date, timedelta
from os import environ, listdir, remove
from pprint import pprint 
from pytz import timezone

from fefelson_sports.utils.file_agent import JSONAgent
from fefelson_sports.utils.gaming_utils import calculate_moneyline_probs, calculate_kelly_criterion, calculate_winnings


BASE_PATH = f"{environ['HOME']}/FEFelson/FEFelson_Sports/matchups"
est = timezone('America/New_York')

    
if __name__ == "__main__":
    gameList = []
    for filePath in [f"{BASE_PATH}/{fileName}" for fileName in listdir(BASE_PATH)]:
        gameList.append(JSONAgent.read(filePath))

    for data in sorted(gameList, key=lambda x: datetime.fromisoformat(x["gameTime"])):
        
        # if datetime.fromisoformat(data["gameTime"]).date() < date.today():
        #     remove(filePath)

        if datetime.fromisoformat(data["gameTime"]).date() >= date.today():

            if data["odds"]:
                try:
                    awayML = data["odds"][-1]["away_ml"]
                    homeML = data["odds"][-1]["home_ml"]
                    spread = f"+{data['odds'][-1]['home_spread']}" if float(data['odds'][-1]['home_spread']) > 0 else f"{data['odds'][-1]['home_spread']}"
                    awayProb, homeProb, vig = calculate_moneyline_probs(int(awayML), int(homeML))
                    awayImp = round(awayProb["implied_prob"]*100, 1)
                    awayTrue = round(awayProb["true_prob"]*100, 1)

                    homeImp = round(homeProb["implied_prob"]*100, 1)
                    homeTrue = round(homeProb["true_prob"]*100, 1)

                    vig = round(vig*100,1)

                    awayESPN = data['predictor'][0][1]
                    homeESPN = data['predictor'][1][1]

                    awayKelly = calculate_kelly_criterion(float(awayESPN)/100, int(awayML))
                    homeKelly = calculate_kelly_criterion(float(homeESPN)/100, int(homeML))

                    awayWin = calculate_winnings(awayKelly, int(awayML), 1)
                    homeWin = calculate_winnings(homeKelly, int(homeML), 1)

                    if awayKelly or homeKelly:

                        print(f"{data['title']:^90}\n") 
                        print(f"{spread:^90}\n")
                        print(f"{'away':^40}{'':^10}{'home':^40}")
                        print(f"{awayML:^40}{vig:^10}{homeML:^40}\n")
                        print(f"{awayImp:^20}{awayTrue:^10}{'':^20}{homeImp:^20}{homeTrue:^10}")
                        print(f"{awayESPN:^40}{'':^10}{homeESPN:^40}\n\n")
                    
                        print(f"{awayKelly:^40.2f}{'':^10}{homeKelly:^40.2f}")
                        print(f"{awayWin:^40.2f}{'':^10}{homeWin:^40.2f}")
                        print("\n\n\n")
                    
                except ValueError:
                    pass
            
            
           

