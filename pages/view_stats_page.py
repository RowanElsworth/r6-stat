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

        back_btn = self.create_button("← Back to Team Page", self.main_window.switch_to_view_team_page)
        self.layout.addWidget(back_btn)

        self.layout.addWidget(self.create_button("View Global Stats", self.show_global_stats))

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

    def show_global_stats(self):
        map_stats = self.main_window.db.get_map_stats(game_id=None, game_type_id=None, map_id=None)
        player_stats = self.main_window.db.get_player_stats(game_id=None, game_type_id=None, map_id=None)
        dialog = StatsDialog("Game Stats", map_stats, player_stats)
        dialog.exec()


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
                ["Username", "Rating", "K-D(+/-)", "K/D %", "Headshots", "KPR", "KOST", "Entry(+/-)", "Survival",
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