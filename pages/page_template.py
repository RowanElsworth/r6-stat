from PyQt6.QtWidgets import QWidget, QPushButton, QLabel


class PageTemplate(QWidget):
    def create_button(self, text):
        button = QPushButton(text, self)
        button.setStyleSheet("font-size: 14px;")
        self.layout.addWidget(button)

    def create_text(self, text):
        label = QLabel(text, self)
        self.layout.addWidget(label)