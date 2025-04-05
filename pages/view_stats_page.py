from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton

from pages.page_template import PageTemplate

class ViewStatsPage(PageTemplate):
    def __init__(self, main_window):
        super().__init__()
        self.layout = QVBoxLayout()

        self.main_window = main_window

        btn = QPushButton("Go to Page 1")
        btn.clicked.connect(main_window.switch_to_main_page)

        self.layout.addWidget(btn)
        self.setLayout(self.layout)

    def on_activated(self):
        self.team, self.players = self.main_window.get_team()