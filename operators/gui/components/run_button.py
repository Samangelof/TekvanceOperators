from PySide6.QtWidgets import QPushButton

class RunButton(QPushButton):
    def __init__(self, label="▶ Запуск", parent=None):
        super().__init__(label, parent)
        self.setFixedHeight(40)
        self.setStyleSheet("font-weight: bold; font-size: 14px;")
