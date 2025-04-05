import os
import sqlite3
from datetime import datetime
import subprocess

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel, QTextEdit, QComboBox, QLineEdit

import analyser
from pages.page_template import PageTemplate

class AddGamePage(PageTemplate):
    def __init__(self, main_window):
        super().__init__()
        self.team = None
        self.players = []
        self.db_path = None
        self.series = None # 1: bo1, 2: bo2, 3: bo3
        self.folders = None
        self.game_types = []
        self.dir_path = r"C:\Program Files (x86)\Steam\steamapps\common\Tom Clancy's Rainbow Six Siege\MatchReplay"

        self.main_window = main_window

        self.layout = QVBoxLayout()

        # name of game
        self.game_name_label = QLabel("Game Name: ", self)
        self.layout.addWidget(self.game_name_label)

        self.game_name_input = QLineEdit(self)
        self.game_name_input.setPlaceholderText("Enter the name of the game")
        self.layout.addWidget(self.game_name_input)

        # type of game
        self.game_type_label = QLabel("Game Type: ", self)
        self.layout.addWidget(self.game_type_label)

        self.game_type_combobox = QComboBox(self)
        self.game_type_combobox.setEditable(True)
        self.layout.addWidget(self.game_type_combobox)

        label = QLabel("Are these the correct games?", self)
        self.layout.addWidget(label)

        self.games_info_display = QTextEdit(self)
        self.games_info_display.setReadOnly(True)
        self.layout.addWidget(self.games_info_display)

        add_games_button = QPushButton("Yes", self)
        add_games_button.clicked.connect(lambda: (self.process_game()))
        self.layout.addWidget(add_games_button)

        add_games_button = QPushButton("No", self)
        add_games_button.clicked.connect(lambda: (print("to implement"))) # TODO:
        self.layout.addWidget(add_games_button)

        btn = QPushButton("Go back")
        btn.clicked.connect(main_window.switch_to_view_team_page)
        self.layout.addWidget(btn)

        self.setLayout(self.layout)


    def on_activated(self):
        self.team, self.players = self.main_window.get_team()

        self.folders = [
            (f, os.path.getmtime(os.path.join(self.dir_path, f)))
            for f in os.listdir(self.dir_path)
            if os.path.isdir(os.path.join(self.dir_path, f))
        ]

        self.series = self.main_window.get_series()

        formatted_games = ""
        for game in reversed(self.folders[-self.series:]):
            last_modified = datetime.fromtimestamp(game[1]).strftime('%Y-%m-%d %H:%M:%S')
            formatted_games += f"Game: {game[0]}, Last Modified: {last_modified}\n"

        self.games_info_display.setText(formatted_games)
        
        self.game_types = self.main_window.db.get_competition_types()

        self.game_type_combobox.clear()

        for game_type in self.game_types:
            self.game_type_combobox.addItem(game_type)

    def process_game(self):
        game_name = self.game_name_input.text().strip()
        game_type = self.game_type_combobox.currentText()

        if not game_name:
            print("game name cannot be empty")
            return

        if game_type not in self.game_types:
            self.main_window.db.insert_new_competition_type(game_type)
            
        # Process games and add to db
        games_to_process_paths = [os.path.join(self.dir_path, folder[0]) for folder in self.folders[-self.series:]]

        print(games_to_process_paths)

        # insert game
        game_id = self.main_window.db.insert_new_game(game_name, game_type, self.series)

        for map_path in games_to_process_paths:
            print(f"Processing folder: {map_path}")

            command = ['./dependencies/r6-dissect', map_path, '-o', 'game.json']

            try:
                result = subprocess.run(command, check=True, capture_output=True, text=True)
                print(f"Command Output: {result.stdout}")
            except subprocess.CalledProcessError as e:
                print(f"Error: {e.stderr}")

            game, raw_data = analyser.run()

            teams = game.teams

            # insert map
            map_id = self.main_window.db.insert_new_map(game.map_name, game.total_rounds, game.timestamp, game_id)

            # insert teams
            for team in teams:
                team_id = self.main_window.db.insert_new_team(team.team_name, team.rounds_won, team.rounds_lost, map_id, team.team_id)

                # insert players
                for player in team.players:
                    player_id = self.main_window.db.insert_new_player(
                        player.username, team_id, player.kills, player.deaths, player.headshots, player.kd_percent,
                        player.kd_plus_minus, player.headshot_percentage, player.kpr, player.kost, player.kost_round_count,
                        player.entry_kills, player.entry_deaths, player.entry_diff, player.survival, player.trade_kills,
                        player.trade_deaths, player.trade_diff, player.clutches, player.plants, player.defuses, player.rating
                    )

        print("should be complete :)")
        
        



