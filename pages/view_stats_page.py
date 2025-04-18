from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QDialog,
    QLabel, QFrame, QSizePolicy, QTableWidgetItem, QTableWidget, QHeaderView
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from pages.page_template import PageTemplate


class ViewStatsPage(PageTemplate):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window

        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(40, 40, 40, 40)
        self.layout.setSpacing(20)

        title = QLabel("Statistics Dashboard")
        title.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(title)

        self.layout.addWidget(self.create_button("View Global Stats", self.view_global_stats)) # All stats, ever - shows maps and players stats
        self.layout.addWidget(self.create_button("View Specific Series Stats", self.view_series_stats)) # All stats from a specific selected series (bo1/bo2/bo3) - shows each individual map and also overall
        self.layout.addWidget(self.create_button("View Specific Game Stats", self.view_game_stats)) # All stats from a specific selected game (1 map, selected from a series)
        self.layout.addWidget(self.create_button("View Specific Game Type Stats", self.view_type_stats)) # All stats from a specific game type (Scrim, etc)
        self.layout.addWidget(self.create_button("View Specific Map Stats", self.view_map_stats)) # All stats from a specific map, shows individual player's performance on that selected map too
        self.layout.addWidget(self.create_button("View Specific Player Stats", self.view_player_stats)) # All stats of a specific player - individual performance tracking

        back_btn = self.create_button("← Back to Team Page", self.main_window.switch_to_view_team_page)
        self.layout.addWidget(back_btn)

        self.setLayout(self.layout)

    def on_activated(self):
        self.team, self.players = self.main_window.get_team()

    def create_button(self, text, slot_func):
        btn = QPushButton(text)
        btn.setStyleSheet("""
            QPushButton {
                padding: 12px;
                font-size: 15px;
                background-color: #2d89ef;
                color: white;
                border-radius: 8px;
            }
            QPushButton:hover {
                background-color: #1e5cb3;
            }
        """)
        btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        btn.clicked.connect(slot_func)
        return btn

    def view_global_stats(self):
        map_stats = self.main_window.db.get_map_stats()
        player_stats = self.main_window.db.get_player_stats()
        dialog = StatsDialog("Game Stats", map_stats, player_stats)
        dialog.exec()

    def view_series_stats(self):
        dialog = SelectorDialog(self.main_window, "Select Series", "series")
        dialog.exec()
        series_id, series_name = dialog.get_selected_id()

        if series_id and series_name:
            map_stats = self.main_window.db.get_map_stats(series_id=series_id)
            player_stats = self.main_window.db.get_player_stats(series_id=series_id)
            dialog = StatsDialog("Game Stats", map_stats, player_stats)
            dialog.exec()
        else:
            print("nothing selected")

    def view_game_stats(self):
        dialog = SelectorDialog(self.main_window, "Select Game", "games")
        dialog.exec()
        game_id, game_name = dialog.get_selected_id()

        if game_id and game_name:
            map_stats = self.main_window.db.get_map_stats(game_id=game_id)
            player_stats = self.main_window.db.get_player_stats(game_id=game_id)
            dialog = StatsDialog("Game Stats", map_stats, player_stats)
            dialog.exec()
        else:
            print("nothing selected")

    def view_type_stats(self):
        dialog = SelectorDialog(self.main_window, "Select Game Type", "game_type")
        dialog.exec()
        game_type_id, game_type_name = dialog.get_selected_id()

        if game_type_id and game_type_name:
            map_stats = self.main_window.db.get_map_stats(game_type_id=game_type_id)
            player_stats = self.main_window.db.get_player_stats(game_type_id=game_type_id)
            dialog = StatsDialog("Game Stats", map_stats, player_stats)
            dialog.exec()
        else:
            print("nothing selected")

    def view_map_stats(self):
        dialog = SelectorDialog(self.main_window, "Select Map", "map")
        dialog.exec()
        map_id, map_name = dialog.get_selected_id()

        if map_id and map_name:
            map_stats = self.main_window.db.get_map_stats(map_name=map_name)
            player_stats = self.main_window.db.get_player_stats(map_name=map_name)
            dialog = StatsDialog("Game Stats", map_stats, player_stats)
            dialog.exec()
        else:
            print("nothing selected")

    def view_player_stats(self):
        dialog = SelectorDialog(self.main_window, "Select Player", "team_players")
        dialog.exec()
        player_id, player_name = dialog.get_selected_id()

        if player_id and player_name:
            map_stats = self.main_window.db.get_map_stats(player_name=player_name)
            player_stats = self.main_window.db.get_player_stats(player_name=player_name)
            dialog = StatsDialog("Game Stats", map_stats, player_stats)
            dialog.exec()
        else:
            print("nothing selected")


