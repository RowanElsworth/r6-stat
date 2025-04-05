import sys
from PyQt6.QtWidgets import QApplication, QStackedWidget, QMainWindow

from tools.db_helper import DBHelper
from pages.add_game_page import AddGamePage
from pages.select_team_page import MainPage
from pages.view_stats_page import ViewStatsPage
from pages.view_team_page import ViewTeamPage


class MyApp(QMainWindow):
    def __init__(self):
        super().__init__()

        # Global vars
        self.team = None
        self.players = []

        self.db = DBHelper()

        self.series_selector = None

        # Set up the window
        self.setWindowTitle('SQLite Database Player Fetcher')
        self.setGeometry(100, 100, 600, 400)

        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        # Pages
        self.main_page = MainPage(self)
        self.view_team_page = ViewTeamPage(self)
        self.add_game_page = AddGamePage(self)
        self.view_stats_page = ViewStatsPage(self)

        self.stack.addWidget(self.main_page)
        self.stack.addWidget(self.view_team_page)
        self.stack.addWidget(self.add_game_page)
        self.stack.addWidget(self.view_stats_page)

        self.stack.setCurrentWidget(self.main_page)

        self.stack.currentChanged.connect(self.on_page_switch)

    def switch_to_main_page(self):
        self.stack.setCurrentWidget(self.main_page)

    def switch_to_view_team_page(self):
        self.stack.setCurrentWidget(self.view_team_page)

    def switch_to_add_game_page(self):
        self.stack.setCurrentWidget(self.add_game_page)

    def switch_to_view_stats_page(self):
        self.stack.setCurrentWidget(self.view_stats_page)

    def on_page_switch(self, index):
        current_page = self.stack.widget(index)

        if isinstance(current_page, MainPage):
            current_page.on_activated()
        elif isinstance(current_page, ViewTeamPage):
            current_page.on_activated()
        elif isinstance(current_page, AddGamePage):
            current_page.on_activated()
        elif isinstance(current_page, ViewStatsPage):
            current_page.on_activated()


    def set_team(self, team_name, players):
        self.team = team_name
        self.players = players

    def get_team(self):
        return self.team, self.players

    def set_series(self, num):
        self.series_selector = num

    def get_series(self):
        return self.series_selector

if __name__ == "__main__":
    import traceback

    try:
        app = QApplication(sys.argv)
        window = MyApp()
        window.show()
        sys.exit(app.exec())
    except Exception as e:
        print("Unhandled Exception:", e)
        traceback.print_exc()