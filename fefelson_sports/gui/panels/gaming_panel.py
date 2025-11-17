from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLabel, QDoubleSpinBox, QLineEdit


from ...gui.components.label_components import PctComponent, MoneyComponent
from ...utils.gaming_utils import calculate_kelly_criterion, calculate_moneyline_probs

# for debugging
# from pprint import pprint 


class GamingTitle(QWidget):
    
    _updating = False 
    
    def __init__(self):
        super().__init__()

        self.odds = {}
        self.impPct = {}
        self.espnPct = {}
        self.wager = {}

        self.vig = PctComponent('vig')

        baseFont = QFont("Serif", 15)
        baseFont.setBold(True)

        for a_h in ("away", "home"):

            self.odds[a_h] = QLineEdit()
            self.odds[a_h].setAlignment(Qt.AlignHCenter)
            self.odds[a_h].returnPressed.connect(self.odds_edit)
            self.odds[a_h].setFont(baseFont)
            self.odds[a_h].setFixedWidth(100)

            self.impPct[a_h] = PctComponent("pct")
            self.impPct[a_h].setFont(baseFont)
            self.impPct[a_h].setFixedWidth(100)

            self.espnPct[a_h] = QDoubleSpinBox()
            self.espnPct[a_h].setMinimum(0)
            self.espnPct[a_h].setMaximum(100)
            self.espnPct[a_h].setSingleStep(0.5)
            self.espnPct[a_h].setAlignment(Qt.AlignHCenter)
            self.espnPct[a_h].valueChanged.connect(self.pct_edit)
            self.espnPct[a_h].setFont(baseFont)
            self.espnPct[a_h].setFixedWidth(100)

            self.wager[a_h] = MoneyComponent("WAGER")


        layout = {}
        for a_h in ("away", "home"):
            
            mlLayout = QHBoxLayout()
            if a_h == "away":
                mlLayout.addWidget(self.impPct[a_h])
                mlLayout.addWidget(self.odds[a_h])
            else:
                mlLayout.addWidget(self.odds[a_h])
                mlLayout.addWidget(self.impPct[a_h])

            wagerLayout = QHBoxLayout()
            if a_h == "away":
                wagerLayout.addWidget(self.espnPct[a_h])
                wagerLayout.addWidget(self.wager[a_h])
            else:
                wagerLayout.addWidget(self.wager[a_h])
                wagerLayout.addWidget(self.espnPct[a_h])

            layout[a_h] = QVBoxLayout()
            layout[a_h].addLayout(mlLayout)
            layout[a_h].addLayout(wagerLayout)
            
        mainLayout = QHBoxLayout()
        mainLayout.addLayout(layout["away"], 1)
        mainLayout.addStretch(1)
        mainLayout.addWidget(self.vig, 0, Qt.AlignTop)
        mainLayout.addStretch(1)
        mainLayout.addLayout(layout['home'], 1)

        self.setLayout(mainLayout)


    def pct_edit(self, pct):
        if self._updating:
            return  # Prevent recursion

        self._updating = True
        try:
            # Get the sender (the spin box that triggered the signal)
            sender = self.sender()

            # Update the other spin box
            if sender == self.espnPct['home']:
                self.espnPct['away'].setValue(100-pct)
            elif sender == self.espnPct['away']:
                self.espnPct['home'].setValue(100-pct)
            self._set_bets()
        finally:
            self._updating = False  # Reset flag
        
        


    def odds_edit(self):
        try:
            for a_h in ("away", "home"):
                int(self.odds[a_h].text())
        except ValueError:
            self._set_odds()
        self._set_bets()


    def _set_odds(self):
        odds = self.game["odds"][-1] 
        for a_h in ("away", "home"):
            self.odds[a_h].setText(str(odds[f"{a_h}_ml"]))
        



    def _set_bets(self):

        for a_h in ("away", "home"):
            if self.odds[a_h].text() != '':
                opp = "home" if a_h == "away" else "away"
                mL = int(self.odds[a_h].text())
                try:
                    oppML = int(self.odds[opp].text())
                except ValueError:
                    oppML = int(self.game['odds'][-1][f"{opp}_ml"])

                probs = calculate_moneyline_probs(mL, oppML)
                kelly = calculate_kelly_criterion(self.espnPct[a_h].value()/100, mL, edge=.05)

                self.impPct[a_h].set_panel(probs[0]['implied_prob']*100)
                self.wager[a_h].set_panel(kelly)
                self.vig.set_panel(probs[2]*100)

    def clear(self):
        for a_h in ("away", "home"):
            self.odds[a_h].clear()
            self.impPct[a_h].clear()
            self.espnPct[a_h].clear()
            self.vig.clear()
            self.wager[a_h].clear()


    def set_game(self, game):
        self.clear()
        self.game = game 

        if game["odds"]:
            self._set_odds()

        if game.get('predictor'):
            for a_h in ("away", "home"):
                self.espnPct[a_h].setValue(float(game['predictor'][a_h == 'home'][1]))
                
        self._set_bets()


    


        