class StatsDialog(QDialog):
    def __init__(self, title: str, stats_data: list, player_data: list = None):
        super().__init__()
        self.setWindowTitle(title)
        self.setMinimumWidth(1400)

        layout = QVBoxLayout()

        self.table_map = self.create_table(
            ["Map Name", "Played", "Won", "Map Win %", "Rounds Played", "Rounds Won", "Round Win %", "% Playtime"],
            stats_data
        )
        layout.addWidget(QLabel("<b>Map Statistics</b>"))
        layout.addWidget(self.table_map)

        if player_data:
            self.table_player = self.create_table(
                ["Username", "Rating", "K-D(+/-)", "K/D", "Headshots", "KPR", "KOST", "Entry(+/-)", "Survival",
                 "Trades(+/-)", "Clutches", "Plants", "Defuses"],
                player_data,
                is_player_data=True
            )
            layout.addWidget(QLabel("<b>Player Statistics</b>"))
            layout.addWidget(self.table_player)

        close_button = QPushButton("Close")
        close_button.setStyleSheet("background-color: #4CAF50; color: white; padding: 5px 10px; border-radius: 5px;")
        close_button.clicked.connect(self.accept)
        layout.addWidget(close_button, alignment=Qt.AlignmentFlag.AlignCenter)

        self.setLayout(layout)

    def create_table(self, headers: list, data: list, is_player_data: bool = False) -> QTableWidget:
        table = QTableWidget()
        table.setColumnCount(len(headers))
        table.setHorizontalHeaderLabels(headers)
        table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)

        table.setStyleSheet("""
            QTableWidget {
                border: 1px solid #ccc;
                border-radius: 5px;
                font-size: 12px;
                background-color: #f9f9f9;
                color: #333;
            }
            QHeaderView::section {
                background-color: #f2f2f2;
                padding: 5px;
                border: 1px solid #ddd;
                font-weight: bold;
            }
            QTableWidget::item {
                padding: 5px;
            }
        """)

        formatted_data = []
        for item in data:
            if is_player_data:
                formatted_data.append(self.format_player_data(item))
            else:
                formatted_data.append(self.format_map_data(item))

        table.setRowCount(len(formatted_data))
        for row_idx, row in enumerate(formatted_data):
            for col_idx, value in enumerate(row):
                table.setItem(row_idx, col_idx, QTableWidgetItem(str(value)))

        table.horizontalHeader().setStretchLastSection(True)
        table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        return table

    def format_map_data(self, map: list) -> list:
        return [
            map[0],
            map[1],
            map[2],
            f"{map[3]:.0f}%",
            map[4],
            map[5],
            f"{map[6]:.0f}%",
            f"{map[7]:.0f}%"
        ]

    def format_player_data(self, player: list) -> list:
        kd_plus_minus = int(player[4])
        entry_diff = int(player[11])
        trade_diff = int(player[15])
        return [
            player[0],
            f"{player[1]:.2f}",
            f"{player[2]}-{player[3]}({f'+{kd_plus_minus}' if kd_plus_minus >= 0 else kd_plus_minus})",
            f"{player[5]:.2f}",
            f"{player[6] * 100:.0f}%",
            f"{player[7]:.2f}",
            f"{player[8] * 100:.0f}%",
            f"{player[9]}-{player[10]}({f'+{entry_diff}' if entry_diff >= 0 else entry_diff})",
            f"{player[12] * 100:.0f}%",
            f"{player[13]}-{player[14]}({f'+{trade_diff}' if trade_diff >= 0 else trade_diff})",
            player[16],
            player[17],
            player[18]
        ]


class SelectorDialog(QDialog):
    def __init__(self, main_window, title, table_name):
        super().__init__()

        self.selected_id = None
        self.selected_name = None

        self.main_window = main_window
        self.setWindowTitle(title)
        self.setMinimumWidth(800)

        layout = QVBoxLayout()
        self.table = QTableWidget()
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)

        self.data, headers = self.fetch_data(table_name)
        self.populate_table(self.data, headers)

        layout.addWidget(self.table)

        close_button = QPushButton("Confirm")
        close_button.setStyleSheet("background-color: #4CAF50; color: white; padding: 5px 10px; border-radius: 5px;")
        close_button.clicked.connect(self.accept)
        layout.addWidget(close_button, alignment=Qt.AlignmentFlag.AlignCenter)

        self.setLayout(layout)

    def fetch_data(self, table_name):
        data = []
        headers = []

        if table_name == "series":
            data = self.main_window.db.get_series()
            headers = ["Series Name", "Game Type", "Map Count", "Timestamp"]
        elif table_name == "games":
            data = self.main_window.db.get_games()
            headers = ["Map Name", "Total Rounds", "Timestamp", "Game Name", "Game Type"]
        elif table_name == "game_type":
            data = self.main_window.db.get_competition_types()
            headers = ["Game Type"]
        elif table_name == "map":
            data = self.main_window.db.get_distinct_map_names()
            data = [(name, name) for name in data]
            headers = ["Map Name"]
        elif table_name == "team_players":
            data = self.main_window.db.get_players()
            headers = ["Player Name"]
            data = [(player['id'], player['name']) for player in data]

        return data, headers

    def populate_table(self, data, headers):
        if data:
            self.table.setColumnCount(len(headers))
            self.table.setHorizontalHeaderLabels(headers)
            self.table.setRowCount(len(data))

            for row_idx, row in enumerate(data):
                for col_idx, value in enumerate(row[1:]):
                    self.table.setItem(row_idx, col_idx, QTableWidgetItem(str(value)))

            self.table.horizontalHeader().setStretchLastSection(True)
            self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

    def accept(self):
        selected_row = self.table.selectionModel().selectedRows()
        if selected_row:
            selected_row_idx = selected_row[0].row()

            selected_data = self.data[selected_row_idx]
            self.selected_id = selected_data[0]
            self.selected_name = selected_data[1]

        super().accept()

    def get_selected_id(self):
        return self.selected_id, self.selected_name
