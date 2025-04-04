from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton

from pages.page_template import PageTemplate

class ViewTeamPage(PageTemplate):
    def __init__(self, main_window):
        super().__init__()
        self.team = None
        self.players = []
        self.db_path = None

        self.main_window = main_window

        self.layout = QVBoxLayout()


        add_bo1_button = QPushButton("BO1", self)
        add_bo1_button.clicked.connect(lambda: (self.main_window.set_series(1), self.main_window.switch_to_add_game_page()))
        self.layout.addWidget(add_bo1_button)

        add_bo2_button = QPushButton("BO2", self)
        add_bo2_button.clicked.connect(lambda: (self.main_window.set_series(2), self.main_window.switch_to_add_game_page()))
        self.layout.addWidget(add_bo2_button)

        add_bo3_button = QPushButton("BO3", self)
        add_bo3_button.clicked.connect(lambda: (self.main_window.set_series(3), self.main_window.switch_to_add_game_page()))
        self.layout.addWidget(add_bo3_button)

        btn = QPushButton("Go to Page 1")
        btn.clicked.connect(main_window.switch_to_main_page)

        self.layout.addWidget(btn)
        self.setLayout(self.layout)


    def on_activated(self):
        self.team, self.players = self.main_window.get_team()
        print(self.team, self.players)


