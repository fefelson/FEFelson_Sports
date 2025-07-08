import threading
import wx

from ..views.dashboards.teams_compare_view import TeamsCompareView, TeamPanel

from ...models.teams import TeamModel


class CompareTeamsController:
    def __init__(self, frame):
        self.teamModel = TeamModel
        self.view = TeamsCompareView(frame)

        self.view.searchCtrl.Bind(wx.EVT_TEXT, self.on_search)
        self.view.teamList.Bind(wx.EVT_LIST_ITEM_SELECTED, self.on_list_double_click)

        self.view.update_team_list(self.model.get_ncaab_team_names())


    
    def on_list_double_click(self, event):
        print("here")
        """Handle double-click event on list items"""
        newTeamPanel = TeamPanel(self.view.displayPanel)
        team = self.model.get_ncaab_team_by_name()
        self.view.displaySizer.Add(newTeamPanel, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 15)
        self.view.Layout()
        # firstName = self.view.teamList.GetItem(event.GetIndex()).GetText()
        # team = self.model.get_team_by_first_name(firstName)
        
        


    def on_search(self, event):
        query = self.view.searchCtrl.GetValue()
        if query:
            threading.Thread(target=self.search_teams, args=(query,), daemon=True).start()
        else:
            self.view.update_team_list(self.model.get_ncaab_team_names())



    def search_teams(self, query):
        teams = self.model.search_ncaab_teams(query)
        wx.CallAfter(self.view.update_team_list, teams)

    def on_team_select(self, event):
        team = self.view.team_list.GetItemText(event.GetIndex())
        if team not in self.selected_teams:
            self.selected_teams.append(team)
            self.view.add_team_panel(team)
            threading.Thread(target=self.compare_teams, daemon=True).start()

    def compare_teams(self):
        if self.selected_teams:
            teams_data = self.model.compare_teams(self.selected_teams)
            wx.CallAfter(self.view.show_team_data, teams_data)

   