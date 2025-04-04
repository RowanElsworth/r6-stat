from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel

from pages.page_template import PageTemplate

class AddGamesPage(PageTemplate):
    def __init__(self, main_window):
        super().__init__()
        self.team = None
        self.players = []

        self.layout = QVBoxLayout()

        label = QLabel("Add Games", self)
        self.layout.addWidget(label)

        add_games_button = QPushButton("Add Games", self)
        add_games_button.clicked.connect(lambda: ())
        self.layout.addWidget(add_games_button)

        self.main_window = main_window

        btn = QPushButton("Go to Page 1")
        btn.clicked.connect(main_window.switch_to_main_page)

        self.layout.addWidget(btn)
        self.setLayout(self.layout)



    def on_activated(self):
        self.team, self.players = self.main_window.get_team()
        print(self.team, self.players)