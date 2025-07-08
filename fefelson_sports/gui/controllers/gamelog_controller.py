from datetime import datetime, timedelta

from ..stores.team_store import TeamStore
from ..views.components.game_filter import FilterFrame


############################################################################
############################################################################


def passes_cutoff_date(game, timeframe):
    cutoffDate = {"season":None, 
                      "2Months":datetime.today()-timedelta(60),
                      "1Month": datetime.today()-timedelta(30),
                      "2Weeks": datetime.today()-timedelta(14)}.get(timeframe, None)
    if cutoffDate:
        if game["game_date"] < cutoffDate:
                return False
    return True
            

############################################################################
############################################################################


class GamelogController:

    def __init__(self, teamCtrl, gamelogPanel):

        self.gamelog = None
        self.selectedGameIds = []

        self.filterCtrl = GameFilterController(self)

        self.teamCtrl = teamCtrl
        self.gamelogPanel = gamelogPanel


    def _add_game(self, gameId):
        if gameId in [game["game_id"] for game in self.gamelog]:
            self.selectedGameIds.add(gameId)


    def _remove_game(self, gameId):
        if gameId in self.selectedGameIds:
            self.selectedGameIds.remove(gameId)


    def filter_display_changed(self):
        self.gamelogPanel.set_display(self.filterCtrl.isDisplayed)


    def get_selectedIds(self):
        return self.selectedGameIds
    

    def get_timeframe(self):
        return self.filterCtrl.filters["timeframe"]


    def on_checkbox(self, event):
        gameId = event.GetEventObject().GetName()
        if event.IsChecked():
            self._add_game(gameId)
        else:
            self._remove_game(gameId)
        self.selected_gameIds_changed()


    def new_team(self, leagueId, teamId, season):

        self.filterCtrl.set_defaults()
        self.gamelog = TeamStore.get_team_gamelog(leagueId, teamId, season)
        [self.selectedGameIds.append(game["game_id"]) for _, game in self.gamelog.iterrows() if passes_cutoff_date(game, self.filterCtrl.filters["timeframe"])]
        self.gamelogPanel.set_panel(self.gamelog, self.selectedGameIds, self)
        self.filter_display_changed()


    def selected_gameIds_changed(self):
        self.teamCtrl.redisplay_team_panel()
        self.gamelogPanel.set_selected_gameIds(self.selectedGameIds)
        self.gamelogPanel.set_display()


    def set_selectedIds(self, filteredIds):
        self.selectedGameIds = filteredIds
        self.selected_gameIds_changed()




############################################################################
############################################################################



class GameFilterController:

    _default_filters = {
            'is_home': "all",
            'is_winner': "all",
            'is_favorite': "all",
            'is_cover': "all",
            'is_over': "all",
            "timeframe": "2Months"
        }
    

    def __init__(self, gamelogCtrl):  

        self.filterFrame = None
        self.isDisplayed = False
        self.filters = None 

        self.gamelogCtrl = gamelogCtrl

        self.set_defaults()


    def __del__(self):
        if self.filterFrame:
            self.filterFrame.Destroy()


    def _new_filter_frame(self):
        self.filterFrame = FilterFrame(self.gamelogCtrl.gamelogPanel, self.filter_frame_closed)
        self.filterFrame.filterPanel.set_default(self.filters)
        self.filterFrame.filterPanel.bind_to_ctrl(self)


    def _passes_filters(self, game, filters):
        
        if not passes_cutoff_date(game, filters["timeframe"]):
            return False

        # Home/Away filter
        if filters['is_home'] != "all":
            if game["is_home"] != (filters['is_home'] == "home"):
                return False
                
        # Win/Loss filter
        if filters['is_winner'] != "all":
            if game["is_winner"] and filters['is_winner'] == "loser":
                return False
            if not game["is_winner"] and filters['is_winner'] == "winner":
                return False
                
        # Favorite/Underdog filter
        if filters['is_favorite'] != "all" and game.get("pts_spread"):
            spread = game["pts_spread"]
            if spread < 0 and filters['is_favorite'] == "underdog":
                return False
            if spread > 0 and filters['is_favorite'] == "favorite":
                return False
                
        # Covers filter
        if filters['is_cover'] != "all" and game.get("is_cover") is not None:
            if game["is_cover"] > 0 and filters['is_cover'] == "loser":
                return False
            if game["is_cover"] < 0 and filters['is_cover'] == "cover":
                return False
            

        # Over/Under filter
        if filters['is_over'] != "all" and game.get("is_over"):
            ou = game["is_over"]
            if ou < 0 and filters['is_over'] == "over":
                return False
            if ou > 0 and filters['is_over'] == "under":
                return False
                
        return True
    

    def apply_filters(self, event):
        filterPanel = self.filterFrame.filterPanel
        self.filters = {
            'is_home': filterPanel.hA.GetString(filterPanel.hA.GetSelection()),
            'is_winner': filterPanel.wL.GetString(filterPanel.wL.GetSelection()),
            'is_favorite': filterPanel.fav.GetString(filterPanel.fav.GetSelection()),
            'is_cover': filterPanel.ats.GetString(filterPanel.ats.GetSelection()),
            'is_over': filterPanel.over.GetString(filterPanel.over.GetSelection()),
            "timeframe": filterPanel.timeframe.GetString(filterPanel.timeframe.GetSelection())
        }
               
        filteredIds = []
        for _, game in self.gamelogCtrl.gamelog.iterrows():
            if self._passes_filters(game, self.filters):
                filteredIds.append(game["game_id"])
        
        self.gamelogCtrl.set_selectedIds(filteredIds)


    def clear_selection(self, event):
        return []
    

    def filter_frame_closed(self, event):
        self.filterFrame.Destroy()
        self.filterFrame = None
        self.isDisplayed = False
        self.gamelogCtrl.filter_display_changed()
    
    
    def set_defaults(self):
        self.filters = self._default_filters.copy()


    def select_all(self, event):
        return self.gamelogCtrl.set_selectedIds([game["game_id"] for _, game in self.gamelogCtrl.iterrows()])


    def toggle_filter_frame(self, event):
        if self.gamelogCtrl.gamelog is not None:
            if not self.filterFrame:
                self._new_filter_frame()
            
            if not self.filterFrame.IsShown():
                self.filterFrame.Show()
                self.isDisplayed = True 
            else:
                self.filterFrame.Hide()
                self.isDisplayed = False 
            self.gamelogCtrl.filter_display_changed()


    

       
        
    
    
    

        

    

    

    
        


