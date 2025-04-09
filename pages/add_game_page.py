import os
from datetime import datetime
import subprocess
from PyQt6.QtWidgets import QVBoxLayout, QPushButton, QLabel, QTextEdit, QComboBox, QLineEdit, QMessageBox
from tools import analyser
from pages.page_template import PageTemplate

class AddGamePage(PageTemplate):
    def __init__(self, main_window):
        super().__init__()
        self.team = None
        self.players = []
        self.db_path = None
        self.series = None  # 1: bo1, 2: bo2, 3: bo3
        self.folders = None
        self.game_types = []
        self.dir_path = r"C:\Program Files (x86)\Steam\steamapps\common\Tom Clancy's Rainbow Six Siege\MatchReplay"

        self.main_window = main_window

        # Initialize layout
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(20, 20, 20, 20)

        # Game name input
        self.game_name_label = QLabel("Game Name: ", self)
        self.game_name_label.setStyleSheet("font-size: 16px;")
        self.layout.addWidget(self.game_name_label)

        self.game_name_input = QLineEdit(self)
        self.game_name_input.setPlaceholderText("Enter the name of the game")
        self.game_name_input.setStyleSheet("padding: 10px; font-size: 14px; border: 1px solid #ccc;")
        self.layout.addWidget(self.game_name_input)

        # Game type selection
        self.game_type_label = QLabel("Game Type: ", self)
        self.game_type_label.setStyleSheet("font-size: 16px;")
        self.layout.addWidget(self.game_type_label)

        self.game_type_combobox = QComboBox(self)
        self.game_type_combobox.setEditable(True)
        self.game_type_combobox.setStyleSheet("padding: 10px; font-size: 14px; border: 1px solid #ccc;")
        self.layout.addWidget(self.game_type_combobox)

        # Information display section
        self.info_label = QLabel("Are these the correct games?", self)
        self.layout.addWidget(self.info_label)

        self.games_info_display = QTextEdit(self)
        self.games_info_display.setReadOnly(True)
        self.games_info_display.setStyleSheet("font-size: 14px; padding: 10px; border: 1px solid #ccc;")
        self.layout.addWidget(self.games_info_display)

        # Action buttons
        self.add_games_button = QPushButton("Yes", self)
        self.add_games_button.setStyleSheet("background-color: #4CAF50; color: white; border-radius: 5px; padding: 10px;")
        self.add_games_button.clicked.connect(lambda: self.process_game())
        self.layout.addWidget(self.add_games_button)

        self.add_games_button_no = QPushButton("No", self)
        self.add_games_button_no.setStyleSheet("background-color: #f44336; color: white; border-radius: 5px; padding: 10px;")
        self.add_games_button_no.clicked.connect(lambda: print("to implement"))  # TODO
        self.layout.addWidget(self.add_games_button_no)

        # Go back button
        self.go_back_button = QPushButton("Go back", self)
        self.go_back_button.setStyleSheet("background-color: #9E9E9E; color: white; border-radius: 5px; padding: 10px;")
        self.go_back_button.clicked.connect(main_window.switch_to_view_team_page)
        self.layout.addWidget(self.go_back_button)

        self.setLayout(self.layout)

    def on_activated(self):
        """Fetch team and player data from the main window."""
        self.team, self.players = self.main_window.get_team()

        # Get directories containing game replays
        self.folders = [
            (f, os.path.getmtime(os.path.join(self.dir_path, f)))
            for f in os.listdir(self.dir_path)
            if os.path.isdir(os.path.join(self.dir_path, f))
        ]

        # Get the series type (BO1, BO2, or BO3)
        self.series = self.main_window.get_series()

        # Prepare formatted display of game info
        formatted_games = ""
        for game in reversed(self.folders[-self.series:]):
            last_modified = datetime.fromtimestamp(game[1]).strftime('%Y-%m-%d %H:%M:%S')
            formatted_games += f"Game: {game[0]}, Last Modified: {last_modified}\n"

        # Update display
        self.games_info_display.setText(formatted_games)

        # Fetch game types from the database
        self.game_types = self.main_window.db.get_competition_types()

        # Populate the game type combobox
        self.game_type_combobox.clear()
        for game_type in self.game_types:
            self.game_type_combobox.addItem(game_type)

    def process_game(self):
        """Process the selected game, run the analyser, and insert the game data into the database."""
        game_name = self.game_name_input.text().strip()
        game_type = self.game_type_combobox.currentText()

        if not game_name:
            self.show_message("Error", "Game name cannot be empty", QMessageBox.Icon.Critical)
            return

        if game_type not in self.game_types:
            self.main_window.db.insert_new_competition_type(game_type)

        # Process the selected games
        games_to_process_paths = [os.path.join(self.dir_path, folder[0]) for folder in self.folders[-self.series:]]

        # Insert the new game into the database
        game_id = self.main_window.db.insert_new_game(game_name, game_type, self.series)

        for map_path in games_to_process_paths:
            print(f"Processing folder: {map_path}")

            command = ['./dependencies/r6-dissect', map_path, '-o', 'game.json']

            try:
                result = subprocess.run(command, check=True, capture_output=True, text=True)
                print(f"Command Output: {result.stdout}")
            except subprocess.CalledProcessError as e:
                self.show_message("Error", f"Error while processing map: {e.stderr}", QMessageBox.Icon.Critical)
                return

            game, raw_data = analyser.run()

            teams = game.teams

            # Insert map data into the database
            map_id = self.main_window.db.insert_new_map(game.map_name, game.total_rounds, game.timestamp, game_id)

            # Insert teams and players data into the database
            for team in teams:
                team_id = self.main_window.db.insert_new_team(
                    team.team_name, team.rounds_won, team.rounds_lost, map_id, team.side_started, team.team_id
                )

                # Insert players for the team
                for player in team.players:
                    player_id = self.main_window.db.insert_new_player(
                        player.username, team_id, player.kills, player.deaths, player.headshots, player.kd_percent,
                        player.kd_plus_minus, player.headshot_percentage, player.kpr, player.kost, player.kost_round_count,
                        player.entry_kills, player.entry_deaths, player.entry_diff, player.survival, player.trade_kills,
                        player.trade_deaths, player.trade_diff, player.clutches, player.plants, player.defuses, player.rating
                    )

    def show_message(self, title, message, icon):
        """Show a message box with a title, message, and icon."""
        msg_box = QMessageBox(self)
        msg_box.setIcon(icon)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg_box.exec()
