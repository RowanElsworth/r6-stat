import os

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel, QDialog, QInputDialog, QDialogButtonBox, \
    QLineEdit, QMessageBox, QHBoxLayout, QScrollArea

from pages.page_template import PageTemplate

class MainPage(PageTemplate):
    def __init__(self, main_window):
        super().__init__()
        self.layout = QVBoxLayout()

        self.team_buttons_layout = QVBoxLayout()
        self.layout.addLayout(self.team_buttons_layout)

        self.add_team_button = QPushButton("Add New Team", self)
        self.add_team_button.clicked.connect(self.show_add_team_dialog)

        self.layout.addWidget(self.add_team_button)

        self.main_window = main_window
        self.setLayout(self.layout)

        self.fetch_players()

    def on_activated(self):
        self.team, self.players = self.main_window.get_team()

    def fetch_players(self):
        data_directory = './data'

        if not os.path.isdir(data_directory):
            self.create_text("Directory not found: ./data")
            return

        teams_data = []

        for i in reversed(range(self.team_buttons_layout.count())):
            widget = self.team_buttons_layout.itemAt(i).widget()
            if widget is not None:
                widget.deleteLater()

        for filename in os.listdir(data_directory):
            if filename.endswith(".db"):
                db_path = os.path.join(data_directory, filename)
                team_name = filename.replace(".db", "")
                self.main_window.db.set_db_path(db_path)
                players = self.main_window.db.get_players()
                players = [player['name'] for player in players]
                if players:
                    teams_data.append((team_name, players, db_path))

        if teams_data:
            for team_name, players, db_path in teams_data:
                team_button_text = f"{team_name}\n{', '.join(players)}"
                button = QPushButton(team_button_text, self)
                button.clicked.connect(
                    lambda _, tn=team_name, pl=players, dp=db_path: (
                        self.main_window.set_team(tn, pl),
                        self.main_window.db.set_db_path(dp),
                        self.main_window.switch_to_view_team_page()
                    )
                )
                self.team_buttons_layout.addWidget(button)
        else:
            self.create_text("No players found in any database.")

    def show_add_team_dialog(self):
        dialog = AddTeamDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            team_name = dialog.get_team_name()
            players = dialog.get_players()
            if team_name:
                self.add_team(team_name, players)

    def add_team(self, team_name, players):
        data_directory = './data'

        if not os.path.exists(data_directory):
            os.makedirs(data_directory)

        new_db_path = os.path.join(data_directory, f"{team_name}.db")

        if os.path.exists(new_db_path):
            msg_box = QMessageBox(self)
            msg_box.setIcon(QMessageBox.Icon.Warning)
            msg_box.setWindowTitle("Team Exists")
            msg_box.setText(f"Team '{team_name}' already exists.")
            msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
            msg_box.exec()
        else:
            self.create_new_team_db(new_db_path, players)
            msg_box = QMessageBox(self)
            msg_box.setIcon(QMessageBox.Icon.NoIcon)
            msg_box.setWindowTitle("Success")
            msg_box.setText(f"Team '{team_name}' added successfully!")
            msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
            msg_box.exec()
            self.fetch_players()

    def create_new_team_db(self, db_path, players):
        self.main_window.db.create_new_table(db_path, players)


class AddTeamDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add New Team")

        self.setFixedSize(400, 400)

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.label = QLabel("Enter Team Name:", self)
        self.layout.addWidget(self.label)

        self.team_name_input = QLineEdit(self)
        self.team_name_input.setPlaceholderText("Enter team name here")
        self.layout.addWidget(self.team_name_input)

        self.players_label = QLabel("Enter Players and their Aliases:", self)
        self.layout.addWidget(self.players_label)
        self.players_widget = QWidget(self)
        self.players_layout = QVBoxLayout(self.players_widget)

        self.scroll_area = QScrollArea(self)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setWidget(self.players_widget)
        self.layout.addWidget(self.scroll_area)

        self.add_player_button = QPushButton("Add Player", self)
        self.add_player_button.clicked.connect(self.add_player_field)
        self.layout.addWidget(self.add_player_button)

        self.buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        self.layout.addWidget(self.buttons)

        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)

        self.players = []

    def add_player_field(self):
        player_layout = QHBoxLayout()

        player_input = QLineEdit(self)
        player_input.setPlaceholderText("Player Name")
        alias_input = QLineEdit(self)
        alias_input.setPlaceholderText("Player Alias (comma separated)")

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