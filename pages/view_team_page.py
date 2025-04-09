import os
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QDialog, QLabel, QLineEdit, QScrollArea, \
    QDialogButtonBox, QHBoxLayout, QMessageBox
from pages.page_template import PageTemplate

class ViewTeamPage(PageTemplate):
    def __init__(self, main_window):
        super().__init__()
        self.team = None
        self.players = []
        self.db_path = None

        self.main_window = main_window

        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(20, 20, 20, 20)

        self.add_bo1_button = QPushButton("BO1", self)
        self.add_bo1_button.setStyleSheet("background-color: #4CAF50; color: white; border-radius: 5px; padding: 10px;")
        self.add_bo1_button.clicked.connect(lambda: (self.main_window.set_series(1), self.main_window.switch_to_add_game_page()))
        self.layout.addWidget(self.add_bo1_button)

        self.add_bo2_button = QPushButton("BO2", self)
        self.add_bo2_button.setStyleSheet("background-color: #4CAF50; color: white; border-radius: 5px; padding: 10px;")
        self.add_bo2_button.clicked.connect(lambda: (self.main_window.set_series(2), self.main_window.switch_to_add_game_page()))
        self.layout.addWidget(self.add_bo2_button)

        self.add_bo3_button = QPushButton("BO3", self)
        self.add_bo3_button.setStyleSheet("background-color: #4CAF50; color: white; border-radius: 5px; padding: 10px;")
        self.add_bo3_button.clicked.connect(lambda: (self.main_window.set_series(3), self.main_window.switch_to_add_game_page()))
        self.layout.addWidget(self.add_bo3_button)

        self.view_stats_button = QPushButton("View Stats", self)
        self.view_stats_button.setStyleSheet("background-color: #2196F3; color: white; border-radius: 5px; padding: 10px;")
        self.view_stats_button.clicked.connect(lambda: self.main_window.switch_to_view_stats_page())
        self.layout.addWidget(self.view_stats_button)

        self.modify_team_button = QPushButton("Modify Team (WIP)", self)
        self.modify_team_button.setStyleSheet("background-color: #f44336; color: white; border-radius: 5px; padding: 10px;")
        self.modify_team_button.clicked.connect(lambda: print("not working yet"))
        self.layout.addWidget(self.modify_team_button)

        self.go_back_button = QPushButton("Go back", self)
        self.go_back_button.setStyleSheet("background-color: #9E9E9E; color: white; border-radius: 5px; padding: 10px;")
        self.go_back_button.clicked.connect(main_window.switch_to_main_page)
        self.layout.addWidget(self.go_back_button)

        self.setLayout(self.layout)

    def on_activated(self):
        self.team, self.players = self.main_window.get_team()

    def show_modify_team_dialog(self):
        players = self.main_window.db.get_players()
        dialog = ModifyTeamDialog(self, team_name=self.team, players=players)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            team_name = dialog.get_team_name()
            players = dialog.get_players()
            if team_name:
                self.update_team(team_name, players)

    def update_team(self, team_name, players):
        data_directory = './data'

        if not os.path.exists(data_directory):
            os.makedirs(data_directory)

        old_db_path = self.main_window.db.db_path
        new_db_path = os.path.join(data_directory, f"{team_name}.db")

        try:
            os.rename(old_db_path, new_db_path)
            self.main_window.db.set_db_path(new_db_path)
        except OSError as e:
            msg_box = QMessageBox(self)
            msg_box.setIcon(QMessageBox.Icon.Critical)
            msg_box.setWindowTitle("Rename Failed")
            msg_box.setText(f"Failed to rename team database file:\n{e}")
            msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
            msg_box.exec()
            return

        msg_box = QMessageBox(self)
        msg_box.setIcon(QMessageBox.Icon.NoIcon)
        msg_box.setWindowTitle("Success")
        msg_box.setText(f"Team '{team_name}' updated successfully!")
        msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg_box.exec()


class ModifyTeamDialog(QDialog):
    def __init__(self, parent=None, team_name="", players=None):
        super().__init__(parent)

        self.setWindowTitle("Modify Team")

        self.setFixedSize(400, 400)

        if players is None:
            players = []

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.label = QLabel("Enter Team Name:", self)
        self.label.setStyleSheet("font-size: 16px;")
        self.layout.addWidget(self.label)

        self.team_name_input = QLineEdit(self)
        self.team_name_input.setPlaceholderText("Enter team name here")
        self.team_name_input.setText(team_name)
        self.team_name_input.setStyleSheet("padding: 10px; font-size: 14px; border: 1px solid #ccc;")
        self.layout.addWidget(self.team_name_input)

        self.players_label = QLabel("Enter Players and their Aliases:", self)
        self.players_label.setStyleSheet("font-size: 16px;")
        self.layout.addWidget(self.players_label)
        self.players_widget = QWidget(self)
        self.players_layout = QVBoxLayout(self.players_widget)

        self.scroll_area = QScrollArea(self)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setWidget(self.players_widget)
        self.layout.addWidget(self.scroll_area)

        self.add_player_button = QPushButton("Add Player", self)
        self.add_player_button.setStyleSheet("background-color: #008CBA; color: white; border-radius: 5px; padding: 8px;")
        self.add_player_button.clicked.connect(self.add_player_field)
        self.layout.addWidget(self.add_player_button)

        self.buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        self.buttons.setStyleSheet("background-color: #4CAF50; color: white; border-radius: 5px;")
        self.layout.addWidget(self.buttons)

        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)

        for player in players:
            name = player.get('name', '')
            aliases = player.get('aliases', '')
            self.add_player_field(name, aliases)

    def add_player_field(self, name, aliases):
        player_layout = QHBoxLayout()

        player_input = QLineEdit(self)
        player_input.setPlaceholderText("Player Name")
        player_input.setText(name)
        player_input.setStyleSheet("padding: 10px; font-size: 14px; border: 1px solid #ccc;")

        alias_input = QLineEdit(self)
        alias_input.setPlaceholderText("Player Alias (comma separated)")
        alias_input.setText(aliases)
        alias_input.setStyleSheet("padding: 10px; font-size: 14px; border: 1px solid #ccc;")

        player_layout.addWidget(player_input)
        player_layout.addWidget(alias_input)

        self.players_layout.addLayout(player_layout)

    def get_team_name(self):
        return self.team_name_input.text().strip()

    def get_players(self):
        player_data = []
        for i in range(self.players_layout.count()):
            layout = self.players_layout.itemAt(i)
            if layout:
                player_input = layout.itemAt(0).widget()
                alias_input = layout.itemAt(1).widget()
                player_name = player_input.text().strip()
                alias_name = alias_input.text().strip()
                if player_name:
                    player_data.append((player_name, alias_name))

        return player_data