from datetime import date, timedelta

from ..database.stores.base import LeagueStore

# for debugging
from pprint import pprint 

####################################################################
####################################################################


today = date.today()


####################################################################
####################################################################


class Schedule:

    def __init__(self, leagueId):
        self.leagueId = leagueId
        self.leagueStore = LeagueStore()


    def current_until(self, gameDate):
        raise NotImplementedError


    def get_back_dates(self):
        raise NotImplementedError



    def get_future_dates(self, nGD):
        raise NotImplementedError


    def is_active(self) -> bool:
        league = self.leagueStore.get_major_dates(self.leagueId)
        return league["startDate"] <= today < league["endDate"]


    def is_up_to_date(self) -> bool:
        raise NotImplementedError

####################################################################
####################################################################



class DailySchedule(Schedule):
        
    
    def current_until(self, gameDate):
        self.leagueStore.set_last_update(self.leagueId, date.fromisoformat(gameDate))


    def get_back_dates(self):
        backDates = []
        gameDate = self.leagueStore.get_last_update(self.leagueId)
        while gameDate < today:
            
            backDates.append(str(gameDate))
            gameDate += timedelta(1)
        
        # print("\nback dates")
        # pprint(backDates)
        return backDates


    def get_future_dates(self, nGD):
        futureDates = []
        gameDate = today 
        for i in range(nGD):

            gameDate += timedelta(i)
            futureDates.append(str(gameDate))
        
        # print("\nfuture dates")
        # pprint(futureDates)
        return futureDates



    def is_up_to_date(self) -> bool:
        lastUpdate = self.leagueStore.get_last_update(self.leagueId)
        if lastUpdate is None:
            return False
        else:
            return lastUpdate == today - timedelta(1)



####################################################################
####################################################################



class WeeklySchedule(Schedule):


    def _get_week(self, gameDate):
        found = 0 
        weeks = sorted(self.leagueStore.get_weeks(self.leagueId), key=lambda x: x["week_num"])
        for week in weeks:
            if week["start_date"] <= gameDate <= week["end_date"]:
                found = week["week_num"]
                break
        return found

    
    def current_until(self, gameDate):
        currentDate = None
        gameDate = gameDate.split("_")[-1]
        weeks = sorted(self.leagueStore.get_weeks(self.leagueId), key=lambda x: x["week_num"])
        for week in weeks:
            if int(gameDate) == week["week_num"]:
                currentDate = week["end_date"]
                break

        if currentDate:
            self.leagueStore.set_last_update(self.leagueId, currentDate)


    def get_back_dates(self):
        season = self.leagueStore.get_current_season(self.leagueId)
        lastUpdate = self.leagueStore.get_last_update(self.leagueId)
        if not lastUpdate:
            lastUpdate = self.leagueStore.get_major_dates(self.leagueId)["startDate"]
        weeks = sorted(self.leagueStore.get_weeks(self.leagueId), key=lambda x: x["week_num"])

        backDates = []
        for week in weeks:
            if week["start_date"] > lastUpdate and today > week["end_date"]:
                backDates.append(f"{season}_{week['week_num']}")
        
        # print("\nback dates")
        # pprint(backDates)
        return backDates


    def get_future_dates(self, nGD):
        season = self.leagueStore.get_current_season(self.leagueId)
        gameWeek = self._get_week(today)
        futureDates = []
        for i in range(nGD):
            gameWeek += i
            if gameWeek > 0:
                futureDates.append(f"{season}_{gameWeek}")
        
        # print("\nfuture dates")
        # pprint(futureDates)
        return futureDates


    def is_up_to_date(self) -> bool:
        lastUpdate = self.leagueStore.get_last_update(self.leagueId)
        if lastUpdate is None:
            return False

        updateWeek = self._get_week(lastUpdate)
        todayWeek = self._get_week(today)

        return ((todayWeek -1) - updateWeek) <= 0
               
        

        
        
    
        
        